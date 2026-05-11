#!/usr/bin/env python3
"""
Navigation Controller Node - Navigasyon Kontrol Düğümü
Robot hareketlerini koordine eder.
Odometry verisini işler ve durum bilgisi sağlar.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import math


class NavigationController(Node):
    def __init__(self):
        super().__init__('navigation_controller')
        
        # Robot durumu
        self.robot_pose = {
            'x': 0.0, 'y': 0.0, 'yaw': 0.0
        }
        self.robot_velocity = {
            'linear': 0.0, 'angular': 0.0
        }
        
        # Navigasyon durumu
        self.navigation_active = False
        self.current_goal = None
        
        # Parametreler
        self.goal_tolerance = 0.3
        self.max_linear_vel = 0.3
        self.max_angular_vel = 1.0
        
        # Publisher'lar
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.nav_status_pub = self.create_publisher(String, '/nav_status', 10)
        self.robot_pose_pub = self.create_publisher(String, '/robot_pose', 10)
        
        # Subscriber'lar
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        
        self.nav_goal_sub = self.create_subscription(
            String, '/nav_goal', self.nav_goal_callback, 10)
        
        # Kontrol döngüsü (20 Hz)
        self.timer = self.create_timer(0.05, self.control_loop)
        
        # Pose yayınlama timer (5 Hz)
        self.pose_timer = self.create_timer(0.2, self.publish_pose)
        
        self.get_logger().info('Navigation Controller başlatıldı')
    
    def odom_callback(self, msg):
        """Odometry verisini işle"""
        self.robot_pose['x'] = msg.pose.pose.position.x
        self.robot_pose['y'] = msg.pose.pose.position.y
        
        # Quaternion -> Yaw dönüşümü
        orientation = msg.pose.pose.orientation
        siny_cosp = 2.0 * (orientation.w * orientation.z + 
                          orientation.x * orientation.y)
        cosy_cosp = 1.0 - 2.0 * (orientation.y ** 2 + orientation.z ** 2)
        self.robot_pose['yaw'] = math.atan2(siny_cosp, cosy_cosp)
        
        # Hız bilgisi
        self.robot_velocity['linear'] = msg.twist.twist.linear.x
        self.robot_velocity['angular'] = msg.twist.twist.angular.z
    
    def nav_goal_callback(self, msg):
        """Navigasyon hedefi al"""
        try:
            # Format: "x,y"
            parts = msg.data.split(',')
            x = float(parts[0])
            y = float(parts[1])
            
            self.current_goal = {'x': x, 'y': y}
            self.navigation_active = True
            
            self.get_logger().info(f'Yeni hedef: ({x:.2f}, {y:.2f})')
        except (ValueError, IndexError) as e:
            self.get_logger().error(f'Hedef parse hatası: {e}')
    
    def control_loop(self):
        """Navigasyon kontrol döngüsü"""
        if not self.navigation_active or self.current_goal is None:
            return
        
        # Hedefe mesafe
        dx = self.current_goal['x'] - self.robot_pose['x']
        dy = self.current_goal['y'] - self.robot_pose['y']
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Hedefe ulaşıldı mı?
        if distance < self.goal_tolerance:
            self.navigation_active = False
            self.stop_robot()
            self.publish_nav_status('REACHED')
            self.get_logger().info('Hedefe ulaşıldı!')
            return
        
        # Hedef açısı
        target_yaw = math.atan2(dy, dx)
        yaw_error = self.normalize_angle(target_yaw - self.robot_pose['yaw'])
        
        cmd = Twist()
        
        # Önce dön, sonra ilerle
        if abs(yaw_error) > 0.3:
            cmd.angular.z = self.clamp(
                yaw_error * 2.0,
                -self.max_angular_vel,
                self.max_angular_vel
            )
        else:
            cmd.linear.x = self.clamp(
                distance * 0.5,
                0.0,
                self.max_linear_vel
            )
            cmd.angular.z = self.clamp(
                yaw_error * 1.0,
                -self.max_angular_vel * 0.5,
                self.max_angular_vel * 0.5
            )
        
        self.cmd_vel_pub.publish(cmd)
        self.publish_nav_status('NAVIGATING')
    
    def stop_robot(self):
        """Robotu durdur"""
        cmd = Twist()
        self.cmd_vel_pub.publish(cmd)
    
    def publish_nav_status(self, status):
        """Navigasyon durumunu yayınla"""
        msg = String()
        if self.current_goal:
            dx = self.current_goal['x'] - self.robot_pose['x']
            dy = self.current_goal['y'] - self.robot_pose['y']
            distance = math.sqrt(dx * dx + dy * dy)
            msg.data = f"{status}|{distance:.2f}m"
        else:
            msg.data = f"{status}|idle"
        self.nav_status_pub.publish(msg)
    
    def publish_pose(self):
        """Robot pozisyonunu yayınla"""
        msg = String()
        msg.data = (f"{self.robot_pose['x']:.2f},"
                   f"{self.robot_pose['y']:.2f},"
                   f"{math.degrees(self.robot_pose['yaw']):.1f}")
        self.robot_pose_pub.publish(msg)
    
    @staticmethod
    def normalize_angle(angle):
        """Açıyı [-pi, pi] aralığına normalize et"""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle
    
    @staticmethod
    def clamp(value, min_val, max_val):
        """Değeri sınırla"""
        return max(min_val, min(value, max_val))


def main(args=None):
    rclpy.init(args=args)
    node = NavigationController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Navigation Controller kapatılıyor...')
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
