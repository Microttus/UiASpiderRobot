from dataclasses import replace
from pathlib import Path
import unittest

from spider_robot.config import JointConfig, load_config


ROOT = Path(__file__).resolve().parents[1]


class ConfigTests(unittest.TestCase):
    def test_default_robot_configuration(self) -> None:
        config = load_config(ROOT / "config" / "spider.toml")

        self.assertEqual(len(config.legs), 8)
        self.assertEqual(
            {joint.servo_id for leg in config.legs for joint in (leg.coxa, leg.femur, leg.tibia)},
            set(range(1, 25)),
        )

    def test_joint_calibration_applies_direction_and_limits(self) -> None:
        joint = JointConfig(servo_id=1, neutral=500, minimum=400, maximum=600, direction=-1)

        self.assertEqual(joint.resolve(25), 475)
        with self.assertRaises(ValueError):
            joint.resolve(101)

    def test_duplicate_servo_ids_are_rejected(self) -> None:
        config = load_config(ROOT / "config" / "spider.toml")
        duplicate_leg = replace(
            config.legs[1],
            coxa=replace(config.legs[1].coxa, servo_id=config.legs[0].coxa.servo_id),
        )

        with self.assertRaisesRegex(ValueError, "unique servo ID"):
            replace(config, legs=(config.legs[0], duplicate_leg, *config.legs[2:]))


if __name__ == "__main__":
    unittest.main()
