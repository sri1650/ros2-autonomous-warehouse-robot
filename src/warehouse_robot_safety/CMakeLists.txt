cmake_minimum_required(VERSION 3.8)
project(warehouse_robot_safety)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(warehouse_robot_interfaces REQUIRED)

add_library(safety_policy src/safety_policy.cpp)
target_include_directories(safety_policy PUBLIC include)
target_compile_features(safety_policy PUBLIC cxx_std_17)

add_executable(safety_supervisor src/safety_supervisor.cpp)
target_compile_features(safety_supervisor PUBLIC cxx_std_17)
target_link_libraries(safety_supervisor safety_policy)
ament_target_dependencies(safety_supervisor rclcpp geometry_msgs sensor_msgs std_msgs warehouse_robot_interfaces)

install(TARGETS safety_policy safety_supervisor
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_safety_policy test/test_safety_policy.cpp)
  target_link_libraries(test_safety_policy safety_policy)
  target_include_directories(test_safety_policy PUBLIC include)
endif()

ament_export_include_directories(include)
ament_package()
