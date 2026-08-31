from setuptools import setup, find_packages

package_name = 'spider_robot_ros2'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    py_modules=[],
    install_requires=[
        'setuptools',
        'rclpy',
        'geometry_msgs',
        'std_msgs',
        'spider-robot @ file:///${PROJECT_ROOT}/src/spider_robot',
    ],
    zip_safe=True,
    maintainer='UiA Robotics Team',
    maintainer_email='robotics@uia.no',
    description='ROS2 integration for UiA Spider Robot',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'spider_robot_node = spider_robot_ros2.main_controller:main',
        ],
    },
)