from dataclasses import replace
from pathlib import Path
import unittest

from spider_robot.config import JointConfig, PoseOffsets, load_config


ROOT = Path(__file__).resolve().parents[1]


class ConfigTests(unittest.TestCase):
    def test_default_robot_configuration(self) -> None:
        config = load_config(ROOT / "config" / "spider.toml")

        self.assertEqual(len(config.legs), 8)
        self.assertEqual(
            {joint.servo_id for leg in config.legs for joint in (leg.coxa, leg.femur, leg.tibia)},
            set(range(1, 25)),
        )
        self.assertEqual(
            config.dead_pose.default,
            PoseOffsets(coxa=0.0, femur=-250.0, tibia=-330.0),
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

    def test_unknown_dead_pose_leg_is_rejected(self) -> None:
        config = load_config(ROOT / "config" / "spider.toml")
        dead_pose = replace(
            config.dead_pose,
            legs={"not_a_leg": PoseOffsets()},
        )

        with self.assertRaisesRegex(ValueError, "unknown leg overrides"):
            replace(config, dead_pose=dead_pose)

    def test_dead_pose_outside_joint_limits_is_rejected(self) -> None:
        config = load_config(ROOT / "config" / "spider.toml")
        dead_pose = replace(
            config.dead_pose,
            default=PoseOffsets(coxa=0.0, femur=-400.0, tibia=-330.0),
        )

        with self.assertRaisesRegex(ValueError, "dead_pose for"):
            replace(config, dead_pose=dead_pose)

    def test_dead_pose_can_override_one_leg(self) -> None:
        config = load_config(ROOT / "config" / "spider.toml")
        override = PoseOffsets(coxa=10.0, femur=-240.0, tibia=-320.0)
        dead_pose = replace(
            config.dead_pose,
            legs={"front_left": override},
        )
        config = replace(config, dead_pose=dead_pose)

        self.assertEqual(config.dead_pose.for_leg("front_left"), override)
        self.assertEqual(
            config.dead_pose.for_leg("rear_left"),
            config.dead_pose.default,
        )


if __name__ == "__main__":
    unittest.main()
