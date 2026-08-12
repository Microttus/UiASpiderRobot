"""Hardware boundary used by the motion layers.

Only this module knows about the concrete LewanSoul serial implementation.
Tests and future ROS 2 integration can use the same controller through the
``ServoBus`` protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .config import BusConfig


@runtime_checkable
class ServoBus(Protocol):
    """Small interface required by the leg layer."""

    def stage_position(self, servo_id: int, ticks: int, duration: float) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def read_position(self, servo_id: int) -> float: ...

    def set_powered(self, powered: bool) -> None: ...

    def close(self) -> None: ...


class LewanSoulBus:
    """Adapter around the bachelor project's LewanSoul servo bus driver."""

    def __init__(self, config: BusConfig) -> None:
        # Keep pyserial optional for simulation and unit tests.
        from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication

        self._communication = ServoBusCommunication(
            port=config.port,
            baudrate=config.baudrate,
            timeout=config.timeout,
            discard_echo=config.discard_echo,
            on_enter_power_on=False,
            on_exit_power_off=False,
        )
        self._broadcast = self._communication.get_servo(config.broadcast_id)
        self._closed = False

    def stage_position(self, servo_id: int, ticks: int, duration: float) -> None:
        self._communication.move_time_wait_write(servo_id, ticks, duration)

    def start(self) -> None:
        self._broadcast.move_start()

    def stop(self) -> None:
        self._broadcast.move_stop()

    def read_position(self, servo_id: int) -> float:
        return self._communication.pos_read(servo_id)

    def set_powered(self, powered: bool) -> None:
        self._broadcast.set_powered(powered)

    def close(self) -> None:
        if not self._closed:
            self._communication.serial_conn.close()
            self._closed = True

    def __enter__(self) -> "LewanSoulBus":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


@dataclass(frozen=True)
class StagedPosition:
    servo_id: int
    ticks: int
    duration: float


class SimulationBus:
    """In-memory bus for development without a connected robot."""

    def __init__(self) -> None:
        self.pending: list[StagedPosition] = []
        self.history: list[tuple[StagedPosition, ...]] = []
        self.positions: dict[int, int] = {}
        self.powered = False
        self.stopped = False
        self.closed = False

    def stage_position(self, servo_id: int, ticks: int, duration: float) -> None:
        self.pending.append(StagedPosition(servo_id, ticks, duration))

    def start(self) -> None:
        frame = tuple(self.pending)
        self.history.append(frame)
        for command in frame:
            self.positions[command.servo_id] = command.ticks
        self.pending.clear()
        self.stopped = False

    def stop(self) -> None:
        self.pending.clear()
        self.stopped = True

    def read_position(self, servo_id: int) -> float:
        return float(self.positions.get(servo_id, 500))

    def set_powered(self, powered: bool) -> None:
        self.powered = powered

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> "SimulationBus":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
