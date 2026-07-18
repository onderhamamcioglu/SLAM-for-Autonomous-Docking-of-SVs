# Livox Mid-360 & ROS2 Integration on Nvidia Jetson
This part documents the setup process for using Livox Mid-360 LiDAR with ROS2 on Nvidia Jetson Orin Nano Super DevKit.

## 1. Prerequisites & Hardware Setup
First, ensure you have the following hardware ready and properly connected:

* **Nvidia Jetson** (Flashed with JetPack, running Ubuntu compatible with ROS2)
    - If you are doing local tests instead, any Ubuntu installation running a version compatible with your ROS 2 version (22.04 followed in this guide) works as well — natively, via WSL (`wsl --install -d Ubuntu-22.04`), on a server, or on any VM.
* **Livox Mid-360 LiDAR** (Connected to Jetson via Ethernet port and powered)
* **ROS 2** (Desktop-Full installation is needed):
    - Ubuntu 20.04 for [ROS2 Foxy](https://docs.ros.org/en/foxy/Installation/Ubuntu-Install-Debians.html)
    - Ubuntu 22.04 for [ROS2 Humble](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html) - _Followed in this guide_
    - Ubuntu 24.04 for [ROS2 Jazzy](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debians.html)

## 2. Network Configuration
The Livox Mid-360 communicates via Ethernet. Both the host (Jetson) and the LiDAR must be on the same subnet (`192.168.1.X`).

### 2.1. Jetson Static IP Setup
Configure the Jetson's wired connection to use a static IP address:
* **IP Address:** `192.168.1.50`
* **Netmask:** `255.255.255.0`
* **Gateway:** `192.168.1.1`

You can set this via the Ubuntu Network Settings GUI, `nmtui` or using `nmcli` in the terminal. Verify the IP using the `ifconfig` command.

### 2.2. Finding the LiDAR IP
The Mid-360's factory IP address is determined by the last 3 digits of its **Serial Number** written on its box.
* Example: If the code is `47MDL1C0010139`, the LiDAR IP is `192.168.1.139`.

Note down this ip adress since it will be needed later.

## 3. Software Installation

### 3.1. Install ROS2 and Build Tools
Ensure ROS2 Desktop is installed (required for `rviz2`). Install the necessary build tools:

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions cmake -y
```

### 3.2. Install Livox-SDK2
The Mid-360 requires the `Livox-SDK2` (do not use the legacy Livox-SDK).

```bash
cd ~
git clone [https://github.com/Livox-SDK/Livox-SDK2.git](https://github.com/Livox-SDK/Livox-SDK2.git)
cd Livox-SDK2
mkdir build && cd build
cmake .. && make -j
sudo make install
```

### 3.3 Install and Configure the Livox ROS2 Driver
Create your ROS2 workspace and clone the official driver:

```bash
mkdir ~/ws/src
cd ~/ws/src
git clone [https://github.com/Livox-SDK/livox_ros_driver2.git](https://github.com/Livox-SDK/livox_ros_driver2.git)
```

Before building, configure the driver to connect to your specific LiDAR IP. Open the configuration file `~/ws/src/livox_ros_driver2/config/MID360_config.json`

Change ip adresses:
- under `host_net_info` to `192.168.1.50`
- under `lidar_configs` to the ip adress you noted earlier. (See [section 2.2](#22-finding-the-lidar-ip))

Now, build the package:

```bash
source ~/ws/install/setup.bash
cd ~/ws
colcon build --packages-select livox_ros_driver2
```

**Add `source ~/ros2_ws/install/setup.bash` command to your `~/.bashrc` file to avoid running on each step. This will run the command everytime you login.**

## 4. Running & Visualization

To launch the driver and automatically open RViz2 with the correct standard `sensor_msgs/PointCloud2` format, run:

```bash
ros2 launch livox_ros_driver2 rviz_MID360_launch.py
```

## 5. Recording Data
SLAM algorithms usually require both Point Cloud and IMU data. To record this data into a ROS2 bag file keep the driver running in the first terminal and open a new terminal and create a directory for your records:

```bash
mkdir ~/bag_files
cd ~/bag_files
```

Start recording both the LiDAR and IMU topics:

```bash
ros2 bag record /livox/lidar /livox/imu -o ~/recordings/test
```