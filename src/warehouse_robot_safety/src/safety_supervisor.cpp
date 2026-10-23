#include <algorithm>
#include <chrono>
#include <cmath>
#include <limits>
#include <memory>
#include <string>

#include "geometry_msgs/msg/twist.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "std_msgs/msg/bool.hpp"
#include "warehouse_robot_interfaces/msg/safety_state.hpp"
#include "warehouse_robot_safety/safety_policy.hpp"

using namespace std::chrono_literals;

class SafetySupervisor : public rclcpp::Node
{
public:
  SafetySupervisor()
  : Node("safety_supervisor"),
    policy_(
      declare_parameter("stop_distance_m", 0.35),
      declare_parameter("slow_distance_m", 0.80),
      declare_parameter("maximum_linear_mps", 0.70)),
    command_timeout_(std::chrono::duration<double>(declare_parameter("command_timeout_s", 0.5))),
    scan_timeout_(std::chrono::duration<double>(declare_parameter("scan_timeout_s", 0.5)))
  {
    safe_command_publisher_ = create_publisher<geometry_msgs::msg::TwistStamped>("cmd_vel", 10);
    state_publisher_ = create_publisher<warehouse_robot_interfaces::msg::SafetyState>(
      "safety/state", rclcpp::QoS(1).transient_local());
    command_subscription_ = create_subscription<geometry_msgs::msg::Twist>(
      "cmd_vel_nav", 10, [this](geometry_msgs::msg::Twist::SharedPtr message) {
        requested_command_ = *message;
        last_command_time_ = now();
        command_received_ = true;
      });
    scan_subscription_ = create_subscription<sensor_msgs::msg::LaserScan>(
      "scan", rclcpp::SensorDataQoS(), [this](sensor_msgs::msg::LaserScan::SharedPtr scan) {
        nearest_obstacle_m_ = std::numeric_limits<double>::infinity();
        for (const auto range : scan->ranges) {
          if (std::isfinite(range)) {
            nearest_obstacle_m_ = std::min(nearest_obstacle_m_, static_cast<double>(range));
          }
        }
        last_scan_time_ = now();
        scan_received_ = true;
      });
    estop_subscription_ = create_subscription<std_msgs::msg::Bool>(
      "safety/emergency_stop", rclcpp::QoS(1).transient_local(),
      [this](std_msgs::msg::Bool::SharedPtr message) {emergency_stop_ = message->data;});
    timer_ = create_wall_timer(50ms, [this]() {tick();});
  }

private:
  void tick()
  {
    const bool stale = !command_received_ ||
      (now() - last_command_time_).seconds() > command_timeout_.count();
    const bool sensor_stale = !scan_received_ ||
      (now() - last_scan_time_).seconds() > scan_timeout_.count();
    warehouse_robot_safety::SafetyInput input;
    input.emergency_stop = emergency_stop_;
    input.command_stale = stale;
    input.sensor_stale = sensor_stale;
    input.nearest_obstacle_m = nearest_obstacle_m_;
    input.linear_x = requested_command_.linear.x;
    input.angular_z = requested_command_.angular.z;
    const auto output = policy_.evaluate(input);

    geometry_msgs::msg::TwistStamped safe_command;
    safe_command.header.stamp = now();
    safe_command.header.frame_id = "base_footprint";
    safe_command.twist.linear.x = output.linear_x;
    safe_command.twist.angular.z = output.angular_z;
    safe_command_publisher_->publish(safe_command);

    warehouse_robot_interfaces::msg::SafetyState state;
    state.stamp = now().to_msg();
    state.safe_to_move = output.safe_to_move;
    state.emergency_stop = emergency_stop_;
    state.command_timed_out = stale;
    state.obstacle_stop = output.obstacle_stop;
    state.nearest_obstacle_m = static_cast<float>(nearest_obstacle_m_);
    state.reason = emergency_stop_ ? "EMERGENCY_STOP" :
      (sensor_stale ? "SENSOR_TIMEOUT" :
      (stale ? "COMMAND_TIMEOUT" : (output.obstacle_stop ? "OBSTACLE" : "CLEAR")));
    state_publisher_->publish(state);
  }

  warehouse_robot_safety::SafetyPolicy policy_;
  std::chrono::duration<double> command_timeout_;
  std::chrono::duration<double> scan_timeout_;
  rclcpp::Time last_command_time_{0, 0, RCL_ROS_TIME};
  rclcpp::Time last_scan_time_{0, 0, RCL_ROS_TIME};
  geometry_msgs::msg::Twist requested_command_;
  double nearest_obstacle_m_{std::numeric_limits<double>::infinity()};
  bool emergency_stop_{false};
  bool command_received_{false};
  bool scan_received_{false};
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr safe_command_publisher_;
  rclcpp::Publisher<warehouse_robot_interfaces::msg::SafetyState>::SharedPtr state_publisher_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr command_subscription_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_subscription_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr estop_subscription_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SafetySupervisor>());
  rclcpp::shutdown();
  return 0;
}
