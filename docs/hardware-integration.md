# Hardware integration plan

The simulation exposes the same high-level interfaces expected from a physical differential-drive platform. Porting should replace the Gazebo `ros2_control` system, not the mission or navigation layers.

## Candidate hardware contract

- Two velocity-controlled drive joints with position and velocity feedback
- 2D LiDAR publishing calibrated `sensor_msgs/LaserScan`
- IMU publishing calibrated `sensor_msgs/Imu` with covariance
- Safety PLC or safety relay exposing a read-only status signal to ROS
- Independent, hardwired e-stop and drive-enable circuit
- Monotonic clock synchronisation across compute and sensor devices

## Bring-up stages

1. Bench-test communication with wheels mechanically raised.
2. Verify sign conventions and encoder scale at low speed.
3. Measure command-to-motion latency and command watchdog behaviour.
4. Calibrate wheel radius/separation and IMU bias.
5. Tune EKF covariances from measured noise.
6. Validate footprint, LiDAR blind zones, and minimum stopping distance.
7. Tune Nav2 at reduced speed in a controlled area.
8. Execute fault-injection and recovery tests.

## Non-negotiable safety boundary

ROS must never be the only means of emergency stopping. A physical deployment requires safety-rated devices and a circuit designed and validated for the machine risk category. Parameters in this repository are illustrative starting points, not approved values.
