# Portfolio demo walkthrough

Use this sequence for a concise recruiter-facing demonstration once the simulation has been run locally.

1. Show the package graph and explain separation of mission, navigation, state estimation, safety, and hardware.
2. Launch the warehouse world and show live LiDAR, map, TF, and filtered odometry in RViz.
3. Submit a multi-stop mission and show action feedback updating per waypoint.
4. Introduce an obstacle and show the safety state transition plus zero base command.
5. Remove the obstacle and complete the mission.
6. Open the unit tests and CI run, explaining what each level proves.
7. End on the hardware-integration plan and clearly state that physical validation remains future work.

Recommended evidence to add after the first successful local run:

- 60–90 second screen recording
- RViz/Gazebo screenshot in the README
- rosbag metadata and a short results table
- GitHub release tagged `v0.1.0-sim-validated`
