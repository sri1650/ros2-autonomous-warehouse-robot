"""Start Gazebo, the simulated robot, localisation/navigation, and AMR applications."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    bringup = Path(get_package_share_directory("warehouse_robot_bringup"))
    description = Path(get_package_share_directory("warehouse_robot_description"))
    nav2 = Path(get_package_share_directory("nav2_bringup"))
    slam = Path(get_package_share_directory("slam_toolbox"))

    use_sim_time = LaunchConfiguration("use_sim_time")
    use_slam = LaunchConfiguration("use_slam")
    use_rviz = LaunchConfiguration("use_rviz")
    headless = LaunchConfiguration("headless")
    map_file = LaunchConfiguration("map")
    robot_description = ParameterValue(
        Command(["xacro ", str(description / "urdf/warehouse_robot.urdf.xacro")]),
        value_type=str,
    )

    gz_sim_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(Path(get_package_share_directory("ros_gz_sim")) / "launch/gz_sim.launch.py")
        ),
        condition=UnlessCondition(headless),
        launch_arguments={
            "gz_args": ["-r ", str(bringup / "worlds/warehouse.sdf")]
        }.items(),
    )
    gz_sim_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(Path(get_package_share_directory("ros_gz_sim")) / "launch/gz_sim.launch.py")
        ),
        condition=IfCondition(headless),
        launch_arguments={
            "gz_args": ["-r -s ", str(bringup / "worlds/warehouse.sdf")]
        }.items(),
    )

    nav2_common = {
        "use_sim_time": use_sim_time,
        "params_file": str(bringup / "config/nav2.yaml"),
        "autostart": "true",
    }

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("use_slam", default_value="true"),
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("headless", default_value="false"),
            DeclareLaunchArgument("map", default_value=""),
            gz_sim_gui,
            gz_sim_headless,
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": robot_description, "use_sim_time": use_sim_time}],
            ),
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=["-topic", "robot_description", "-name", "warehouse_robot", "-z", "0.11"],
                output="screen",
            ),
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                arguments=[
                    "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
                    "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
                    "/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU",
                ],
                output="screen",
            ),
            TimerAction(
                period=4.0,
                actions=[
                    Node(
                        package="controller_manager",
                        executable="spawner",
                        arguments=[
                            "joint_state_broadcaster",
                            "--controller-manager",
                            "/controller_manager",
                        ],
                    ),
                    Node(
                        package="controller_manager",
                        executable="spawner",
                        arguments=[
                            "diff_drive_controller",
                            "--controller-manager",
                            "/controller_manager",
                        ],
                    ),
                ],
            ),
            Node(
                package="robot_localization",
                executable="ekf_node",
                name="ekf_filter_node",
                parameters=[str(bringup / "config/ekf.yaml"), {"use_sim_time": use_sim_time}],
                remappings=[("odometry/filtered", "/odometry/filtered")],
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(slam / "launch/online_async_launch.py")),
                condition=IfCondition(use_slam),
                launch_arguments={
                    "use_sim_time": use_sim_time,
                    "slam_params_file": str(bringup / "config/slam.yaml"),
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(nav2 / "launch/bringup_launch.py")),
                condition=UnlessCondition(use_slam),
                launch_arguments={**nav2_common, "slam": "false", "map": map_file}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(nav2 / "launch/navigation_launch.py")),
                condition=IfCondition(use_slam),
                launch_arguments=nav2_common.items(),
            ),
            Node(
                package="warehouse_robot_mission",
                executable="mission_manager",
                parameters=[str(bringup / "config/application.yaml")],
                output="screen",
            ),
            Node(
                package="warehouse_robot_navigation",
                executable="navigation_manager",
                parameters=[str(bringup / "config/application.yaml")],
            ),
            Node(
                package="warehouse_robot_safety",
                executable="safety_supervisor",
                parameters=[str(bringup / "config/application.yaml")],
                remappings=[
                    ("cmd_vel_nav", "/cmd_vel_smoothed"),
                    ("cmd_vel", "/diff_drive_controller/cmd_vel"),
                ],
                output="screen",
            ),
            Node(
                package="warehouse_robot_diagnostics",
                executable="diagnostics_aggregator",
                parameters=[str(bringup / "config/application.yaml")],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                condition=IfCondition(use_rviz),
                arguments=["-d", str(description / "rviz/warehouse_robot.rviz")],
                parameters=[{"use_sim_time": use_sim_time}],
            ),
        ]
    )
