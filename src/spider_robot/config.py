"""Configuration types and TOML loading for the robot."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import tomllib


@dataclass(frozen=True)
class BusConfig:
    port: str
    baudrate: int = 115200
    timeout: float = 0.05
    discard_echo: bool = False
    broadcast_id: int = 254

    def __post_init__(self) -> None:
        if not self.port:
            raise ValueError("bus port must not be empty")
        if self.baudrate <= 0:
            raise ValueError("bus baudrate must be positive")
        if self.timeout <= 0:
            raise ValueError("bus timeout must be positive")
        if self.broadcast_id != 254:
            raise ValueError("LewanSoul broadcast_id must be 254")


@dataclass(frozen=True)
class JointConfig:
    servo_id: int
    neutral: int = 500
    minimum: int = 0
    maximum: int = 1000
    direction: int = 1

    def __post_init__(self) -> None:
        if not 0 <= self.servo_id <= 253:
            raise ValueError(f"servo_id must be between 0 and 253, got {self.servo_id}")
        if not 0 <= self.minimum < self.maximum <= 1000:
            raise ValueError("joint limits must satisfy 0 <= minimum < maximum <= 1000")
        if not self.minimum <= self.neutral <= self.maximum:
            raise ValueError("joint neutral must be within its limits")
        if self.direction not in (-1, 1):
            raise ValueError("joint direction must be -1 or 1")

    def resolve(self, offset: float) -> int:
        """Convert a calibrated logical offset into a servo tick target."""

        target = int(round(self.neutral + self.direction * offset))
        if not self.minimum <= target <= self.maximum:
            raise ValueError(
                f"servo {self.servo_id} target {target} is outside "
                f"[{self.minimum}, {self.maximum}]"
            )
        return target


@dataclass(frozen=True)
class LegConfig:
    name: str
    mount_angle_degrees: float
    gait_group: int
    sweep_scale: float
    coxa: JointConfig
    femur: JointConfig
    tibia: JointConfig

    def __post_init__(self) -> None:
        if self.gait_group not in (0, 1):
            raise ValueError(f"{self.name}: gait_group must be 0 or 1")
        if not 0 < self.sweep_scale <= 1:
            raise ValueError(f"{self.name}: sweep_scale must be in (0, 1]")


@dataclass(frozen=True)
class GaitConfig:
    phase_duration: float = 0.45
    sweep_ticks: float = 100.0
    lift_femur_offset: float = -100.0
    lift_tibia_offset: float = 0.0
    stand_femur_offset: float = 0.0
    stand_tibia_offset: float = -100.0
    sit_femur_offset: float = -200.0
    sit_tibia_offset: float = -300.0

    def __post_init__(self) -> None:
        if not 0 < self.phase_duration <= 30:
            raise ValueError("gait phase_duration must be in (0, 30] seconds")
        if self.sweep_ticks <= 0:
            raise ValueError("gait sweep_ticks must be positive")


@dataclass(frozen=True)
class PoseOffsets:
    """Logical joint offsets from each servo's calibrated neutral tick."""

    coxa: float = 0.0
    femur: float = 0.0
    tibia: float = 0.0


@dataclass(frozen=True)
class DeadPoseConfig:
    """Storage pose and its safe transition timing.

    Values in ``legs`` replace the default offsets for one named leg. Missing
    values in a TOML leg override inherit from ``default`` during loading.
    """

    default: PoseOffsets = field(
        default_factory=lambda: PoseOffsets(coxa=0.0, femur=-250.0, tibia=-330.0)
    )
    approach_duration: float = 2.0
    duration: float = 3.0
    legs: dict[str, PoseOffsets] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name, duration in (
            ("approach_duration", self.approach_duration),
            ("duration", self.duration),
        ):
            if not 0 < duration <= 30:
                raise ValueError(f"dead_pose {name} must be in (0, 30] seconds")

    def for_leg(self, leg_name: str) -> PoseOffsets:
        return self.legs.get(leg_name, self.default)


