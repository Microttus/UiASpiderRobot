# Dead/storage pose and fine-tuning

The dead pose folds the legs underneath the chassis to reduce the robot's
storage footprint. Run it with either equivalent command:

```sh
spider-robot dead
spider-robot storage
```

The controller uses two synchronized frames:

1. All legs move to the existing sitting pose over `approach_duration`.
2. All legs move to the configured dead-pose offsets over `duration`.

Passing through the sitting pose avoids curling directly from an unknown point
in a gait. The command does **not** unload the servos or disconnect power. Once
the final pose has settled and the robot is physically supported, disconnect
servo power using the robot's normal hardware procedure.

## Configuration values

The defaults are in `config/spider.toml`:

```toml
[dead_pose]
approach_duration = 2.0
duration = 3.0
coxa_offset = 0.0
femur_offset = -250.0
tibia_offset = -330.0
```

These are logical offsets in servo ticks, not absolute positions and not
degrees. Each absolute target is calculated as:

```text
target ticks = joint neutral + joint direction * pose offset
```

For a joint with `neutral = 500` and `direction = 1`, a femur offset of `-250`
therefore targets tick 250. A Hiwonder servo's nominal 0-1000 tick range spans
about 240 degrees, so one tick is approximately 0.24 degrees. Linkage geometry
means a servo-angle change is not the same as the foot's angle or displacement.

The supplied values are initial placeholders inferred from the old sitting
pose. They have not been physically verified on this robot.

## Preview final targets

Use the simulation bus to resolve calibration, joint directions, and offsets
without opening the serial port:

```sh
spider-robot --simulate --show-targets dead
```

The result lists the final absolute coxa, femur, and tibia tick for every leg.
Every target must remain inside that joint's `minimum` and `maximum` values.
Configuration loading fails with the leg and servo ID if a target is outside
its configured limits.

## Fine-tuning procedure

1. Support the chassis above the work surface and keep power disconnect within
   reach.
2. Confirm `sit --duration 3` is safe before testing the tighter dead pose.
3. Preview targets with `--simulate --show-targets`.
4. Adjust offsets by only 5-10 ticks at a time.
5. Run `dead` with slower timing for the first physical tests:

   ```sh
   spider-robot dead --approach-duration 4 --duration 5
   ```

6. Check every linkage for collision, cable tension, servo buzzing, or contact
   with a mechanical stop. Disconnect power immediately if any occurs.
7. Tighten each joint's software `minimum` and `maximum` after finding its safe
   physical range.

Start with the tibia offset to fold the outer segment, then adjust the femur.
Tune coxa last because it changes sideways clearance between neighboring legs.

## Per-leg overrides

If one leg needs different clearance, add a table named after that configured
leg. Omitted fields inherit the common `[dead_pose]` values:

```toml
[dead_pose.legs.front_left]
coxa_offset = 10.0
tibia_offset = -320.0
```

For example, this keeps the common femur offset but changes the front-left coxa
and tibia. Leg names must exactly match the `name` values in each `[[legs]]`
entry. Unknown names are rejected when configuration loads.

## Programmatic use

```python
controller.dead()

# Temporary timing overrides; configured joint offsets are still used.
controller.dead(approach_duration=4.0, duration=5.0)
```

The `wait=False` option returns after the final curl is broadcast, but the
sitting approach always completes first so the storage transition remains
ordered.
