#pragma once

#include <algorithm>

namespace warehouse_robot_safety
{

struct SafetyInput
{
  bool emergency_stop{false};
  bool command_stale{true};
  bool sensor_stale{true};
  double nearest_obstacle_m{100.0};
  double linear_x{0.0};
  double angular_z{0.0};
};

struct SafetyOutput
{
  bool safe_to_move{false};
  bool obstacle_stop{false};
  bool sensor_fault{false};
  double linear_x{0.0};
  double angular_z{0.0};
};

class SafetyPolicy
{
public:
  SafetyPolicy(double stop_distance_m, double slow_distance_m, double maximum_linear_mps);
  SafetyOutput evaluate(const SafetyInput & input) const;

private:
  double stop_distance_m_;
  double slow_distance_m_;
  double maximum_linear_mps_;
};

}  // namespace warehouse_robot_safety
