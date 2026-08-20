#!/usr/bin/env python3
"""
Parameters:
    --window / window_sec  : sliding buffer length in seconds(default 5.0)
    --rate   / publish_rate: rate of republishing, in Hz (default 2.0)
    --min-z  / min_z       : discard points below this height in the world frame, in metres
    --max-z  / max_z       : discard points above this height in the world frame, in metres
Usage:
    python3 cloud_window.py --window 10 --rate 2 --min-z -1.0
    or:
    python3 cloud_window.py --ros-args -p window_sec:=10.0
"""
import argparse
from collections import deque
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2, PointField

OUT_STEP = 16

def repack_xyzi(data, point_step, xoff, ioff, min_z, max_z):
    arr = np.frombuffer(data, dtype=np.uint8).reshape(-1, point_step)
    n = arr.shape[0]
    if n == 0:
        return b''
    out = np.empty((n, 4), dtype=np.float32)
    out[:, :3] = arr[:, xoff:xoff + 12].copy().view(np.float32) \
                    .reshape(-1, 3)
    if ioff >= 0:
        out[:, 3] = arr[:, ioff:ioff + 4].copy().view(np.float32).ravel()
    else:
        out[:, 3] = 0.0
    if min_z > -999.0 or max_z < 999.0:
        keep = (out[:, 2] > min_z) & (out[:, 2] < max_z)
        out = out[keep]
    return out.tobytes()

class CloudWindow(Node):
    def __init__(self, cli):
        super().__init__('cloud_window')
        self.declare_parameter('window_sec', cli.window)
        self.declare_parameter('publish_rate', cli.rate)
        self.declare_parameter('min_z', cli.min_z)
        self.declare_parameter('max_z', cli.max_z)
        self.win_ns = int(self.get_parameter('window_sec').value * 1e9)
        self.min_z = self.get_parameter('min_z').value
        self.max_z = self.get_parameter('max_z').value
        rate = self.get_parameter('publish_rate').value

        self.buf = deque()
        self.frame = 'camera_init'
        self.fields = [
            PointField(name=n, offset=o, datatype=PointField.FLOAT32,
                       count=1)
            for n, o in (('x', 0), ('y', 4), ('z', 8), ('intensity', 12))]

        self.create_subscription(PointCloud2, '/cloud_registered', self.cb, 10)
        self.pub = self.create_publisher(PointCloud2, '/cloud_window', 1)
        self.create_timer(1.0 / rate, self.publish_window)
        self.get_logger().info(
            f'window={self.win_ns / 1e9:.1f}s rate={rate:.1f}Hz '
            f'z=[{self.min_z}, {self.max_z}] output=XYZI {OUT_STEP}B/pt')

    def cb(self, msg):
        t = Time.from_msg(msg.header.stamp).nanoseconds
        if self.buf and t < self.buf[-1][0] - int(1e9):
            self.buf.clear()
            self.get_logger().warn('Time jump detected, buffer cleared')

        xoff = next(f.offset for f in msg.fields if f.name == 'x')
        ioff = next((f.offset for f in msg.fields
                     if f.name == 'intensity'), -1)
        self.frame = msg.header.frame_id
        self.buf.append((t, msg.header.stamp,
                         repack_xyzi(msg.data, msg.point_step, xoff, ioff,
                                     self.min_z, self.max_z)))

    def publish_window(self):
        if not self.buf:
            return
        newest = self.buf[-1][0]
        while self.buf and self.buf[0][0] < newest - self.win_ns:
            self.buf.popleft()

        data = b''.join(b for _, _, b in self.buf)

        out = PointCloud2()
        out.header.stamp = self.buf[-1][1]
        out.header.frame_id = self.frame
        out.height = 1
        out.width = len(data) // OUT_STEP
        out.fields = self.fields
        out.is_bigendian = False
        out.point_step = OUT_STEP
        out.row_step = len(data)
        out.is_dense = False
        out.data = data
        self.pub.publish(out)

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
    known, _ = cli.parse_known_args()

    rclpy.init()
    try:
        rclpy.spin(CloudWindow(known))
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()