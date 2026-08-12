"""Read every configured servo without moving the robot."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from spider_robot.config import load_config
from spider_robot.hardware import LewanSoulBus


DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "spider.toml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--port", help="override the port in the config")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.port:
        config = replace(config, bus=replace(config.bus, port=args.port))

    failures = 0
    checked = 0
    with LewanSoulBus(config.bus) as bus:
        for leg in config.legs:
            for joint_name in ("coxa", "femur", "tibia"):
                checked += 1
                joint = getattr(leg, joint_name)
                try:
                    position = bus.read_position(joint.servo_id)
                    print(
                        f"OK   id={joint.servo_id:3} "
                        f"{leg.name}.{joint_name:6} position={position:.0f}"
                    )
                except Exception as error:
                    failures += 1
                    print(
                        f"FAIL id={joint.servo_id:3} "
                        f"{leg.name}.{joint_name:6} {error}"
                    )

    print(f"Checked {checked} configured joints; {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
