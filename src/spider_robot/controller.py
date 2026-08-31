"""Whole-body controller: the overhead above individual legs."""

from __future__ import annotations

import time
from collections.abc import Callable

from .config import RobotConfig
from .gait import AlternatingTetrapodGait, MotionCommand, RippleGait, TripodGait
from .hardware import ServoBus
from .leg import Leg, LegPose, ResolvedLegPose


class SpiderController:
    """Coordinates calibrated legs and commits synchronized servo frames."""

    def __init__(
        self,
        config: RobotConfig,
        bus: ServoBus,
        sleep: Callable[[float], None] = time.sleep,
        gait_type: str = "alternating_tetrapod"
    ) -> None:
        self.config = config
        self.bus = bus
        self.legs = tuple(Leg(leg_config, bus) for leg_config in config.legs)
        self._legs_by_name = {leg.name: leg for leg in self.legs}
        
        # Initialize gait based on type
        if gait_type == "ripple":
            self._gait = RippleGait(config.gait, config.legs)
        elif gait_type == "tripod":
            self._gait = TripodGait(config.gait, config.legs)
        else:
            self._gait = AlternatingTetrapodGait(config.gait, config.legs)
            
        self._sleep = sleep

    def _apply(self, poses: dict[str, LegPose], duration: float) -> None:
        missing = self._legs_by_name.keys() - poses.keys()
        unknown = poses.keys() - self._legs_by_name.keys()
        if missing or unknown:
            raise ValueError(
                f"pose must target every configured leg; missing={sorted(missing)}, "
                f"unknown={sorted(unknown)}"
            )

        # Validate the complete frame before staging its first hardware command.
        resolved: dict[str, ResolvedLegPose] = {
            name: self._legs_by_name[name].resolve(pose)
            for name, pose in poses.items()
        }
        for leg in self.legs:
            leg.stage_resolved(resolved[leg.name], duration)
        self.bus.start()

    def stand(self, duration: float = 1.0, wait: bool = True) -> None:
        gait = self.config.gait
        pose = LegPose(
            femur=gait.stand_femur_offset,
            tibia=gait.stand_tibia_offset,
        )
        self._apply({leg.name: pose for leg in self.legs}, duration)
        if wait:
            self._sleep(duration)

    def sit(self, duration: float = 1.5, wait: bool = True) -> None:
        gait = self.config.gait
        pose = LegPose(
            femur=gait.sit_femur_offset,
            tibia=gait.sit_tibia_offset,
        )
        self._apply({leg.name: pose for leg in self.legs}, duration)
        if wait:
            self._sleep(duration)

    def dead(
        self,
        duration: float | None = None,
        approach_duration: float | None = None,
        wait: bool = True,
    ) -> None:
        """Curl all legs underneath in preparation for unpowered storage.

        The robot first moves through its sitting pose to avoid folding from an
        arbitrary gait phase. This method only positions the legs; it does not
        unload the servos or disconnect electrical power.
        """

        dead_pose = self.config.dead_pose
        curl_duration = dead_pose.duration if duration is None else duration
        sit_duration = (
            dead_pose.approach_duration
            if approach_duration is None
            else approach_duration
        )
        for name, value in (
            ("dead pose duration", curl_duration),
            ("dead pose approach duration", sit_duration),
        ):
            if not 0 < value <= 30:
                raise ValueError(f"{name} must be in (0, 30] seconds")

        # The approach must finish before the tighter storage curl is staged.
        self.sit(duration=sit_duration, wait=True)
        poses: dict[str, LegPose] = {}
        for leg in self.legs:
            offsets = dead_pose.for_leg(leg.name)
            poses[leg.name] = LegPose(offsets.coxa, offsets.femur, offsets.tibia)
        self._apply(poses, curl_duration)
        if wait:
            self._sleep(curl_duration)

    def step(self, command: MotionCommand) -> None:
        """Execute one complete gait cycle."""
        for frame in self._gait.frames(command):
            self._apply(frame.poses, frame.duration)
            self._sleep(frame.duration)

    def walk(self, command: MotionCommand, cycles: int = 1) -> None:
        """Walk for ``cycles``; use 0 to continue until interrupted."""

        if command.normalized().is_zero:
            self.stop()
            return
        if cycles < 0:
            raise ValueError("cycles must be zero or positive")

        completed = 0
        while cycles == 0 or completed < cycles:
            self.step(command)
            completed += 1

    def read_positions(self) -> dict[str, ResolvedLegPose]:
        return {leg.name: leg.read_positions() for leg in self.legs}

    def stop(self) -> None:
        self.bus.stop()

    def set_powered(self, powered: bool) -> None:
        self.bus.set_powered(powered)


__all__ = ["MotionCommand", "SpiderController"]
