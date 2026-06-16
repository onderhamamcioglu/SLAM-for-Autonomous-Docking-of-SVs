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
- [ ] Perform water ingress and leakage testing
- [ ] Complete final prototype assembly  

### SLAM Implementation
- [x] Define use cases and system constraints
- [x] Evaluate SLAM approaches based on hardware requirements
- [x] Review 3D LiDAR SLAM methodologies
- [x] Analyze 3D LiDAR SLAM algorithms suitable for ASVs
- [x] Compile a list of candidate algorithms
- [x] Select the initial algorithm for implementation
- [x] Identify maritime datasets for testing and validation
- [x] Test and evaluate the selected algorithm
- [ ] Test the algorithm using data collected by the prototype vessel
- [ ] Implement algorithm refinements and optimizations (if necessary)
- [ ] Conduct initial real-world field testing of the algorithm
- [ ] Implement final algorithm refinements and optimizations (if necessary)

## Documentation
The `doc/` directory contains step-by-step guides for setting up the hardware and software stack used in this project:

* [`LivoxMid360-ROS2.md`](doc/LivoxMid360-ROS2.md): Instructions for setting up, configuring, and interfacing the Livox MID-360 LiDAR sensor within ROS 2 environment.

* [`FastLIO2-ROS2.md`](doc/FastLIO2-ROS2.md): Guide for installing and configuring the Fast-LIO2 mapping algorithm with ROS 2 Humble on Ubuntu 22.04 (for both PC and Jetson).

* [`Testing-FastLIO2.md`](doc/Testing-FastLIO2.md): Documentation on testing Fast-LIO2 for maritime SLAM using the MIT Sea Grant Marine Perception Dataset, including steps for dataset conversion (ROS 1 to ROS 2) and mapping configuration. 
