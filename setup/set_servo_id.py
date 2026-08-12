"""Assign one servo ID. Connect exactly one servo before running this tool."""

from __future__ import annotations

import argparse
from pathlib import Path
import time

from spider_robot.config import load_config


DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "spider.toml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-id", required=True, type=int)
    parser.add_argument("--new-id", required=True, type=int)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--port", help="override the port in the config")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="confirm that only the target servo is connected",
    )
    args = parser.parse_args()

    if not args.yes:
        parser.error("connect exactly one servo, then repeat with --yes")
    if not 0 <= args.old_id <= 253 or not 0 <= args.new_id <= 253:
        parser.error("servo IDs must be between 0 and 253")

    config = load_config(args.config)
    port = args.port or config.bus.port
    from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication

    bus = ServoBusCommunication(
        port=port,
        baudrate=config.bus.baudrate,
        timeout=config.bus.timeout,
        discard_echo=config.bus.discard_echo,
        on_exit_power_off=False,
    )
    try:
        print(f"Changing the only connected servo: {args.old_id} -> {args.new_id}")
        bus.id_write(args.old_id, args.new_id)
        time.sleep(0.2)
        position = bus.pos_read(args.new_id)
        print(f"Servo {args.new_id} responded at position {position:.0f}")
    finally:
        bus.serial_conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
