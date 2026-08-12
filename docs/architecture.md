
# Software architecture

The controller is split at the places most likely to change: servo hardware,
leg calibration, gait generation, and the external command source.

```text
CLI today / ROS 2 node later
            |
            v
SpiderController             whole-body lifecycle and synchronized frames
            |
            +---- AlternatingTetrapodGait(MotionCommand)
            |       x = forward, y = left, yaw = counter-clockwise
            |
            v
Leg x 8                      calibrated coxa/femur/tibia targets and limits
            |
            v
ServoBus interface           stage, start, stop, read, power, close
       /             \
LewanSoulBus          SimulationBus
       |
existing lewansoul_servo_bus.py and pyserial
```

## Responsibilities

### Hardware layer

`spider_robot.hardware.ServoBus` is the small contract seen by the rest of the
application. `LewanSoulBus` adapts the existing
`tools/hiwonderbuslinker/lewansoul_servo_bus.py` implementation. It stages all
joint targets and starts them with broadcast ID 254, so one body frame begins
as nearly simultaneously as the servo protocol permits.

`SimulationBus` records the same frames in memory. It makes development and
automated tests possible without opening a serial port.

### Leg layer

Each `Leg` owns one coxa, femur, and tibia configuration. Higher layers provide
logical offsets from neutral; the leg applies direction, checks the calibrated
limits, and converts the result to absolute servo ticks. A complete body frame
is validated before its first serial command is sent.

### Gait layer

`AlternatingTetrapodGait` divides the eight legs into two stable groups. One
group swings while the other remains in stance. Mounting angles project a body
velocity request onto each coxa joint, allowing forward/backward, left/right,
turning, and blended movement.

This is a joint-space gait, not inverse kinematics. It is an intentional first
step because the old project contains useful servo positions but no measured
link lengths or coordinate calibration. When those measurements are available,
add a Cartesian gait/IK implementation that produces `LegPose` objects; the leg,
hardware, CLI, and future ROS layers do not need to change.

### Body layer

`SpiderController` owns all legs, applies stand/sit poses, executes gait cycles,
reads positions, and performs broadcast stops. Application code should depend
on this class instead of individual servo IDs.

## Configuration

`config/spider.toml` is the single source of hardware-specific data:

- serial settings and broadcast ID;
- gait timing, lift height, stance, and sitting offsets;
- the dead/storage pose, transition timing, and optional per-leg overrides;
- leg names, mounting angles, and alternating gait groups;
- joint servo IDs, neutral ticks, safe limits, and direction signs.

The default ID layout was recovered from the bachelor code. The physical leg
names and mount angles are an explicit assumption and must be checked on the
actual robot before floor testing.

## ROS 2 integration path

A future ROS 2 package only needs a thin node above `SpiderController`:

1. Subscribe to `geometry_msgs/msg/Twist` on `/cmd_vel`.
2. Map `linear.x`, `linear.y`, and `angular.z` to `MotionCommand`.
3. Advance the gait from a timer or dedicated control thread; do not block the
   ROS executor with `time.sleep`.
4. Publish measured joint states from `read_positions()`.
5. Call `stop()` on timeout, node shutdown, or an emergency-stop input.

For smooth teleoperation, the next controller iteration should expose a
non-blocking `tick(command, now)` API. The present blocking `walk()` method is
kept simple and safe for calibration and command-line operation.
