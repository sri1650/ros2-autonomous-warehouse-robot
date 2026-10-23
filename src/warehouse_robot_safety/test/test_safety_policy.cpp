#include <gtest/gtest.h>

#include "warehouse_robot_safety/safety_policy.hpp"

using warehouse_robot_safety::SafetyInput;
using warehouse_robot_safety::SafetyPolicy;

TEST(SafetyPolicy, StopsForEmergencyStop)
{
  SafetyPolicy policy(0.35, 0.8, 0.7);
  SafetyInput input;
  input.emergency_stop = true;
  input.command_stale = false;
  input.sensor_stale = false;
  input.linear_x = 0.5;
  EXPECT_FALSE(policy.evaluate(input).safe_to_move);
  EXPECT_DOUBLE_EQ(policy.evaluate(input).linear_x, 0.0);
}

TEST(SafetyPolicy, StopsForStaleCommand)
{
  SafetyPolicy policy(0.35, 0.8, 0.7);
  SafetyInput input;
  input.command_stale = true;
  input.sensor_stale = false;
  input.linear_x = 0.5;
  EXPECT_FALSE(policy.evaluate(input).safe_to_move);
}

TEST(SafetyPolicy, ScalesForwardSpeedInWarningZone)
{
  SafetyPolicy policy(0.3, 0.7, 1.0);
  SafetyInput input;
  input.command_stale = false;
  input.sensor_stale = false;
  input.nearest_obstacle_m = 0.5;
  input.linear_x = 0.8;
  const auto output = policy.evaluate(input);
  EXPECT_TRUE(output.safe_to_move);
  EXPECT_NEAR(output.linear_x, 0.4, 1e-9);
}

TEST(SafetyPolicy, CapsMaximumVelocity)
{
  SafetyPolicy policy(0.3, 0.7, 0.6);
  SafetyInput input;
  input.command_stale = false;
  input.sensor_stale = false;
  input.nearest_obstacle_m = 2.0;
  input.linear_x = 2.0;
  EXPECT_DOUBLE_EQ(policy.evaluate(input).linear_x, 0.6);
}

TEST(SafetyPolicy, StopsWhenLidarHeartbeatIsStale)
{
  SafetyPolicy policy(0.3, 0.7, 0.6);
  SafetyInput input;
  input.command_stale = false;
  input.sensor_stale = true;
  input.linear_x = 0.4;
  const auto output = policy.evaluate(input);
  EXPECT_FALSE(output.safe_to_move);
  EXPECT_TRUE(output.sensor_fault);
}
