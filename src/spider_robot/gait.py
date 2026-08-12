"""Joint-space gait generation.

This first gait deliberately stays in servo-tick space. It provides useful
directional control with the existing calibration data while keeping inverse
kinematics as a replaceable future layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, radians, sin

from .config import GaitConfig, LegConfig
from .leg import LegPose


@dataclass(frozen=True)
class MotionCommand:
    """Body velocity request, using the same axes as a ROS ``Twist``.

    ``linear_x`` is forward, ``linear_y`` is left, and ``angular_z`` is a
    counter-clockwise turn. Values are normalized to the range [-1, 1].
    """

    linear_x: float = 0.0
    linear_y: float = 0.0
    angular_z: float = 0.0

    def normalized(self) -> "MotionCommand":
        scale = max(abs(self.linear_x), abs(self.linear_y), abs(self.angular_z), 1.0)
        return MotionCommand(
            linear_x=self.linear_x / scale,
            linear_y=self.linear_y / scale,
            angular_z=self.angular_z / scale,
        )

    @property
    def magnitude(self) -> float:
        linear = hypot(self.linear_x, self.linear_y)
        return min(1.0, max(linear, abs(self.angular_z)))

    @property
    def is_zero(self) -> bool:
        return self.magnitude < 1e-9


@dataclass(frozen=True)
class GaitFrame:
    poses: dict[str, LegPose]
    duration: float


class AlternatingTetrapodGait:
    """Four-phase crawl in which alternating groups of four legs swing."""

    def __init__(self, config: GaitConfig, legs: tuple[LegConfig, ...]) -> None:
        self.config = config
        self.legs = legs

    def _stroke(self, command: MotionCommand, leg: LegConfig) -> float:
        angle = radians(leg.mount_angle_degrees)

        # Positive coxa motion follows the tangent of the leg's mounting angle.
        tangent_x = -sin(angle)
        tangent_y = cos(angle)

        # Feet move opposite the requested body motion during the stance phase.
        linear_component = -(
            command.linear_x * tangent_x + command.linear_y * tangent_y
        )
        rotational_component = -command.angular_z
        component = max(-1.0, min(1.0, linear_component + rotational_component))
        return component * self.config.sweep_ticks * leg.sweep_scale

    def frames(self, command: MotionCommand) -> tuple[GaitFrame, ...]:
        command = command.normalized()
        if command.is_zero:
            return ()

        strokes = {leg.name: self._stroke(command, leg) for leg in self.legs}
        duration = self.config.phase_duration
        frames: list[GaitFrame] = []

        # Each tuple is (swing group, lower swing group). A group stays at the
        # front of its stroke for two frames and then moves to the rear while
        # supporting the other group.
        for swing_group, lowered in ((0, False), (0, True), (1, False), (1, True)):
            poses: dict[str, LegPose] = {}
            for leg in self.legs:
                is_swing = leg.gait_group == swing_group
                coxa = strokes[leg.name] if is_swing else -strokes[leg.name]
                femur = self.config.stand_femur_offset
                tibia = self.config.stand_tibia_offset
                if is_swing and not lowered:
                    femur += self.config.lift_femur_offset
                    tibia += self.config.lift_tibia_offset
                poses[leg.name] = LegPose(coxa=coxa, femur=femur, tibia=tibia)
            frames.append(GaitFrame(poses=poses, duration=duration))

        return tuple(frames)
