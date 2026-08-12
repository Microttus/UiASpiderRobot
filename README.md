# UiA Spider-Robot

Layered Python control software for the eight-legged bachelor-project robot.
It keeps the existing LewanSoul serial driver, but separates hardware access,
leg calibration, gait generation, and whole-body commands.

## Quick start without hardware

```sh
./setup/install.sh
. .venv/bin/activate
spider-robot --simulate walk forward --cycles 1
spider-robot --simulate move --x 0.7 --y 0.3 --yaw 0.2 --cycles 2
```

## Robot commands

After completing the safety and calibration steps in [docs/setup.md](docs/setup.md):

```sh
spider-robot stand
spider-robot walk forward --cycles 2
spider-robot walk left --cycles 2
spider-robot walk turn-right --cycles 2
spider-robot move --x 0.8 --y 0.2 --yaw -0.1 --cycles 2
spider-robot sit
spider-robot stop
```

`--cycles 0` walks until Ctrl-C. Use `--port /dev/ttyUSB0` to override the
configured port.

## Documentation

- [Architecture and ROS 2 path](docs/architecture.md)
- [Installation, wiring, and calibration](docs/setup.md)
- [Motion model and command reference](docs/motion.md)
- [Initial setup tools](setup/README.md)

The original showcase programs remain in `src/bachelor/` as reference material;
new development should use the `spider_robot` package.
