"""ExecuteMission action server coordinating sequential navigation goals."""

from action_msgs.msg import GoalStatus
import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from std_msgs.msg import String
from warehouse_robot_interfaces.action import ExecuteMission

from .model import MissionProgress, MissionState

try:
    from nav2_msgs.action import NavigateToPose
except ImportError:  # Allows the pure model to be imported outside a ROS installation.
    NavigateToPose = None


class MissionManager(Node):
    def __init__(self) -> None:
        super().__init__("mission_manager")
        self.declare_parameter("navigation_action", "/navigate_to_pose")
        self.declare_parameter("navigation_server_timeout_s", 10.0)
        callback_group = ReentrantCallbackGroup()
        action_name = self.get_parameter("navigation_action").value
        self._navigation = ActionClient(
            self, NavigateToPose, action_name, callback_group=callback_group
        )
        self._active_navigation_goal = None
        self._status = self.create_publisher(String, "mission/status", 10)
        self._server = ActionServer(
            self,
            ExecuteMission,
            "execute_mission",
            execute_callback=self.execute,
            goal_callback=self.on_goal,
            cancel_callback=self.on_cancel,
            callback_group=callback_group,
        )

    def on_goal(self, request: ExecuteMission.Goal) -> GoalResponse:
        if not request.mission_id.strip() or not request.waypoints:
            self.get_logger().warning("Rejected mission with missing ID or waypoints")
            return GoalResponse.REJECT
        if any(pose.header.frame_id != "map" for pose in request.waypoints):
            self.get_logger().warning("Rejected mission: every waypoint must use the map frame")
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def on_cancel(self, _goal_handle) -> CancelResponse:
        self.get_logger().info("Mission cancellation requested")
        if self._active_navigation_goal is not None:
            self._active_navigation_goal.cancel_goal_async()
        return CancelResponse.ACCEPT

    async def execute(self, goal_handle):
        goal = goal_handle.request
        progress = MissionProgress(goal.mission_id, len(goal.waypoints))
        progress.start()
        self._publish_status(progress)

        timeout = self.get_parameter("navigation_server_timeout_s").value
        if not self._navigation.wait_for_server(timeout_sec=timeout):
            return self._abort(goal_handle, progress, "Nav2 action server unavailable")

        for index, waypoint in enumerate(goal.waypoints):
            if goal_handle.is_cancel_requested:
                return await self._cancel(goal_handle, progress)

            feedback = ExecuteMission.Feedback()
            feedback.current_state = ExecuteMission.Feedback.NAVIGATING
            feedback.active_waypoint = index
            feedback.completion = progress.completion
            feedback.detail = progress.detail
            goal_handle.publish_feedback(feedback)

            nav_goal = NavigateToPose.Goal()
            nav_goal.pose = self._normalise_timestamp(waypoint)
            future = self._navigation.send_goal_async(nav_goal)
            self._active_navigation_goal = await future
            if not self._active_navigation_goal.accepted:
                return self._abort(goal_handle, progress, f"Waypoint {index + 1} rejected")

            wrapped_result = await self._active_navigation_goal.get_result_async()
            if goal_handle.is_cancel_requested:
                return await self._cancel(goal_handle, progress)
            if wrapped_result.status != GoalStatus.STATUS_SUCCEEDED:
                return self._abort(
                    goal_handle, progress, f"Navigation failed at waypoint {index + 1}"
                )
            progress.waypoint_succeeded()
            self._publish_status(progress)

        goal_handle.succeed()
        return self._result(ExecuteMission.Result.SUCCEEDED, progress)

    async def _cancel(self, goal_handle, progress):
        progress.request_cancel()
        if self._active_navigation_goal is not None:
            await self._active_navigation_goal.cancel_goal_async()
        progress.canceled()
        goal_handle.canceled()
        self._publish_status(progress)
        return self._result(ExecuteMission.Result.CANCELED, progress)

    def _abort(self, goal_handle, progress, reason):
        progress.fail(reason)
        goal_handle.abort()
        self._publish_status(progress)
        return self._result(ExecuteMission.Result.FAILED, progress)

    @staticmethod
    def _result(status, progress):
        result = ExecuteMission.Result()
        result.status = status
        result.message = progress.detail
        result.completed_waypoints = progress.completed
        return result

    def _publish_status(self, progress: MissionProgress) -> None:
        message = String()
        message.data = f"{progress.mission_id}:{progress.state.name}:{progress.detail}"
        self._status.publish(message)

    def _normalise_timestamp(self, waypoint: PoseStamped) -> PoseStamped:
        if waypoint.header.stamp.sec == 0 and waypoint.header.stamp.nanosec == 0:
            waypoint.header.stamp = self.get_clock().now().to_msg()
        return waypoint


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MissionManager()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
