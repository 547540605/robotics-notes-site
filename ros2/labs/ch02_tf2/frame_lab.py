#!/usr/bin/env python3
"""Craig chapter 2: verify point, vector and inverse transforms with ROS 2 tf2."""

import argparse
import math
import sys
import time

import rclpy
from geometry_msgs.msg import PointStamped, TransformStamped, Vector3Stamped
from rclpy.node import Node
from rclpy.time import Time
from tf2_geometry_msgs import do_transform_point, do_transform_vector3
from tf2_ros import Buffer, StaticTransformBroadcaster, TransformException, TransformListener


def make_static_transform(node, parent, child, xyz, quaternion):
    transform = TransformStamped()
    transform.header.stamp = node.get_clock().now().to_msg()
    transform.header.frame_id = parent
    transform.child_frame_id = child
    transform.transform.translation.x = xyz[0]
    transform.transform.translation.y = xyz[1]
    transform.transform.translation.z = xyz[2]
    transform.transform.rotation.x = quaternion[0]
    transform.transform.rotation.y = quaternion[1]
    transform.transform.rotation.z = quaternion[2]
    transform.transform.rotation.w = quaternion[3]
    return transform


def coordinates(message):
    value = message.point if hasattr(message, "point") else message.vector
    return (value.x, value.y, value.z)


def check(label, actual, expected):
    if not all(math.isclose(a, e, abs_tol=1e-6) for a, e in zip(actual, expected)):
        raise AssertionError(f"{label}: got {actual}, expected {expected}")
    print(f"PASS {label}: {tuple(round(value, 6) for value in actual)}")


class FrameLab(Node):
    def __init__(self):
        super().__init__("craig_ch02_frame_lab")
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.broadcaster = StaticTransformBroadcaster(self)

        half_turn = math.sqrt(0.5)
        self.broadcaster.sendTransform(
            [
                make_static_transform(
                    self, "base_link", "camera", (1.0, 2.0, 0.0),
                    (0.0, 0.0, half_turn, half_turn),
                ),
                make_static_transform(
                    self, "camera", "target", (0.5, 0.0, 0.0),
                    (0.0, 0.0, 0.0, 1.0),
                ),
            ]
        )

    def lookup(self, target, source):
        return self.buffer.lookup_transform(target, source, Time())

    def verify(self):
        base_from_camera = self.lookup("base_link", "camera")
        camera_from_base = self.lookup("camera", "base_link")
        base_from_target = self.lookup("base_link", "target")

        point = PointStamped()
        point.header.frame_id = "camera"
        point.point.x = 1.0
        direction = Vector3Stamped()
        direction.header.frame_id = "camera"
        direction.vector.x = 1.0

        point_in_base = do_transform_point(point, base_from_camera)
        direction_in_base = do_transform_vector3(direction, base_from_camera)
        check("point: R p + t", coordinates(point_in_base), (1.0, 3.0, 0.0))
        check("vector: R v", coordinates(direction_in_base), (0.0, 1.0, 0.0))
        check(
            "inverse: camera <- base_link",
            coordinates(do_transform_point(point_in_base, camera_from_base)),
            (1.0, 0.0, 0.0),
        )

        target_origin = PointStamped()
        target_origin.header.frame_id = "target"
        check(
            "chain: base_link <- camera <- target",
            coordinates(do_transform_point(target_origin, base_from_target)),
            (1.0, 2.5, 0.0),
        )
        print("The target origin is now expressed in base_link; no IK is called.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep-alive", action="store_true",
        help="keep publishing /tf_static so another terminal can run tf2_echo",
    )
    args = parser.parse_args()

    rclpy.init()
    node = FrameLab()
    try:
        deadline = time.monotonic() + 10.0
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            try:
                node.verify()
                break
            except TransformException:
                if time.monotonic() >= deadline:
                    raise TimeoutError("tf2 frames were not available within 10 seconds")
        if args.keep_alive:
            print("Publishing static frames; press Ctrl+C to stop.")
            rclpy.spin(node)
        return 0
    except (AssertionError, TimeoutError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
