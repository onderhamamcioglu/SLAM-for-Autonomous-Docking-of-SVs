#!/usr/bin/env python3
"""Sliding-window accumulator for FAST-LIO's /cloud_registered.

Republishes the last N seconds of registered scans as a single
PointCloud2 on /cloud_window.

Usage:
    python3 cloud_window.py --window 10 --rate 2 --min-z -1.0
    # ROS-style parameters still work and take precedence:
    python3 cloud_window.py --ros-args -p window_sec:=10.0
"""
import argparse
from collections import deque

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2


class CloudWindow(Node):
    def __init__(self, cli):
        super().__init__('cloud_window')
        # CLI flags provide the defaults; --ros-args -p overrides them
        self.declare_parameter('window_sec', cli.window)
        self.declare_parameter('publish_rate', cli.rate)
        self.declare_parameter('min_z', cli.min_z)
        self.declare_parameter('max_z', cli.max_z)
        self.win_ns = int(self.get_parameter('window_sec').value * 1e9)
        self.min_z = self.get_parameter('min_z').value
        self.max_z = self.get_parameter('max_z').value
        rate = self.get_parameter('publish_rate').value

        self.buf = deque()  # (stamp_ns, PointCloud2)
        self.create_subscription(PointCloud2, '/cloud_registered', self.cb, 10)
        self.pub = self.create_publisher(PointCloud2, '/cloud_window', 1)
        self.create_timer(1.0 / rate, self.publish_window)
        self.get_logger().info(
            f'window={self.win_ns / 1e9:.1f}s rate={rate:.1f}Hz '
            f'z=[{self.min_z}, {self.max_z}]')

    def cb(self, msg):
        t = Time.from_msg(msg.header.stamp).nanoseconds
        # Bag restart / clock jump backwards -> stale buffer, drop it
        if self.buf and t < self.buf[-1][0] - int(1e9):
            self.buf.clear()
            self.get_logger().warn('Time jump detected, buffer cleared')
        self.buf.append((t, msg))

    def publish_window(self):
        if not self.buf:
            return
        newest = self.buf[-1][0]  # anchored to data time -> sim time safe
        while self.buf and self.buf[0][0] < newest - self.win_ns:
            self.buf.popleft()

        msgs = [m for _, m in self.buf]
        ref = msgs[0]
        # Identical field layout in every FAST-LIO scan -> raw byte concat,
        # no per-point parsing needed
        data = b''.join(m.data for m in msgs)
        if self.min_z > -999.0 or self.max_z < 999.0:
            data = self.z_crop(data, ref)

        out = PointCloud2()
        out.header.stamp = msgs[-1].header.stamp
        out.header.frame_id = ref.header.frame_id  # camera_init
        out.height = 1
        out.width = len(data) // ref.point_step
        out.fields = ref.fields
        out.is_bigendian = ref.is_bigendian
        out.point_step = ref.point_step
        out.row_step = len(data)
        out.is_dense = False
        out.data = data
        self.pub.publish(out)

    def z_crop(self, data, ref):
        # Vectorized z filter (kills mirror ghosts below the waterline)
        zoff = next(f.offset for f in ref.fields if f.name == 'z')
        arr = np.frombuffer(data, dtype=np.uint8).reshape(-1, ref.point_step)
        z = arr[:, zoff:zoff + 4].copy().view(np.float32).ravel()
        keep = (z > self.min_z) & (z < self.max_z)
        return arr[keep].tobytes()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--window', type=float, default=5.0,
                     help='buffer length in seconds')
    cli.add_argument('--rate', type=float, default=2.0,
                     help='output publish rate in Hz')
    cli.add_argument('--min-z', dest='min_z', type=float, default=-1000.0,
                     help='drop points below this z (world frame, m)')
    cli.add_argument('--max-z', dest='max_z', type=float, default=1000.0,
                     help='drop points above this z (world frame, m)')
    known, _ = cli.parse_known_args()  # --ros-args etc. pass through

    rclpy.init()
    try:
        rclpy.spin(CloudWindow(known))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()