# SLAM-for-Autonomous-Docking-of-SVs
Simultaneous Localization and Mapping for Autonomous Docking of Surface Vessels

## Introduction
This repository documents process of implementing SLAM for Autonomous Docking of SVs. The prototype vessel used in this project utilizes a `Livox MID-360 LiDAR` and a `Jetson Orin Nano Super DevKit` for performing SLAM.

## Progress and Milestones

### Prototype Vessel
- [x] Research existing ASV platforms
- [x] Analyze common electronics and hardware architectures
- [x] Evaluate build materials for 3D-printed vessels
- [x] Finalize the list of materials
- [x] Create the initial 3D CAD design
- [x] Verify component fitment within the 3D CAD design
- [x] Finalize the 3D CAD design
- [x] Print the finalized 3D CAD design
- [x] Conduct physical test fitting and subassembly
- [x] Perform water ingress and leakage testing
- [x] Complete final prototype assembly  

### SLAM Implementation
- [x] Define use cases and system constraints
- [x] Evaluate SLAM approaches based on hardware requirements
- [x] Review 3D LiDAR SLAM methodologies
- [x] Analyze 3D LiDAR SLAM algorithms suitable for ASVs
- [x] Compile a list of candidate algorithms
- [x] Select algorithm(s) for initial trial
- [x] Identify maritime datasets for testing and validation
- [x] Test and evaluate the selected algorithm(s)
- [x] Test the algorithm using data collected by the prototype vessel
- [x] Implement algorithm refinements and optimizations (if necessary)
- [ ] Conduct initial real-world field testing of the algorithm
- [ ] Implement final algorithm refinements and optimizations (if necessary)

## Documentation
The `doc/` directory contains step-by-step guides for setting up the hardware and software stack used in this project:

* [`LivoxMid360.md`](doc/LivoxMid360.md): Instructions for setting up, configuring, and interfacing the Livox MID-360 LiDAR sensor within ROS 2 environment (Livox-SDK2, `livox_ros_driver2`, network configuration). Prerequisite for the other guides.

* [`FastLIO2.md`](doc/FastLIO2.md): Complete Fast-LIO2 guide — installing and building it with ROS 2 Humble on Ubuntu 22.04 (for both PC and Jetson), running it in real time with the Livox Mid-360 LiDAR or on recorded bag files, live mapping, saving the generated map, and troubleshooting.

* [`SeaGrant.md`](doc/SeaGrant.md): Documentation on testing Fast-LIO2 for maritime SLAM using the MIT Sea Grant Marine Perception Dataset, including steps for dataset conversion (ROS 1 to ROS 2), mapping configuration, and playback.

* [`CostMap.md`](doc/CostMap.md): Guide for generating a live 2D costmap from Fast-LIO2 output using Nav2's `nav2_costmap_2d` and the Spatio-Temporal Voxel Layer — installation, configuration, running the full pipeline on recorded data, and troubleshooting.
