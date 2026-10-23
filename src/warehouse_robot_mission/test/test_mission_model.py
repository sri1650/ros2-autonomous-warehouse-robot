import unittest

from warehouse_robot_mission.model import MissionProgress, MissionState


class TestMissionProgress(unittest.TestCase):
    def test_mission_completes_all_waypoints(self):
        mission = MissionProgress("shift-a", 2)
        mission.start()
        mission.waypoint_succeeded()
        self.assertIs(mission.state, MissionState.NAVIGATING)
        self.assertEqual(mission.completion, 0.5)
        mission.waypoint_succeeded()
        self.assertIs(mission.state, MissionState.SUCCEEDED)
        self.assertEqual(mission.completion, 1.0)

    def test_cancel_is_fail_safe(self):
        mission = MissionProgress("shift-a", 1)
        mission.start()
        mission.request_cancel()
        mission.canceled()
        self.assertIs(mission.state, MissionState.CANCELED)

    def test_invalid_missions_are_rejected(self):
        for mission_id, count in (("", 1), ("valid", 0), ("valid", -1)):
            with self.subTest(mission_id=mission_id, waypoint_count=count):
                with self.assertRaises(ValueError):
                    MissionProgress(mission_id, count)
