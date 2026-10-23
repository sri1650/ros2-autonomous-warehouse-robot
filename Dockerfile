FROM ros:jazzy-ros-base

ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions python3-pip python3-rosdep python3-vcstool \
    ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-slam-toolbox \
    ros-jazzy-robot-localization ros-jazzy-ros-gz ros-jazzy-ros2-control ros-jazzy-gz-ros2-control \
    ros-jazzy-ros2-controllers ros-jazzy-xacro ros-jazzy-rviz2 \
    git sudo && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid ${USER_GID} ${USERNAME} && \
    useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} && \
    echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}

USER ${USERNAME}
WORKDIR /workspace
COPY --chown=${USERNAME}:${USERNAME} . /workspace
RUN sudo rosdep init 2>/dev/null || true
RUN rosdep update && rosdep install --from-paths src --ignore-src -r -y

SHELL ["/bin/bash", "-c"]
RUN source /opt/ros/jazzy/setup.bash && colcon build --symlink-install

CMD ["bash"]
