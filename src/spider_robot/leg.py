"""Single-leg control layer."""

from __future__ import annotations

from dataclasses import dataclass

from .config import LegConfig
from .hardware import ServoBus


@dataclass(frozen=True)
class LegPose:
    """Logical joint offsets in ticks relative to calibrated neutral."""

    coxa: float = 0.0
    femur: float = 0.0
    tibia: float = 0.0


@dataclass(frozen=True)
class ResolvedLegPose:
    """Validated absolute servo targets for one leg."""

    coxa: int
    femur: int
    tibia: int


class Leg:
    """Owns the three joints of one leg and enforces their calibration."""

    def __init__(self, config: LegConfig, bus: ServoBus) -> None:
        self.config = config
        self.bus = bus

    @property
    def name(self) -> str:
        return self.config.name

    def resolve(self, pose: LegPose) -> ResolvedLegPose:
        """Resolve all targets before any serial commands are sent."""

        return ResolvedLegPose(
            coxa=self.config.coxa.resolve(pose.coxa),
            femur=self.config.femur.resolve(pose.femur),
            tibia=self.config.tibia.resolve(pose.tibia),
        )

    def stage_resolved(self, pose: ResolvedLegPose, duration: float) -> None:
        if not 0 < duration <= 30:
            raise ValueError("move duration must be in (0, 30] seconds")
        self.bus.stage_position(self.config.coxa.servo_id, pose.coxa, duration)
        self.bus.stage_position(self.config.femur.servo_id, pose.femur, duration)
        self.bus.stage_position(self.config.tibia.servo_id, pose.tibia, duration)

    def stage(self, pose: LegPose, duration: float) -> None:
        self.stage_resolved(self.resolve(pose), duration)

    def read_positions(self) -> ResolvedLegPose:
        return ResolvedLegPose(
            coxa=int(round(self.bus.read_position(self.config.coxa.servo_id))),
            femur=int(round(self.bus.read_position(self.config.femur.servo_id))),
            tibia=int(round(self.bus.read_position(self.config.tibia.servo_id))),
        )

    def set_position(self, joint_type: str, position: float) -> None:
        """Set individual servo position directly."""
        if joint_type == "coxa":
            servo_id = self.config.coxa.servo_id
            resolved_position = self.config.coxa.resolve(position)
        elif joint_type == "femur":
            servo_id = self.config.femur.servo_id
            resolved_position = self.config.femur.resolve(position)
        elif joint_type == "tibia":
            servo_id = self.config.tibia.servo_id
            resolved_position = self.config.tibia.resolve(position)
        else:
            raise ValueError(f"Unknown joint type: {joint_type}")
            
        # Set the position directly without duration (for immediate control)
        self.bus.stage_position(servo_id, resolved_position, 0.1)  # 0.1s duration
