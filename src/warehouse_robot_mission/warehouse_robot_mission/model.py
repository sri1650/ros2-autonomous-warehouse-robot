"""ROS-independent mission state machine, kept deterministic and unit-testable."""

from dataclasses import dataclass
from enum import Enum, auto


class MissionState(Enum):
    IDLE = auto()
    QUEUED = auto()
    NAVIGATING = auto()
    CANCELING = auto()
    SUCCEEDED = auto()
    CANCELED = auto()
    FAILED = auto()


TERMINAL_STATES = {MissionState.SUCCEEDED, MissionState.CANCELED, MissionState.FAILED}


@dataclass
class MissionProgress:
    mission_id: str
    waypoint_count: int
    completed: int = 0
    state: MissionState = MissionState.QUEUED
    detail: str = "Mission accepted"

    def __post_init__(self) -> None:
        if not self.mission_id.strip():
            raise ValueError("mission_id must not be empty")
        if self.waypoint_count < 1:
            raise ValueError("a mission requires at least one waypoint")

    @property
    def completion(self) -> float:
        return self.completed / self.waypoint_count

    def start(self) -> None:
        self._require(MissionState.QUEUED)
        self.state = MissionState.NAVIGATING
        self.detail = "Navigating to waypoint 1"

    def waypoint_succeeded(self) -> None:
        self._require(MissionState.NAVIGATING)
        self.completed += 1
        if self.completed == self.waypoint_count:
            self.state = MissionState.SUCCEEDED
            self.detail = "Mission completed"
        else:
            self.detail = f"Navigating to waypoint {self.completed + 1}"

    def request_cancel(self) -> None:
        if self.state in TERMINAL_STATES:
            return
        self.state = MissionState.CANCELING
        self.detail = "Canceling active navigation goal"

    def canceled(self) -> None:
        self._require(MissionState.CANCELING)
        self.state = MissionState.CANCELED
        self.detail = "Mission canceled"

    def fail(self, reason: str) -> None:
        if self.state in TERMINAL_STATES:
            raise RuntimeError("cannot fail a completed mission")
        self.state = MissionState.FAILED
        self.detail = reason or "Mission failed"

    def _require(self, expected: MissionState) -> None:
        if self.state is not expected:
            raise RuntimeError(f"expected {expected.name}, got {self.state.name}")
