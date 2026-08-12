# Motion commands and gait tuning

## Coordinate convention

`MotionCommand` follows the planar part of the ROS 2 `Twist` convention:

| Field | Positive direction | Normalized range |
|---|---|---:|
| `linear_x` | forward | -1 to 1 |
| `linear_y` | left | -1 to 1 |
| `angular_z` | counter-clockwise / left turn | -1 to 1 |

Values can be blended. For example, this walks forward-left while turning
slightly right:

```sh
spider-robot move --x 0.8 --y 0.3 --yaw -0.15 --cycles 2
```

Named commands are shortcuts:

```sh
spider-robot walk forward
spider-robot walk backward
spider-robot walk left
spider-robot walk right
spider-robot walk turn-left
spider-robot walk turn-right
```

## One gait cycle

The legs alternate between gait groups 0 and 1:

| Phase | Group 0 | Group 1 |
|---:|---|---|
| 1 | lift and swing forward | stance moves rearward |
| 2 | lower at front | remains in stance |
| 3 | stance moves rearward | lift and swing forward |
| 4 | remains in stance | lower at front |

All 24 servo targets are prepared with `move_time_wait_write`, then started by
one broadcast `move_start`. This avoids the leg-by-leg timing skew present in
independent immediate writes.

## Tuning order

1. Joint IDs, neutral ticks, directions, and safe limits.
2. Standing and sitting femur/tibia offsets.
3. Lift offsets, with the robot supported.
4. `sweep_ticks` at low `--strength`.
5. Individual `sweep_scale` and mounting angles.
6. `phase_duration` after the geometry is reliable.

Direction strength scales stride size. `phase_duration` controls phase timing;
larger values move more slowly. Configuration validation rejects duplicate IDs,
invalid directions, and out-of-limit generated targets before transmitting the
affected frame.
