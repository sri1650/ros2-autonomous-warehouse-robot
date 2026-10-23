# Verification strategy

## Current evidence

| Level | Evidence in this repository | Status |
|---|---|---|
| Pure logic | Mission transition tests; safety-policy C++ tests | Implemented |
| Static quality | Ruff, compiler warnings-as-errors, package metadata | Implemented |
| Build | ROS 2 Jazzy build/test workflow on Ubuntu 24.04 | Configured in GitHub Actions; result visible after push |
| Configuration | YAML parse and robot sensor/plugin assertions | Implemented |
| Simulation | Gazebo world, sensor bridge, Nav2/SLAM launch | Configured; local end-to-end run required |
| Hardware | Base, LiDAR, IMU, e-stop integration | Not performed |

“Configured” is deliberately not presented as “validated.” A green CI build establishes compilation and unit-test evidence. It does not establish navigation performance or hardware safety.

## Simulation acceptance test

Run on Ubuntu 24.04 with ROS 2 Jazzy:

1. Start `simulation.launch.py use_slam:=true`.
2. Confirm `/scan` is at least 8 Hz and `/imu/data` at least 80 Hz.
3. Confirm `map→odom→base_footprint` is connected and contains no competing publishers.
4. Drive the robot to map the warehouse; save the map.
5. Restart with `use_slam:=false` and the saved map.
6. Submit a three-waypoint mission and confirm ordered completion.
7. Place an obstacle within 0.35 m; confirm zero commanded base speed.
8. Stop the Nav2 command stream; confirm zero base output within 0.5 s.
9. Assert `safety/emergency_stop`; confirm motion is inhibited until cleared.
10. Capture a rosbag and screenshots, then attach results to a tagged release.

## Hardware evidence required before making hardware claims

- Encoder direction, scaling, and time synchronisation logs
- Measured sensor rates, timestamp latency, covariance, and dropouts
- Straight-line, rotation, square-path, and repeatability results
- Stopping-distance results at several speeds and payloads
- E-stop, communication-loss, sensor-loss, and power-cycle tests
- Navigation success rate over a documented test route
- Risk assessment and independent safety review
