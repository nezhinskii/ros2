from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('artist_robot')
    urdf_file = os.path.join(pkg_share, 'urdf', 'artist_robot.urdf')
    world_file = os.path.join(pkg_share, 'worlds', 'simple_world.world')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so', world_file],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'publish_frequency': 100.0, 'use_sim_time': True}]
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        name='controller_manager',
        parameters=[os.path.join(pkg_share, 'config', 'controllers.yaml')],
        output='screen',
        condition=IfCondition(LaunchConfiguration('spawn', default='true')),
        # parameters=[{'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'artist_robot', '-file', urdf_file, '-x', '0', '-y', '0', '-z', '0.1'],
        output='screen',
        condition=IfCondition(LaunchConfiguration('spawn', default='true')),
        additional_env={'GAZEBO_MODEL_PATH': os.path.join(pkg_share, 'models')},
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('spawn', default_value='true', description='Spawn the robot in Gazebo'),
        gazebo,
        robot_state_publisher,
        controller_manager,
        spawn_entity,
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', os.path.join(pkg_share, 'config', 'artist_robot.rviz')],
            output='screen',
            parameters=[{'use_sim_time': True}]
        )
    ])