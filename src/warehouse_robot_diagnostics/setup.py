from setuptools import find_packages, setup

package_name = "warehouse_robot_diagnostics"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Warehouse Robot Maintainer",
    maintainer_email="maintainer@example.com",
    description="Runtime diagnostics aggregator.",
    license="MIT",
    entry_points={
        "console_scripts": ["diagnostics_aggregator = warehouse_robot_diagnostics.node:main"]
    },
)
