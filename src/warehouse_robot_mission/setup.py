from setuptools import find_packages, setup

package_name = "warehouse_robot_mission"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    tests_require=["pytest"],
    zip_safe=True,
    maintainer="Warehouse Robot Maintainer",
    maintainer_email="maintainer@example.com",
    description="Mission orchestration and waypoint sequencing.",
    license="MIT",
    entry_points={"console_scripts": ["mission_manager = warehouse_robot_mission.node:main"]},
)
