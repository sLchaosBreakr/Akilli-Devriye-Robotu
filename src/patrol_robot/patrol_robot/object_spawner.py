#!/usr/bin/env python3
"""
Object Spawner - Kontrollü nesne oluşturucu
- Aynı anda sadece 1 nesne
- Bölgeler sırayla (arka arkaya aynı bölge olmaz)
- Robot devriyeye dönene kadar yeni nesne yok
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess
import random
import time

class ObjectSpawner(Node):
    def __init__(self):
        super().__init__('object_spawner')
        
        # İki yasak bölge
        self.zones = [
            {'name': 'ZONE_A', 'x1': 2.2, 'x2': 3.8, 'y1': 2.2, 'y2': 3.8},
            {'name': 'ZONE_B', 'x1': -4.8, 'x2': -3.2, 'y1': -2.8, 'y2': -1.2},
        ]
        
        self.last_zone_index = -1  # Son kullanılan bölge
        self.current_object = None  # Şu anki aktif nesne
        self.counter = 0
        self.can_spawn = True  # Spawn yapılabilir mi?
        self.spawn_delay = 25.0  # Spawn arası bekleme (saniye)
        self.last_spawn_time = 0
        
        # Publishers
        self.pos_pub = self.create_publisher(String, '/object_positions', 10)
        self.rem_pub = self.create_publisher(String, '/object_removed', 10)
        
        # Subscribers
        self.create_subscription(String, '/patrol_status', self.status_cb, 10)
        
        # Timers
        self.create_timer(1.0, self.publish_pos)
        self.create_timer(2.0, self.check_spawn)
        self.create_timer(5.0, self.cleanup)
        
        self.get_logger().info('Object Spawner started')
        self.get_logger().info('Spawn delay: 25s, One object at a time')

    def status_cb(self, msg):
        """Robot durumunu izle - PATROL moduna geçince spawn'a izin ver"""
        if 'PATROL' in msg.data and self.current_object is None:
            self.can_spawn = True

    def check_spawn(self):
        """Kontrollü spawn - koşullar uygunsa spawn et"""
        now = time.time()
        
        # Koşullar:
        # 1. Aktif nesne olmamalı
        # 2. Spawn yapılabilir olmalı
        # 3. Son spawn'dan yeterli süre geçmiş olmalı
        if (self.current_object is None and 
            self.can_spawn and 
            now - self.last_spawn_time > self.spawn_delay):
            
            self.spawn_object()
            self.last_spawn_time = now
            self.can_spawn = False  # Robot devriyeye dönene kadar spawn yok

    def get_next_zone(self):
        """Sıradaki bölgeyi seç (aynı bölge arka arkaya olmaz)"""
        if self.last_zone_index == -1:
            # İlk spawn - rastgele seç
            idx = random.randint(0, len(self.zones) - 1)
        else:
            # Diğer bölgeyi seç
            idx = 1 - self.last_zone_index
        
        self.last_zone_index = idx
        return self.zones[idx]

    def spawn_object(self):
        """Nesne spawn et"""
        zone = self.get_next_zone()
        x = random.uniform(zone['x1'], zone['x2'])
        y = random.uniform(zone['y1'], zone['y2'])
        
        self.counter += 1
        name = f'intruder_{self.counter}'
        
        sdf = f'''<?xml version="1.0"?>
<sdf version="1.8">
  <model name="{name}">
    <static>true</static>
    <link name="link">
      <visual name="v">
        <geometry><box><size>0.3 0.3 0.5</size></box></geometry>
        <material>
          <ambient>1 0.4 0 1</ambient>
          <diffuse>1 0.5 0 1</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>'''
        
        path = f'/tmp/{name}.sdf'
        with open(path, 'w') as f:
            f.write(sdf)
        
        try:
            cmd = ['gz', 'service', '-s', '/world/patrol_world/create',
                   '--reqtype', 'gz.msgs.EntityFactory',
                   '--reptype', 'gz.msgs.Boolean',
                   '--timeout', '2000',
                   '--req', f'sdf_filename: "{path}", pose: {{position: {{x: {x}, y: {y}, z: 0.25}}}}']
            subprocess.run(cmd, capture_output=True, timeout=5)
            
            self.current_object = {
                'name': name, 
                'x': x, 
                'y': y, 
                'time': time.time(),
                'zone': zone['name']
            }
            self.get_logger().warn(f'=== INTRUDER SPAWNED ===')
            self.get_logger().warn(f'Object: {name}')
            self.get_logger().warn(f'Zone: {zone["name"]}')
            self.get_logger().warn(f'Position: ({x:.1f}, {y:.1f})')
            
        except Exception as e:
            self.get_logger().error(f'Spawn failed: {e}')

    def publish_pos(self):
        """Aktif nesnenin pozisyonunu yayınla"""
        if self.current_object:
            m = String()
            m.data = f'{self.current_object["name"]},{self.current_object["x"]},{self.current_object["y"]}'
            self.pos_pub.publish(m)

    def cleanup(self):
        """30 saniye sonra nesneyi sil"""
        if self.current_object:
            elapsed = time.time() - self.current_object['time']
            if elapsed > 30:
                self.remove_object()

    def remove_object(self):
        """Aktif nesneyi sil"""
        if not self.current_object:
            return
            
        name = self.current_object['name']
        
        try:
            cmd = ['gz', 'service', '-s', '/world/patrol_world/remove',
                   '--reqtype', 'gz.msgs.Entity',
                   '--reptype', 'gz.msgs.Boolean',
                   '--timeout', '2000',
                   '--req', f'name: "{name}", type: MODEL']
            subprocess.run(cmd, capture_output=True, timeout=5)
        except:
            pass
        
        # Bildir
        m = String()
        m.data = name
        self.rem_pub.publish(m)
        
        self.get_logger().info(f'Object removed: {name}')
        self.current_object = None
        # Robot PATROL moduna geçince can_spawn True olacak

def main(args=None):
    rclpy.init(args=args)
    node = ObjectSpawner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
