from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='spider_robot_ros2',
            executable='spider_robot_node',
            name='spider_robot_controller',
            output='screen',
            parameters=[
                {'config_path': '/home/rhino/PycharmProjects/UiASpiderRobot/config/spider.toml'},
                {'simulate': False}
            ]
        ),
    ])