import pytest

from warehouse_robot_mission.model import MissionProgress, MissionState


def test_mission_completes_all_waypoints():
    mission = MissionProgress("shift-a", 2)
    mission.start()
    mission.waypoint_succeeded()
    assert mission.state is MissionState.NAVIGATING
    assert mission.completion == 0.5
    mission.waypoint_succeeded()
    assert mission.state is MissionState.SUCCEEDED
    assert mission.completion == 1.0


def test_cancel_is_fail_safe_and_idempotent_after_terminal_state():
    mission = MissionProgress("shift-a", 1)
    mission.start()
    mission.request_cancel()
    mission.canceled()
    mission.request_cancel()
    assert mission.state is MissionState.CANCELED


@pytest.mark.parametrize("mission_id,count", [("", 1), ("valid", 0), ("valid", -1)])
def test_invalid_missions_are_rejected(mission_id, count):
    with pytest.raises(ValueError):
        MissionProgress(mission_id, count)


def test_illegal_transition_is_rejected():
    mission = MissionProgress("shift-a", 1)
    with pytest.raises(RuntimeError):
        mission.waypoint_succeeded()
