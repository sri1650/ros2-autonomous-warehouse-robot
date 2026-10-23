#include "warehouse_robot_safety/safety_policy.hpp"

#include <stdexcept>

namespace warehouse_robot_safety
{

SafetyPolicy::SafetyPolicy(
  double stop_distance_m, double slow_distance_m, double maximum_linear_mps)
: stop_distance_m_(stop_distance_m),
  slow_distance_m_(slow_distance_m),
  maximum_linear_mps_(maximum_linear_mps)
{
  if (stop_distance_m <= 0.0 || slow_distance_m <= stop_distance_m || maximum_linear_mps <= 0.0) {
    throw std::invalid_argument("safety distances and velocity limits are inconsistent");
  }
}

SafetyOutput SafetyPolicy::evaluate(const SafetyInput & input) const
{
  SafetyOutput output;
  output.obstacle_stop = input.nearest_obstacle_m <= stop_distance_m_;
  output.sensor_fault = input.sensor_stale;
  if (input.emergency_stop || input.command_stale || input.sensor_stale || output.obstacle_stop) {
    return output;
  }

  output.safe_to_move = true;
  const auto requested = std::clamp(input.linear_x, -maximum_linear_mps_, maximum_linear_mps_);
  if (requested > 0.0 && input.nearest_obstacle_m < slow_distance_m_) {
    const auto scale = (input.nearest_obstacle_m - stop_distance_m_) /
      (slow_distance_m_ - stop_distance_m_);
    output.linear_x = requested * std::clamp(scale, 0.0, 1.0);
  } else {
    output.linear_x = requested;
  }
  output.angular_z = input.angular_z;
  return output;
}

}  // namespace warehouse_robot_safety
