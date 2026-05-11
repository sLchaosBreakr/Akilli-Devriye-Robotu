#!/usr/bin/env python3
"""
Alert Manager Node - Alarm Yönetim Düğümü
Sistem genelindeki alarmları yönetir ve koordine eder.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class AlertManager(Node):
    def __init__(self):
        super().__init__('alert_manager')
        
        # Alarm durumu
        self.alert_active = False
        self.current_alert = None
        
        # Alarm geçmişi
        self.alert_history = []
        
        # Publisher'lar
        self.patrol_command_pub = self.create_publisher(
            String, '/patrol_command', 10)
        self.system_status_pub = self.create_publisher(
            String, '/system_status', 10)
        
        # Subscriber'lar
        self.zone_alert_sub = self.create_subscription(
            String, '/zone_alert', self.zone_alert_callback, 10)
        
        self.patrol_status_sub = self.create_subscription(
            String, '/patrol_status', self.patrol_status_callback, 10)
        
        self.object_removed_sub = self.create_subscription(
            String, '/object_removed', self.object_removed_callback, 10)
        
        # Durum yayınlama timer
        self.status_timer = self.create_timer(2.0, self.publish_system_status)
        
        self.get_logger().info('Alert Manager başlatıldı')
    
    def zone_alert_callback(self, msg):
        """Bölge alarm mesajını işle"""
        # Format: "VIOLATION|object_name|zone_name"
        try:
            parts = msg.data.split('|')
            if parts[0] == 'VIOLATION':
                obj_name = parts[1]
                zone_name = parts[2]
                
                self.handle_alert(obj_name, zone_name)
        except (IndexError, ValueError) as e:
            self.get_logger().error(f'Alert parse hatası: {e}')
    
    def handle_alert(self, obj_name, zone_name):
        """Alarm durumunu yönet"""
        if self.alert_active and self.current_alert:
            if self.current_alert['object'] == obj_name:
                return  # Zaten bu alarm aktif
        
        self.alert_active = True
        self.current_alert = {
            'object': obj_name,
            'zone': zone_name,
            'handled': False
        }
        
        # Terminale uyarı yazdır
        self.get_logger().error('=' * 60)
        self.get_logger().error('    ALERT: Restricted zone violation detected.')
        self.get_logger().error(f'    Nesne: {obj_name}')
        self.get_logger().error(f'    Bölge: {zone_name}')
        self.get_logger().error('    Robot araştırmaya gidiyor...')
        self.get_logger().error('=' * 60)
        
        # Devriyeyi durdur
        stop_msg = String()
        stop_msg.data = 'stop'
        self.patrol_command_pub.publish(stop_msg)
        
        # Geçmişe ekle
        self.alert_history.append({
            'object': obj_name,
            'zone': zone_name,
            'time': self.get_clock().now().to_msg()
        })
    
    def patrol_status_callback(self, msg):
        """Devriye durumunu izle"""
        # Format: "STATUS|waypoint|x,y"
        pass  # Gerekirse loglama yapılabilir
    
    def object_removed_callback(self, msg):
        """Nesne kaldırıldığında"""
        obj_name = msg.data
        
        if self.current_alert and self.current_alert['object'] == obj_name:
            self.get_logger().info('=' * 60)
            self.get_logger().info('    ALARM SONLANDIRILDI')
            self.get_logger().info(f'    Nesne kaldırıldı: {obj_name}')
            self.get_logger().info('    Devriye devam ediyor...')
            self.get_logger().info('=' * 60)
            
            self.alert_active = False
            self.current_alert = None
            
            # Devriyeye devam et
            resume_msg = String()
            resume_msg.data = 'resume'
            self.patrol_command_pub.publish(resume_msg)
    
    def publish_system_status(self):
        """Sistem durumunu yayınla"""
        msg = String()
        if self.alert_active:
            msg.data = f"ALERT|{self.current_alert['zone']}|{self.current_alert['object']}"
        else:
            msg.data = f"NORMAL|patrol_active|alerts:{len(self.alert_history)}"
        
        self.system_status_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = AlertManager()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Alert Manager kapatılıyor...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
