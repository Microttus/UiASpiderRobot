from __future__ import annotations

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
from spider_robot.controller import SpiderController, MotionCommand

class SpiderRobotTwistController(Node):
    """ROS2 node for controlling the spider robot with Twist commands."""

    def __init__(self):
        super().__init__('spider_robot_twist_controller')
        
        # Create a subscriber for Twist messages
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.twist_callback,
            10
        )
        
        # Create a publisher for current positions (optional)
        self.position_publisher = self.create_publisher(
            Float64MultiArray,
            '/spider_robot/positions',
            10
        )
        
        # Initialize controller reference - this will be set by the main node
        self.controller = None

    def twist_callback(self, msg: Twist):
        """Handle incoming Twist messages and convert to MotionCommand."""
        if self.controller is None:
            self.get_logger().warn('Controller not initialized yet')
            return
            
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
        except Exception as e:
            self.get_logger().error(f'Error executing motion command: {e}')

    def set_controller(self, controller: SpiderController):
        """Set the reference to the spider robot controller."""
        self.controller = controller

class SpiderRobotServoController(Node):
    """ROS2 node for controlling individual servo positions."""

    def __init__(self):
        super().__init__('spider_robot_servo_controller')
        
        # Create a subscriber for direct servo control
        self.subscription = self.create_subscription(
            Float64MultiArray,
            '/spider_robot/servo_positions',
            self.servo_callback,
            10
        )
        
        # Initialize controller reference - this will be set by the main node
        self.controller = None

    def servo_callback(self, msg: Float64MultiArray):
        """Handle incoming servo position commands."""
        if self.controller is None:
            self.get_logger().warn('Controller not initialized yet')
            return
            
        # This would require more complex implementation to set individual servos
        # For now, we'll just log the message
        self.get_logger().info(f'Received servo positions: {msg.data}')

    def set_controller(self, controller: SpiderController):
        """Set the reference to the spider robot controller."""
        self.controller = controller

def main(args=None):
    rclpy.init(args=args)
    
    # Create nodes
    twist_controller = SpiderRobotTwistController()
    servo_controller = SpiderRobotServoController()
    
    # TODO: Initialize and connect to your actual spider robot controller here
    
    # Spin both nodes
    rclpy.spin(twist_controller)
    rclpy.spin(servo_controller)
    
    # Shutdown
    twist_controller.destroy_node()
    servo_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()