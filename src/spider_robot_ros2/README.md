# Spider Robot ROS2 Integration

This package provides ROS2 integration for the UiA Spider Robot, allowing control through Twist commands and direct servo position control.

## Features

- **Twist Command Support**: Control robot movement using `/cmd_vel` topic with standard ROS Twist messages
- **Direct Servo Control**: Control individual servos through `/spider_robot/servo_positions` topic
- **Position Feedback**: Publish current servo positions to `/spider_robot/positions`
- **Backward Compatibility**: Does not change existing CLI control methods

## Topics

### Subscribers
- `/cmd_vel` (geometry_msgs/Twist): Twist velocity commands for robot movement
- `/spider_robot/servo_positions` (std_msgs/Float64MultiArray): Direct servo position commands

### Publishers  
- `/spider_robot/positions` (std_msgs/Float64MultiArray): Current servo positions

## Usage

To run the spider robot controller:

```bash
ros2 run spider_robot_ros2 spider_robot_node
```

Or through launch file:
```bash
ros2 launch spider_robot_ros2 spider_robot.launch.py
```

## Parameters

- `config_path`: Path to the robot configuration file (default: `/home/rhino/PycharmProjects/UiASpiderRobot/config/spider.toml`)
- `simulate`: Run in simulation mode without hardware (default: false)
- `port`: Override serial port for hardware connection (default: from config)

## Integration Details

The ROS2 integration works by:
1. Creating a ROS2 node that connects to the existing spider robot controller
2. Subscribing to Twist messages and converting them to MotionCommands
3. Executing motion commands through the existing controller infrastructure
4. Supporting direct servo position control through additional methods
5. Publishing current positions for feedback

All existing CLI functionality remains unchanged.