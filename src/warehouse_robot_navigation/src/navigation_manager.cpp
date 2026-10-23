#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav2_msgs/action/navigate_to_pose.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class NavigationManager : public rclcpp::Node
{
public:
  using NavigateToPose = nav2_msgs::action::NavigateToPose;
  using GoalHandle = rclcpp_action::ClientGoalHandle<NavigateToPose>;

  NavigationManager()
  : Node("navigation_manager")
  {
    const auto action_name =
      declare_parameter<std::string>("navigation_action", "/navigate_to_pose");
    client_ = rclcpp_action::create_client<NavigateToPose>(this, action_name);
    status_publisher_ = create_publisher<std_msgs::msg::String>("navigation/status", 10);
    goal_subscription_ = create_subscription<geometry_msgs::msg::PoseStamped>(
      "navigation/goal", 10,
      std::bind(&NavigationManager::on_goal, this, std::placeholders::_1));
    timer_ = create_wall_timer(1s, std::bind(&NavigationManager::publish_readiness, this));
  }

private:
  void on_goal(const geometry_msgs::msg::PoseStamped::SharedPtr goal)
  {
    if (goal->header.frame_id != "map") {
      RCLCPP_ERROR(get_logger(), "Navigation goal rejected: expected frame 'map', received '%s'",
        goal->header.frame_id.c_str());
      publish_status("REJECTED_INVALID_FRAME");
      return;
    }
    if (!client_->wait_for_action_server(2s)) {
      RCLCPP_ERROR(get_logger(), "Nav2 action server is unavailable");
      publish_status("NAV2_UNAVAILABLE");
      return;
    }

    NavigateToPose::Goal nav_goal;
    nav_goal.pose = *goal;
    rclcpp_action::Client<NavigateToPose>::SendGoalOptions options;
    options.goal_response_callback = [this](GoalHandle::SharedPtr handle) {
        publish_status(handle ? "GOAL_ACCEPTED" : "GOAL_REJECTED");
      };
    options.feedback_callback = [this](
      GoalHandle::SharedPtr,
      const std::shared_ptr<const NavigateToPose::Feedback> feedback) {
        publish_status("NAVIGATING:" + std::to_string(feedback->distance_remaining));
      };
    options.result_callback = [this](const GoalHandle::WrappedResult & result) {
        switch (result.code) {
          case rclcpp_action::ResultCode::SUCCEEDED: publish_status("SUCCEEDED"); break;
          case rclcpp_action::ResultCode::ABORTED: publish_status("ABORTED"); break;
          case rclcpp_action::ResultCode::CANCELED: publish_status("CANCELED"); break;
          default: publish_status("UNKNOWN"); break;
        }
      };
    client_->async_send_goal(nav_goal, options);
  }

  void publish_readiness()
  {
    publish_status(client_->action_server_is_ready() ? "READY" : "WAITING_FOR_NAV2");
  }

  void publish_status(const std::string & value)
  {
    std_msgs::msg::String message;
    message.data = value;
    status_publisher_->publish(message);
  }

  rclcpp_action::Client<NavigateToPose>::SharedPtr client_;
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr goal_subscription_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<NavigationManager>());
  rclcpp::shutdown();
  return 0;
}
