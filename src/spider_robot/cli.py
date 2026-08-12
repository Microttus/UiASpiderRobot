"""Command-line entry point for operating or simulating the robot."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import time

from .config import load_config
from .controller import MotionCommand, SpiderController
from .hardware import LewanSoulBus, SimulationBus


DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "spider.toml"

DIRECTIONS = {
    "forward": MotionCommand(linear_x=1.0),
    "backward": MotionCommand(linear_x=-1.0),
    "left": MotionCommand(linear_y=1.0),
    "right": MotionCommand(linear_y=-1.0),
    "turn-left": MotionCommand(angular_z=1.0),
    "turn-right": MotionCommand(angular_z=-1.0),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spider-robot", description="Control the UiA spider robot"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--port", help="override the serial port from the config")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="run without serial hardware and print a command summary",
    )
    parser.add_argument(
        "--show-targets",
        action="store_true",
        help="print final joint targets after a simulated command",
    )

    actions = parser.add_subparsers(dest="action", required=True)
    stand = actions.add_parser("stand", help="move all legs to the standing pose")
    stand.add_argument("--duration", type=float, default=1.0)
    sit = actions.add_parser("sit", help="move all legs to the sitting pose")
    sit.add_argument("--duration", type=float, default=1.5)
    dead = actions.add_parser(
        "dead",
        aliases=["storage"],
        help="curl the legs underneath the body for storage",
    )
    dead.add_argument(
        "--duration",
        type=float,
        help="override the configured final curl duration",
    )
    dead.add_argument(
        "--approach-duration",
        type=float,
        help="override the configured sitting approach duration",
    )

    walk = actions.add_parser("walk", help="walk in a named direction")
    walk.add_argument("direction", choices=DIRECTIONS)
    walk.add_argument("--cycles", type=int, default=1, help="0 means until Ctrl-C")
    walk.add_argument("--strength", type=float, default=1.0)

    move = actions.add_parser("move", help="send a ROS-like normalized velocity")
    move.add_argument("--x", type=float, default=0.0, help="forward (+) / backward (-)")
    move.add_argument("--y", type=float, default=0.0, help="left (+) / right (-)")
    move.add_argument("--yaw", type=float, default=0.0, help="turn left (+) / right (-)")
    move.add_argument("--cycles", type=int, default=1, help="0 means until Ctrl-C")

    actions.add_parser("positions", help="read all joint positions")
    actions.add_parser("stop", help="broadcast an immediate stop")
    return parser


def _scaled(command: MotionCommand, strength: float) -> MotionCommand:
    if not 0 < strength <= 1:
        raise ValueError("strength must be in the range (0, 1]")
    return MotionCommand(
        linear_x=command.linear_x * strength,
        linear_y=command.linear_y * strength,
        angular_z=command.angular_z * strength,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.show_targets and not args.simulate:
        parser.error("--show-targets requires --simulate")
    config = load_config(args.config)
    if args.port:
        config = replace(config, bus=replace(config.bus, port=args.port))

    bus = SimulationBus() if args.simulate else LewanSoulBus(config.bus)
    controller = SpiderController(
        config,
        bus,
        sleep=(lambda _seconds: None) if args.simulate else time.sleep,
    )

    try:
        if args.action == "stand":
            controller.stand(args.duration)
        elif args.action == "sit":
            controller.sit(args.duration)
        elif args.action in {"dead", "storage"}:
            controller.dead(args.duration, args.approach_duration)
        elif args.action == "walk":
            controller.walk(_scaled(DIRECTIONS[args.direction], args.strength), args.cycles)
        elif args.action == "move":
            controller.walk(MotionCommand(args.x, args.y, args.yaw), args.cycles)
        elif args.action == "positions":
            for name, position in controller.read_positions().items():
                print(
                    f"{name:16} coxa={position.coxa:4} "
                    f"femur={position.femur:4} tibia={position.tibia:4}"
                )
        elif args.action == "stop":
            controller.stop()
    except KeyboardInterrupt:
        print("Interrupted; stopping all servos.")
        controller.stop()
    except Exception:
        # A partially staged frame has not received move_start, but stopping the
        # bus also handles failures that occur after a frame has begun moving.
        try:
            controller.stop()
        except Exception:
            pass
        raise
    finally:
        if args.simulate:
            assert isinstance(bus, SimulationBus)
            staged = sum(len(frame) for frame in bus.history)
            print(f"Simulation complete: {len(bus.history)} frames, {staged} servo targets")
            if args.show_targets and bus.history:
                for leg in config.legs:
                    print(
                        f"{leg.name:18} "
                        f"coxa={bus.positions[leg.coxa.servo_id]:4} "
                        f"femur={bus.positions[leg.femur.servo_id]:4} "
                        f"tibia={bus.positions[leg.tibia.servo_id]:4}"
                    )
        bus.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
