#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class ZoneMonitor(Node):
    def __init__(self):
        super().__init__('zone_monitor')
        
        self.zones = [
            {'name': 'ZONE_A', 'x1': 2, 'x2': 4, 'y1': 2, 'y2': 4, 'cx': 3, 'cy': 3},
            {'name': 'ZONE_B', 'x1': -5, 'x2': -3, 'y1': -3, 'y2': -1, 'cx': -4, 'cy': -2},
        ]
        
        self.threshold = 5.0
        self.objects = {}
        self.alerted = set()
        
        self.alert_pub = self.create_publisher(String, '/zone_alert', 10)
        self.target_pub = self.create_publisher(String, '/alert_target', 10)
        self.cmd_pub = self.create_publisher(String, '/patrol_command', 10)
        
        self.create_subscription(String, '/object_positions', self.pos_cb, 10)
        self.create_subscription(String, '/object_removed', self.rem_cb, 10)
        
        self.create_timer(0.5, self.check)
        self.get_logger().info('Zone Monitor started')

    def pos_cb(self, msg):
        try:
            p = msg.data.split(',')
            name, x, y = p[0], float(p[1]), float(p[2])
            
            zone = self.in_zone(x, y)
            if zone:
                if name not in self.objects:
                    self.objects[name] = {'zone': zone, 'time': time.time(), 'cx': zone['cx'], 'cy': zone['cy']}
                    self.get_logger().warn(f'{name} entered {zone["name"]}')
            else:
                if name in self.objects:
                    del self.objects[name]
                if name in self.alerted:
                    self.alerted.remove(name)
        except:
            pass

    def rem_cb(self, msg):
        name = msg.data
        if name in self.objects:
            del self.objects[name]
        if name in self.alerted:
            self.alerted.remove(name)
            self.get_logger().info(f'{name} removed - resuming patrol')
            m = String()
            m.data = 'resume'
            self.cmd_pub.publish(m)

    def in_zone(self, x, y):
        for z in self.zones:
            if z['x1'] <= x <= z['x2'] and z['y1'] <= y <= z['y2']:
                return z
        return None

    def check(self):
        now = time.time()
        for name, data in list(self.objects.items()):
            elapsed = now - data['time']
            if elapsed >= self.threshold and name not in self.alerted:
                self.alerted.add(name)
                self.get_logger().error(f'ALERT! {name} in {data["zone"]["name"]} for {elapsed:.0f}s')
                
                m = String()
                m.data = f'{data["cx"]},{data["cy"]}'
                self.target_pub.publish(m)

def main(args=None):
    rclpy.init(args=args)
    node = ZoneMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
