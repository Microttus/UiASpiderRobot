# Initial setup and calibration

Do the first movements with the chassis supported so the feet cannot load the
servos. Keep a physical way to disconnect servo power within reach.

## 1. Install

Python 3.11 or newer is required.

```sh
./setup/install.sh
. .venv/bin/activate
```

The installer creates `.venv` and installs this repository in editable mode,
including `pyserial` and the `spider-robot` command.

On Linux, add your user to the serial-port group and log in again:

```sh
sudo usermod -aG dialout "$USER"
```

The default device is `/dev/ttyACM0`. Change `[bus].port` in
`config/spider.toml` or pass `--port` to a command.

## 2. Verify the bus and IDs

The original project assigns consecutive IDs 1-24, three per leg. To change an
ID, power down, connect exactly one servo, then run:

```sh
python setup/set_servo_id.py --old-id 1 --new-id 5 --yes
```

This example changes ID 1 to ID 5; substitute the current and desired IDs.

Repeat with the correct old and new IDs. Connecting multiple servos while
changing a shared ID can reprogram all of them.

With the full bus connected, perform the read-only check:

```sh
python setup/check_servos.py
```

Do not proceed until every configured ID responds exactly once.

## 3. Confirm configuration assumptions

The default file assumes IDs 1-12 are the left legs from front to rear and
13-24 are the right legs from front to rear. For each `[[legs]]` entry, confirm:

- the three IDs control its coxa, femur, and tibia joints;
- increasing a logical coxa offset moves in the expected angular direction;
- the neutral tick does not push a linkage against a mechanical stop;
- `minimum` and `maximum` are conservative physical limits.

If a joint moves opposite to the logical direction, change its `direction`
between `1` and `-1`; do not compensate in gait code. Adjust `neutral` to level
the robot. The configured limits are software guards and must be tightened for
the actual mechanism.

## 4. Test progressively

First verify the code path without hardware:

```sh
spider-robot --simulate stand
spider-robot --simulate walk forward --cycles 1
```

Then support the robot above the floor and run one real pose at a slow pace:

```sh
spider-robot stand --duration 3
spider-robot positions
spider-robot sit --duration 3
```

Only after every pose is correct should you try one gait cycle:

```sh
spider-robot walk forward --cycles 1 --strength 0.3
```

Increase strength gradually. Tune `phase_duration`, `sweep_ticks`, lift offsets,
and individual `sweep_scale` values in `config/spider.toml`.

## Emergency behavior

Ctrl-C broadcasts a stop before closing the serial port. A separate terminal
can also run `spider-robot stop`, but software stop is not a substitute for a
physical power disconnect.
