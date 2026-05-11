#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import math
import time

class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        
        self.waypoints = [(0,0), (4,0), (4,4), (-4,4), (-4,-2), (0,-2)]
        self.wp_idx = 0
        self.tolerance = 0.4
        
        self.speed_normal = 0.3
        self.speed_fast = 0.6
        self.speed = self.speed_normal
        
        self.x = self.y = self.yaw = 0.0
        self.mode = 'PATROL'
        self.target = None
        self.wait_until = None
        
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/patrol_status', 10)
        
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.create_subscription(String, '/patrol_command', self.cmd_cb, 10)
        self.create_subscription(String, '/alert_target', self.alert_cb, 10)
        
        self.create_timer(0.1, self.update)
        self.get_logger().info('Patrol Node started')

    def odom_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))

    def cmd_cb(self, msg):
        if msg.data == 'resume':
            self.mode = 'PATROL'
            self.speed = self.speed_normal
            self.target = None
        elif msg.data == 'stop':
            self.mode = 'STOP'
            self.send_cmd(0, 0)

    def alert_cb(self, msg):
        try:
            p = msg.data.split(',')
            self.target = (float(p[0]), float(p[1]))
            self.mode = 'EMERGENCY'
            self.speed = self.speed_fast
            self.get_logger().warn(f'EMERGENCY! Target: {self.target}')
        except:
            pass

    def update(self):
        st = String()
        st.data = f'{self.mode}|{self.x:.1f},{self.y:.1f}'
        self.status_pub.publish(st)
        
        if self.mode == 'PATROL':
            tx, ty = self.waypoints[self.wp_idx]
            if self.dist(tx, ty) < self.tolerance:
                self.wp_idx = (self.wp_idx + 1) % len(self.waypoints)
                self.get_logger().info(f'WP{self.wp_idx} reached')
            else:
                self.go_to(tx, ty)
                
        elif self.mode == 'EMERGENCY' and self.target:
            if self.dist(*self.target) < self.tolerance:
                self.get_logger().warn('Zone reached - investigating')
                self.mode = 'WAIT'
                self.wait_until = time.time() + 3
                self.send_cmd(0, 0)
            else:
                self.go_to(*self.target)
                
        elif self.mode == 'WAIT':
            self.send_cmd(0, 0)
            if time.time() > self.wait_until:
                self.mode = 'PATROL'
                self.speed = self.speed_normal
                self.target = None
                self.get_logger().info('Resuming patrol')
                
        elif self.mode == 'STOP':
            self.send_cmd(0, 0)

    def go_to(self, tx, ty):
        dx, dy = tx - self.x, ty - self.y
        angle = math.atan2(dy, dx)
        err = angle - self.yaw
        while err > math.pi: err -= 2*math.pi
        while err < -math.pi: err += 2*math.pi
        
        if abs(err) > 0.3:
            self.send_cmd(0, 0.8 if err > 0 else -0.8)
        else:
            self.send_cmd(self.speed, err * 0.5)

    def send_cmd(self, v, w):
        cmd = Twist()
        cmd.linear.x = float(v)
        cmd.angular.z = float(w)
        self.cmd_pub.publish(cmd)

    def dist(self, x, y):
        return math.sqrt((x-self.x)**2 + (y-self.y)**2)

def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.send_cmd(0, 0)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
