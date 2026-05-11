from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'patrol_robot'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Launch dosyaları
        (os.path.join('share', package_name, 'launch'), 
            glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        # World dosyaları
        (os.path.join('share', package_name, 'worlds'), 
            glob(os.path.join('worlds', '*.sdf'))),
        # Config dosyaları
        (os.path.join('share', package_name, 'config'), 
            glob(os.path.join('config', '*.yaml'))),
        # Model dosyaları
        (os.path.join('share', package_name, 'models', 'restricted_zone'),
            glob(os.path.join('models', 'restricted_zone', '*'))),
        (os.path.join('share', package_name, 'models', 'intruder_object'),
            glob(os.path.join('models', 'intruder_object', '*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@university.edu',
    description='Smart Patrol Robot Simulation',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'patrol_node = patrol_robot.patrol_node:main',
            'object_spawner = patrol_robot.object_spawner:main',
            'zone_monitor = patrol_robot.zone_monitor:main',
            'alert_manager = patrol_robot.alert_manager:main',
            'navigation_controller = patrol_robot.navigation_controller:main',
        ],
    },
)