@dataclass(frozen=True)
class RobotConfig:
    bus: BusConfig
    gait: GaitConfig
    legs: tuple[LegConfig, ...]
    dead_pose: DeadPoseConfig = field(default_factory=DeadPoseConfig)

    def __post_init__(self) -> None:
        if not self.legs:
            raise ValueError("at least one leg must be configured")

        names = [leg.name for leg in self.legs]
        if len(names) != len(set(names)):
            raise ValueError("leg names must be unique")

        servo_ids = [
            joint.servo_id
            for leg in self.legs
            for joint in (leg.coxa, leg.femur, leg.tibia)
        ]
        if len(servo_ids) != len(set(servo_ids)):
            raise ValueError("every joint must have a unique servo ID")

        groups = {leg.gait_group for leg in self.legs}
        if groups != {0, 1}:
            raise ValueError("both gait groups 0 and 1 must contain at least one leg")

        unknown_dead_pose_legs = self.dead_pose.legs.keys() - set(names)
        if unknown_dead_pose_legs:
            raise ValueError(
                "dead_pose contains unknown leg overrides: "
                f"{sorted(unknown_dead_pose_legs)}"
            )

        # Reject an unsafe storage pose when configuration is loaded, rather
        # than after some servo targets have already been transmitted.
        for leg in self.legs:
            offsets = self.dead_pose.for_leg(leg.name)
            try:
                leg.coxa.resolve(offsets.coxa)
                leg.femur.resolve(offsets.femur)
                leg.tibia.resolve(offsets.tibia)
            except ValueError as error:
                raise ValueError(f"dead_pose for {leg.name}: {error}") from error


def _joint(data: dict[str, Any]) -> JointConfig:
    return JointConfig(
        servo_id=int(data["servo_id"]),
        neutral=int(data.get("neutral", 500)),
        minimum=int(data.get("minimum", 0)),
        maximum=int(data.get("maximum", 1000)),
        direction=int(data.get("direction", 1)),
    )


def _pose_offsets(
    data: dict[str, Any], defaults: PoseOffsets | None = None
) -> PoseOffsets:
    defaults = defaults or PoseOffsets()
    return PoseOffsets(
        coxa=float(data.get("coxa_offset", defaults.coxa)),
        femur=float(data.get("femur_offset", defaults.femur)),
        tibia=float(data.get("tibia_offset", defaults.tibia)),
    )


def load_config(path: str | Path) -> RobotConfig:
    """Load and validate a robot configuration from a TOML file."""

    config_path = Path(path)
    with config_path.open("rb") as config_file:
        data = tomllib.load(config_file)

    bus_data = data.get("bus", {})
    gait_data = data.get("gait", {})
    dead_pose_data = data.get("dead_pose", {})
    legs_data = data.get("legs", [])

    bus = BusConfig(
        port=str(bus_data.get("port", "/dev/ttyACM0")),
        baudrate=int(bus_data.get("baudrate", 115200)),
        timeout=float(bus_data.get("timeout", 0.05)),
        discard_echo=bool(bus_data.get("discard_echo", False)),
        broadcast_id=int(bus_data.get("broadcast_id", 254)),
    )
    gait = GaitConfig(
        phase_duration=float(gait_data.get("phase_duration", 0.45)),
        sweep_ticks=float(gait_data.get("sweep_ticks", 100.0)),
        lift_femur_offset=float(gait_data.get("lift_femur_offset", -100.0)),
        lift_tibia_offset=float(gait_data.get("lift_tibia_offset", 0.0)),
        stand_femur_offset=float(gait_data.get("stand_femur_offset", 0.0)),
        stand_tibia_offset=float(gait_data.get("stand_tibia_offset", -100.0)),
        sit_femur_offset=float(gait_data.get("sit_femur_offset", -200.0)),
        sit_tibia_offset=float(gait_data.get("sit_tibia_offset", -300.0)),
    )
    dead_pose_defaults = _pose_offsets(
        dead_pose_data,
        PoseOffsets(coxa=0.0, femur=-250.0, tibia=-330.0),
    )
    dead_pose = DeadPoseConfig(
        default=dead_pose_defaults,
        approach_duration=float(dead_pose_data.get("approach_duration", 2.0)),
        duration=float(dead_pose_data.get("duration", 3.0)),
        legs={
            str(leg_name): _pose_offsets(leg_offsets, dead_pose_defaults)
            for leg_name, leg_offsets in dead_pose_data.get("legs", {}).items()
        },
    )
    legs = tuple(
        LegConfig(
            name=str(leg["name"]),
            mount_angle_degrees=float(leg["mount_angle_degrees"]),
            gait_group=int(leg["gait_group"]),
            sweep_scale=float(leg.get("sweep_scale", 1.0)),
            coxa=_joint(leg["coxa"]),
            femur=_joint(leg["femur"]),
            tibia=_joint(leg["tibia"]),
        )
        for leg in legs_data
    )
    return RobotConfig(bus=bus, gait=gait, dead_pose=dead_pose, legs=legs)
