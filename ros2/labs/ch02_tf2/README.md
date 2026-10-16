# Craig Chapter 2: tf2 frame lab

This is a standalone ROS 2 Jazzy Python exercise, not the planned 3R workspace.
It only broadcasts two static transforms and checks point/vector conversion.
It does not command a robot or publish `/joint_states`.

From Ubuntu with ROS 2 Jazzy installed:

```bash
source /opt/ros/jazzy/setup.bash
python3 -c 'import rclpy, tf2_ros, tf2_geometry_msgs, geometry_msgs'
cd /mnt/c/Repository/547540605/robotics-notes/robotics-notes/ros2/labs/ch02_tf2
python3 frame_lab.py
```

The `cd` path is the default WSL mount of this checkout. Adjust it if the
checkout is elsewhere. If the import check fails, first check that Jazzy is
installed and sourced; `tf2_geometry_msgs` is provided by the
`ros-jazzy-tf2-geometry-msgs` Ubuntu package.

Expected output includes four `PASS` lines:

```text
PASS point: R p + t: (1.0, 3.0, 0.0)
PASS vector: R v: (0.0, 1.0, 0.0)
PASS inverse: camera <- base_link: (1.0, 0.0, 0.0)
PASS chain: base_link <- camera <- target: (1.0, 2.5, 0.0)
```

To inspect the frames from a second terminal, keep the publisher alive:

```bash
python3 frame_lab.py --keep-alive
```

In another sourced terminal:

```bash
ros2 run tf2_ros tf2_echo base_link camera
ros2 run tf2_ros tf2_echo base_link target
```

`tf2_echo` may initially report that a frame does not exist while its buffer
is filling. The check passes when it subsequently reports translation
`[1.000, 2.500, 0.000]` and a `+90` degree yaw. Stop it with Ctrl+C.

The lesson and hand calculation are in
[`../../02a-chapter2-tf2-lab.html`](../../02a-chapter2-tf2-lab.html).
