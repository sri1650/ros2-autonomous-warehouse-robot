cmake_minimum_required(VERSION 3.8)
project(warehouse_robot_navigation)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(navigation_manager src/navigation_manager.cpp)
target_compile_features(navigation_manager PUBLIC cxx_std_17)
ament_target_dependencies(navigation_manager rclcpp rclcpp_action nav2_msgs geometry_msgs std_msgs)

install(TARGETS navigation_manager DESTINATION lib/${PROJECT_NAME})
ament_package()
