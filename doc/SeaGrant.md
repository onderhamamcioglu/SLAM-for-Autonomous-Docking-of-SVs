# Testing Fast-LIO2 with the MIT Sea Grant Dataset
This document explains what should be done to use the [MIT Sea Grant Marine Perception Dataset](https://seagrant.mit.edu/auvlab-datasets-marine-perception-1/) for testing Fast-LIO2 for SLAM in a maritime environment: downloading the recordings, converting them from ROS 1 to ROS 2 format, configuring Fast-LIO2 for the dataset's Velodyne LiDAR, and playing them back.

Some useful scenarios are:

- rex_2019_10_08__13_29_51_harvard_bridge
- philos_2020_10_22_mooring_field_with_ferry

## 1. Prerequisites
* **ROS2** (e.g., Humble)
* **Livox-SDK2 & `livox_ros_driver2`** (required to build Fast-LIO2 even when using Velodyne data, see [`LivoxMid360.md`](LivoxMid360.md))
* **Fast-LIO2** (compiled in your ROS 2 workspace, e.g., `~/ws`, see [`FastLIO2.md`](FastLIO2.md))

## 2. Installing Dependencies
```bash
sudo apt install python3-pip -y
pip install rosbags
```
## 3. Preparation

### 3.1 Setting The Environment
```bash
mkdir ~/datasets
```
> Download desired recordings of the dataset from its website and move to `~/datasets/`

### 3.2 Converting The Dataset
Since the MIT Sea Grant dataset is provided in ROS 1 `.bag` format, we need to convert it to ROS 2 format (`.db3` with SQLite3) to use it with our ROS 2 setup.

```bash
cd ~/datasets
tar -xf <ARCHIVE FILE>
cd <RECORDING FOLDER>
rosbags-convert --src section.bag --dst section_ros2 --dst-typestore ros2_humble
mv section_ros2/section_ros2.db3 section_ros2/section_ros2_0.db3
rm -rf section_ros2/metadata.yaml
ros2 bag reindex section_ros2 -s sqlite3
```

### 3.3 Validating Conversion
Command `ros2 bag info section_ros2/` should give an output that contains `Topic: /velodyne_points` and `Topic: /imu/data`

### 3.4 Configuring Fast-LIO2 for Velodyne LiDAR
Open configuration file using `nano ~/ws/src/FAST_LIO/config/velodyne.yaml` and modify the topics to match the ones you found in the previous step:
```yaml
common:
    lidar_topic: "/velodyne_points"
    imu_topic: "/imu/data"
    time_sync_en: false         # Keep false initially unless timestamps drift
    lidar_type: 2               # 1 for Livox, 2 for Velodyne, 3 for Ouster
```

## 4. Testing

### 4.1 Launch Mapping Node
```bash
cd ~/ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fast_lio mapping.launch.py config_file:=velodyne.yaml use_sim_time:=true
```
At this point, RViz should open on your screen. It will be completely empty, waiting for data.

### 4.2 Playing the Dataset
```bash
source /opt/ros/humble/setup.bash
ros2 bag play ~/datasets/<RECORDING FOLDER>/section_ros2 --clock
```
Switch your attention back to the RViz window. As soon as you hit enter on the rosbag play command, you should immediately see a dense 3D point cloud start drawing itself on the screen.
