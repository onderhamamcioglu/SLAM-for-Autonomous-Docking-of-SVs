# Fast-LIO2 on ROS 2
This document covers everything related to Fast-LIO2 in this project: installing and building it with ROS 2 Humble on Ubuntu 22.04 (for both PC and Jetson), running it in real time with the Livox Mid-360 LiDAR or on recorded bag files, including live mapping and saving the generated map.

> [!NOTE]
> For testing Fast-LIO2 with the MIT Sea Grant Marine Perception Dataset instead of a real sensor, see [`SeaGrant.md`](SeaGrant.md).

## 1. Prerequisites

* **Ubuntu 22.04**: Native, VM, WSL via `wsl --install -d Ubuntu-22.04`, or Jetson with JetPack 6.1 flashed.
* **ROS 2** [Humble](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html): (Desktop-Full installation is recommended)
* **Livox Setup** (see [`LivoxMid360.md`](LivoxMid360.md)): `Livox-SDK2` installed, `livox_ros_driver2` cloned into your ROS 2 workspace (e.g., `~/ws/src`), and — for real-time operation — the Mid-360 connected via Ethernet, powered, and network configured.

## 2. Installation

### 2.1 Dependencies
```bash
sudo apt update
sudo apt install python3-colcon-common-extensions ros-humble-pcl-ros ros-humble-rmw-cyclonedds-cpp cmake -y
```

### 2.2 Repository Cloning
`Livox-SDK2`, the ROS 2 workspace (`~/ws`), and `livox_ros_driver2` should already be set up as described in [`LivoxMid360.md`](LivoxMid360.md). Navigate to the source directory and clone Fast-LIO2 next to the driver.
Currently there is a branch for using Fast-LIO2 on ROS2 in the original repository: https://github.com/hku-mars/FAST_LIO/tree/ROS2
```bash
cd ~/ws/src
git clone -b ROS2 https://github.com/hku-mars/FAST_LIO.git --recursive
```

### 2.3 Build
> [!IMPORTANT]
> Never use `sudo` with `colcon`.

Configure the Livox driver for ROS 2, source your environment, and build.
```bash
cd ~/ws
cp src/livox_ros_driver2/package_ROS2.xml src/livox_ros_driver2/package.xml
cp -r src/livox_ros_driver2/launch_ROS2 src/livox_ros_driver2/launch

source /opt/ros/humble/setup.bash
colcon build --symlink-install --cmake-args -DROS_EDITION=ROS2 -DDISTRO_ROS=humble -Wno-dev
source install/setup.bash
```

## 3. Running Fast-LIO2 with Livox Mid-360 LiDAR
This section documents how to run Fast-LIO2 in real time using the actual Livox Mid-360 LiDAR instead of a pre-recorded dataset. It assumes the sensor and the `livox_ros_driver2` package are already set up as described in [`LivoxMid360.md`](LivoxMid360.md).

### 3.1 Configuring the Livox Driver Output Format
Fast-LIO2 expects the Livox **CustomMsg** format (`livox_ros_driver2/msg/CustomMsg`) on the LiDAR topic, not the standard `sensor_msgs/PointCloud2`. The output format is controlled by the `xfer_format` parameter in the driver's launch files:

* `xfer_format = 0` → `sensor_msgs/PointCloud2` (used by `rviz_MID360_launch.py`)
* `xfer_format = 1` → `livox_ros_driver2/msg/CustomMsg` (used by `msg_MID360_launch.py`)

Therefore, use `msg_MID360_launch.py` when running Fast-LIO2. No file modification is needed unless you changed the defaults.

> [!NOTE]
> Make sure the IP addresses in `~/ws/src/livox_ros_driver2/config/MID360_config.json` are still configured correctly for your LiDAR. (See [`LivoxMid360.md`](LivoxMid360.md))

### 3.2 Configuring Fast-LIO2 for the Mid-360
Open the configuration file using `nano ~/ws/src/FAST_LIO/config/mid360.yaml` and verify the topics match the ones published by the Livox driver:
```yaml
common:
    lidar_topic: "/livox/lidar"
    imu_topic: "/livox/imu"
    time_sync_en: false         # Keep false, the Mid-360 provides synced LiDAR and IMU data
    lidar_type: 1               # 1 for Livox, 2 for Velodyne, 3 for Ouster
```
The default extrinsics in `mid360.yaml` already correspond to the Mid-360's built-in IMU, so they do not need to be changed.

