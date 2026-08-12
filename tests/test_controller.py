from pathlib import Path
import unittest

from spider_robot.config import load_config
from spider_robot.controller import MotionCommand, SpiderController
from spider_robot.gait import AlternatingTetrapodGait
from spider_robot.hardware import SimulationBus


ROOT = Path(__file__).resolve().parents[1]


class ControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(ROOT / "config" / "spider.toml")
        self.bus = SimulationBus()
        self.waits: list[float] = []
        self.controller = SpiderController(self.config, self.bus, self.waits.append)

    def test_stand_is_one_synchronized_frame(self) -> None:
        self.controller.stand(duration=2.0)

        self.assertEqual(len(self.bus.history), 1)
        self.assertEqual(len(self.bus.history[0]), 24)
        self.assertEqual({command.servo_id for command in self.bus.history[0]}, set(range(1, 25)))
        self.assertEqual(self.waits, [2.0])

    def test_forward_step_is_four_complete_frames(self) -> None:
        self.controller.step(MotionCommand(linear_x=1.0))

        self.assertEqual(len(self.bus.history), 4)
        self.assertTrue(all(len(frame) == 24 for frame in self.bus.history))
        self.assertEqual(self.waits, [self.config.gait.phase_duration] * 4)

    def test_mount_angles_create_directional_coxa_targets(self) -> None:
        gait = AlternatingTetrapodGait(self.config.gait, self.config.legs)
        frames = gait.frames(MotionCommand(linear_x=1.0))

        # Compare each leg while it is the swinging group.
        self.assertGreater(frames[0].poses["front_left"].coxa, 0)
        self.assertLess(frames[2].poses["front_right"].coxa, 0)

    def test_zero_command_stops_without_staging_motion(self) -> None:
        self.controller.walk(MotionCommand(), cycles=1)

        self.assertTrue(self.bus.stopped)
        self.assertEqual(self.bus.history, [])

    def test_invalid_duration_is_rejected_before_staging(self) -> None:
        with self.assertRaisesRegex(ValueError, "duration"):
            self.controller.stand(duration=31)

        self.assertEqual(self.bus.pending, [])
        self.assertEqual(self.bus.history, [])

    def test_read_positions_are_named_by_leg(self) -> None:
        positions = self.controller.read_positions()

        self.assertEqual(set(positions), {leg.name for leg in self.config.legs})
        self.assertTrue(all(position.coxa == 500 for position in positions.values()))


if __name__ == "__main__":
    unittest.main()
