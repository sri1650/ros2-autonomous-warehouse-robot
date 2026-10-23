"""Aggregates application heartbeats and safety state into /diagnostics."""

import rclpy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rclpy.node import Node
from std_msgs.msg import String

from warehouse_robot_interfaces.msg import SafetyState


class DiagnosticsAggregator(Node):
    def __init__(self) -> None:
        super().__init__("diagnostics_aggregator")
        self.declare_parameter("heartbeat_timeout_s", 3.0)
        self._last_seen = {}
        self._last_value = {}
        self._safety = None
        self._publisher = self.create_publisher(DiagnosticArray, "/diagnostics", 10)
        self.create_subscription(String, "mission/status", self._mission_callback, 10)
        self.create_subscription(String, "navigation/status", self._navigation_callback, 10)
        self.create_subscription(SafetyState, "safety/state", self._safety_callback, 10)
        self.create_timer(1.0, self._publish)

    def _mission_callback(self, message: String) -> None:
        self._record("mission_manager", message.data)

    def _navigation_callback(self, message: String) -> None:
        self._record("navigation_manager", message.data)

    def _safety_callback(self, message: SafetyState) -> None:
        self._safety = message
        self._record("safety_supervisor", message.reason)

    def _record(self, component: str, value: str) -> None:
        self._last_seen[component] = self.get_clock().now()
        self._last_value[component] = value

    def _publish(self) -> None:
        now = self.get_clock().now()
        timeout = self.get_parameter("heartbeat_timeout_s").value
        array = DiagnosticArray()
        array.header.stamp = now.to_msg()
        for component in ("mission_manager", "navigation_manager", "safety_supervisor"):
            status = DiagnosticStatus()
            status.name = f"warehouse_robot/{component}"
            status.hardware_id = "simulated_amr"
            age = float("inf")
            if component in self._last_seen:
                age = (now - self._last_seen[component]).nanoseconds / 1e9
            status.level = DiagnosticStatus.OK if age <= timeout else DiagnosticStatus.ERROR
            status.message = self._last_value.get(component, "No heartbeat received")
            status.values = [KeyValue(key="heartbeat_age_s", value=f"{age:.2f}")]
            if component == "safety_supervisor" and self._safety is not None:
                if not self._safety.safe_to_move:
                    status.level = max(status.level, DiagnosticStatus.WARN)
                status.values.extend(
                    [
                        KeyValue(
                            key="nearest_obstacle_m",
                            value=f"{self._safety.nearest_obstacle_m:.3f}",
                        ),
                        KeyValue(
                            key="emergency_stop", value=str(self._safety.emergency_stop)
                        ),
                    ]
                )
            array.status.append(status)
        self._publisher.publish(array)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DiagnosticsAggregator()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