### 3.3 (Optional) Enabling Map Saving
To save the generated map as a `.pcd` file when the mapping node shuts down, enable the following in the same configuration file:
```yaml
pcd_save:
    pcd_save_en: true
```
The map will be saved to `~/ws/install/fast_lio/share/fast_lio/PCD/` (or `src/FAST_LIO/PCD/` when built with `--symlink-install`).

### 3.4 Launch the Livox Driver
In the first terminal, start the driver in CustomMsg mode:
```bash
cd ~/ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch livox_ros_driver2 msg_MID360_launch.py
```

Verify that data is being published by opening a new terminal and running:
```bash
source ~/ws/install/setup.bash
ros2 topic hz /livox/lidar /livox/imu
```
You should see `/livox/lidar` at ~10 Hz and `/livox/imu` at ~200 Hz.

### 3.5 Launch Mapping Node
In a second terminal, start Fast-LIO2:
```bash
cd ~/ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fast_lio mapping.launch.py config_file:=mid360.yaml
```

> [!IMPORTANT]
> Unlike dataset playback, do **not** pass `use_sim_time:=true` when running with the real sensor. The node must use the system clock.

RViz should open and immediately start drawing the point cloud map as the LiDAR data streams in. Slowly move the sensor around to build the map; the odometry trajectory is visualized alongside the accumulated point cloud.

### 3.6 Saving the Map
If `pcd_save_en` was enabled, simply stop the mapping node with `Ctrl+C` in its terminal. The accumulated map is written as `scans.pcd` during shutdown. It can be inspected later with `pcl_viewer`:
```bash
sudo apt install pcl-tools -y
pcl_viewer scans.pcd
```

## 4. Using Recorded Data Instead
Instead of the live sensor, Fast-LIO2 can also be run on data previously recorded into a ROS 2 bag file (see [`LivoxMid360.md`](LivoxMid360.md) for how to record `/livox/lidar` and `/livox/imu`).

> [!IMPORTANT]
> The bag must contain the LiDAR topic in **CustomMsg** format, so the recording must be made while the driver is running with `msg_MID360_launch.py`. A bag recorded with `rviz_MID360_launch.py` contains `sensor_msgs/PointCloud2` and will not work with Fast-LIO2. You can verify with `ros2 bag info <BAG FOLDER>`.

### 4.1 Launch Mapping Node
Start Fast-LIO2 with the same Mid-360 configuration as in [section 3.5](#35-launch-mapping-node), but this time with `use_sim_time:=true` so the node follows the timestamps of the recording instead of the system clock:
```bash
cd ~/ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fast_lio mapping.launch.py config_file:=mid360.yaml use_sim_time:=true
```
RViz will open and stay empty, waiting for data.

### 4.2 Playing the Recording
In a second terminal, play the bag while publishing the recorded time on the `/clock` topic:
```bash
source ~/ws/install/setup.bash
ros2 bag play ~/bag_files/livox_test_record --clock
```
The map should start drawing itself in RViz as soon as playback begins. Map saving works the same way as with the live sensor (see [section 3.3](#33-optional-enabling-map-saving)).

> [!NOTE]
> To test Fast-LIO2 with a public maritime dataset instead of your own recordings, see [`SeaGrant.md`](SeaGrant.md).

## 5. Troubleshooting
* **RViz stays empty:** Check `ros2 topic hz /livox/lidar`. If there is no output, the driver is not receiving data — re-check the network configuration and the IP addresses in `MID360_config.json`.
* **`msg_MID360_launch.py` runs but Fast-LIO2 prints no odometry:** Confirm the LiDAR topic type with `ros2 topic info /livox/lidar`. It must be `livox_ros_driver2/msg/CustomMsg`; if it shows `sensor_msgs/msg/PointCloud2`, the driver was launched with the wrong launch file (`rviz_MID360_launch.py`).
