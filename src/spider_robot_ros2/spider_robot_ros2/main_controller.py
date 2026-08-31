from __future__ import annotations

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
from spider_robot.controller import SpiderController, MotionCommand
from spider_robot.config import load_config
from spider_robot.hardware import LewanSoulBus, SimulationBus
import time

class SpiderRobotControllerNode(Node):
    """ROS2 node for controlling the spider robot with Twist commands and servo positions."""

    def __init__(self):
        super().__init__('spider_robot_controller')
        
        # Parameters
        self.declare_parameter('config_path', '/home/rhino/PycharmProjects/UiASpiderRobot/config/spider.toml')
        self.declare_parameter('simulate', False)
        self.declare_parameter('port', '')
        
        config_path = self.get_parameter('config_path').get_parameter_value().string_value
        simulate = self.get_parameter('simulate').get_parameter_value().bool_value
        port = self.get_parameter('port').get_parameter_value().string_value
        
        # Load configuration
        try:
            from spider_robot.config import load_config
            config = load_config(config_path)
            if port:
                from dataclasses import replace
                config = replace(config, bus=replace(config.bus, port=port))
                
            # Initialize hardware bus
            if simulate:
                self.bus = SimulationBus()
            else:
                self.bus = LewanSoulBus(config.bus)
                
            # Create spider controller
            self.controller = SpiderController(
                config,
                self.bus,
                sleep=(lambda _seconds: None) if simulate else time.sleep,
                gait_type="alternating_tetrapod"
            )
            
            self.get_logger().info('Spider robot controller initialized successfully')
            
        except Exception as e:
            self.get_logger().error(f'Failed to initialize spider robot controller: {e}')
            raise
        
        # Create subscribers
        self.twist_subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.twist_callback,
            10
        )
        
        self.servo_subscription = self.create_subscription(
            Float64MultiArray,
            '/spider_robot/servo_positions',
            self.servo_callback,
            10
        )
        
        # Create publisher for positions
        self.position_publisher = self.create_publisher(
            Float64MultiArray,
            '/spider_robot/positions',
            10
        )
        
        # Timer to publish current positions
        self.timer = self.create_timer(1.0, self.publish_positions)
        
        self.get_logger().info('ROS2 nodes initialized')

    def twist_callback(self, msg: Twist):
        """Handle incoming Twist messages and convert to MotionCommand."""
        # Convert Twist message to MotionCommand (ROS coordinate system)
        # linear_x in ROS is forward/backward
        # linear_y in ROS is left/right  
        # angular_z in ROS is yaw (turning)
        command = MotionCommand(
            linear_x=msg.linear.x,
            linear_y=msg.linear.y,
            angular_z=msg.angular.z
        )
        
        # Execute the motion command through the controller
        try:
            self.controller.walk(command, cycles=0)  # 0 means continuous until stopped
            self.get_logger().debug(f'Executed motion command: {command}')
        except Exception as e:
            self.get_logger().error(f'Error executing motion command: {e}')

    def servo_callback(self, msg: Float64MultiArray):
        """Handle incoming servo position commands."""
        # This is a simplified implementation - you would need to parse
        # the array according to your servo layout
        self.get_logger().info(f'Received servo positions message with {len(msg.data)} values')
        
        # Example implementation for setting individual servos
        # In practice, this would require mapping the array elements to specific joints
        try:
            # For now, just log it - actual implementation would need detailed parsing
            self.get_logger().info(f'Processing servo positions: {msg.data}')
            
            # Stop current movement when setting direct servo positions
            self.controller.stop_movement()
            
        except Exception as e:
            self.get_logger().error(f'Error processing servo positions: {e}')

    def publish_positions(self):
        """Publish current servo positions."""
        try:
            positions = self.controller.read_positions()
            msg = Float64MultiArray()
            
            # Flatten all positions into a single array
            position_list = []
            for leg_name, pos in positions.items():
                position_list.extend([float(pos.coxa), float(pos.femur), float(pos.tibia)])
                
            msg.data = position_list
            self.position_publisher.publish(msg)
            
        except Exception as e:
            self.get_logger().error(f'Error publishing positions: {e}')

    def destroy_node(self):
        """Clean up resources."""
        self.get_logger().info('Shutting down spider robot controller')
        self.controller.stop()
        self.bus.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    
    node = SpiderRobotControllerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()