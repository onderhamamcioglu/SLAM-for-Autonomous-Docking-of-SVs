# Running Fast-LIO2 on ROS 2
This part covers setting up Fast-LIO2 with ROS 2 Humble on Ubuntu 22.04.

## 1. Prerequisites

* **Ubuntu 22.04**: Native, VM, WSL via `wsl --install -d Ubuntu-22.04`, or Jetson with JetPack 6.1 flashed.
* **ROS 2** [Humble](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html): (Desktop-Full installation is recommend)

## 2. Installation

### 2.1 Dependencies
```bash
sudo apt update
sudo apt install python3-colcon-common-extensions ros-humble-pcl-ros -y
```

### 2.2 Livox-SDK2
Required for the Livox ROS 2 Driver.
```bash
git clone https://github.com/Livox-SDK/Livox-SDK2.git ~/Livox-SDK2
cd ~/Livox-SDK2 && mkdir build && cd build
cmake .. && make -j && sudo make install
```

### 2.3 Workspace Initialization
Create a dedicated ROS 2 workspace directory.
```bash
mkdir -p ~/ws/src
sudo chown -R $USER:$USER ~/ws/src
```

### 2.4 Repository Cloning
Navigate to the source directory and clone the required packages.
Currently there is a branch for using Fast-LIO2 on ROS2 in the original repository: https://github.com/hku-mars/FAST_LIO/tree/ROS2
```bash
cd ~/ws/src
git clone https://github.com/Livox-SDK/livox_ros_driver2.git
git clone -b ROS2 https://github.com/hku-mars/FAST_LIO.git --recursive
```

### 2.5 Build
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
