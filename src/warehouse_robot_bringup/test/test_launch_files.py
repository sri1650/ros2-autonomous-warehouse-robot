from pathlib import Path

import yaml


ROOT = Path(__file__).parents[3]


def test_required_configuration_files_parse():
    config = ROOT / "src" / "warehouse_robot_bringup" / "config"
    for file_name in ("application.yaml", "controllers.yaml", "ekf.yaml", "nav2.yaml", "slam.yaml"):
        with (config / file_name).open(encoding="utf-8") as stream:
            assert yaml.safe_load(stream)


def test_robot_model_defines_safety_critical_sensors():
    robot = (
        ROOT
        / "src"
        / "warehouse_robot_description"
        / "urdf"
        / "warehouse_robot.urdf.xacro"
    ).read_text(encoding="utf-8")
    assert 'type="gpu_lidar"' in robot
    assert 'type="imu"' in robot
    assert "gz_ros2_control/GazeboSimSystem" in robot
