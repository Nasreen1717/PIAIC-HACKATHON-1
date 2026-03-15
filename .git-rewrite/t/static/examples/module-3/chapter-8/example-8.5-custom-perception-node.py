#!/usr/bin/env python3
"""
Example 8.5: Custom GPU-Accelerated Perception Node

Complete example of building a production-ready perception node that:
- Loads a pre-trained neural network model
- Processes camera images on GPU
- Publishes detection results via ROS 2 topics
- Handles errors gracefully
- Logs performance metrics

Prerequisites:
  - ROS 2 Humble+
  - PyTorch with CUDA support
  - ONNX model or TorchScript weights
  - Camera publishing to /camera/image_raw

Usage:
  ros2 run example_8_5_custom_perception custom_perception_node \
    --ros-args -p model_path:=/path/to/model.pt

Output topics:
  - /perception/detections: Bounding boxes (visualization_msgs/MarkerArray)
  - /perception/class_labels: Object class IDs (std_msgs/Int32MultiArray)
  - /perception/confidence: Detection confidence scores (std_msgs/Float32MultiArray)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray, Int32MultiArray
from visualization_msgs.msg import MarkerArray, Marker
from cv_bridge import CvBridge
import numpy as np
import cv2
import torch
import time
from collections import deque


class CustomPerceptionNode(Node):
    """Production-ready GPU-accelerated perception node."""

    def __init__(self):
        super().__init__('custom_perception_node')

        # Parameters
        self.declare_parameter('model_path', '/models/yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('nms_threshold', 0.45)
        self.declare_parameter('gpu_device', 0)
        self.declare_parameter('input_size', 640)
        self.declare_parameter('batch_size', 1)
        self.declare_parameter('enable_metrics', True)

        model_path = self.get_parameter('model_path').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.nms_threshold = self.get_parameter('nms_threshold').value
        gpu_device = self.get_parameter('gpu_device').value
        self.input_size = self.get_parameter('input_size').value
        self.batch_size = self.get_parameter('batch_size').value
        self.enable_metrics = self.get_parameter('enable_metrics').value

        # Device setup
        self.device = torch.device(f'cuda:{gpu_device}' if torch.cuda.is_available() else 'cpu')
        self.get_logger().info(f"Using device: {self.device}")

        # Load model
        try:
            self.model = torch.jit.load(model_path).to(self.device)
            self.model.eval()
            self.get_logger().info(f"Model loaded: {model_path}")
        except Exception as e:
            self.get_logger().error(f"Failed to load model: {e}")
            raise

        # CV Bridge
        self.bridge = CvBridge()

        # Subscriptions
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publications
        self.detections_pub = self.create_publisher(
            MarkerArray,
            '/perception/detections',
            10
        )

        self.labels_pub = self.create_publisher(
            Int32MultiArray,
            '/perception/class_labels',
            10
        )

        self.confidence_pub = self.create_publisher(
            Float32MultiArray,
            '/perception/confidence',
            10
        )

        # Metrics
        self.frame_count = 0
        self.latency_history = deque(maxlen=100)

        self.get_logger().info("Custom perception node initialized")

    def image_callback(self, msg: Image):
        """Process incoming camera image."""
        try:
            start_time = time.time()

            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

            # Preprocess
            input_tensor = self.preprocess(cv_image)

            # Inference
            with torch.no_grad():
                detections = self.model(input_tensor)

            # Postprocess
            boxes, labels, scores = self.postprocess(detections, cv_image.shape)

            # Publish results
            self.publish_detections(boxes, labels, scores, msg.header)

            # Log metrics
            elapsed = time.time() - start_time
            self.latency_history.append(elapsed)
            self.frame_count += 1

            if self.enable_metrics and self.frame_count % 30 == 0:
                avg_latency = np.mean(self.latency_history) * 1000
                fps = 1.0 / np.mean(self.latency_history)
                self.get_logger().info(
                    f"Frame {self.frame_count}: "
                    f"{len(labels)} detections, "
                    f"{fps:.1f} fps, "
                    f"{avg_latency:.2f}ms latency"
                )

        except Exception as e:
            self.get_logger().error(f"Error in image callback: {e}")

    def preprocess(self, cv_image: np.ndarray) -> torch.Tensor:
        """
        Preprocess image for model inference.

        Args:
            cv_image: Input image (H, W, 3) in BGR format

        Returns:
            Preprocessed tensor ready for model
        """
        # Resize
        resized = cv2.resize(cv_image, (self.input_size, self.input_size))

        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # Normalize to [0, 1]
        normalized = rgb_image.astype(np.float32) / 255.0

        # Convert to tensor and add batch dimension
        tensor = torch.from_numpy(normalized).unsqueeze(0).permute(0, 3, 1, 2)

        # Move to device
        tensor = tensor.to(self.device)

        return tensor

    def postprocess(self, detections: torch.Tensor,
                   image_shape: tuple) -> tuple:
        """
        Postprocess model output to get boxes, labels, and scores.

        Args:
            detections: Model output tensor
            image_shape: Original image shape (H, W, C)

        Returns:
            (boxes, labels, scores) tuple
        """
        h, w = image_shape[:2]

        # Simplified postprocessing (specific to YOLO-like format)
        # detections shape: [1, num_detections, 6] (x, y, w, h, confidence, class)

        detections = detections.cpu().numpy()[0]  # Remove batch dimension

        boxes = []
        labels = []
        scores = []

        for det in detections:
            confidence = det[4]

            if confidence < self.confidence_threshold:
                continue

            # Extract box and scale to original image
            x_center, y_center = det[0] * w, det[1] * h
            box_w, box_h = det[2] * w, det[3] * h

            x1 = int(x_center - box_w / 2)
            y1 = int(y_center - box_h / 2)
            x2 = int(x_center + box_w / 2)
            y2 = int(y_center + box_h / 2)

            boxes.append([x1, y1, x2, y2])
            labels.append(int(det[5]))
            scores.append(float(confidence))

        return np.array(boxes), labels, scores

    def publish_detections(self, boxes: np.ndarray, labels: list,
                          scores: list, header):
        """Publish detection results."""
        # Marker array for visualization
        marker_array = MarkerArray()
        marker_array.markers = []

        for i, (box, label, score) in enumerate(zip(boxes, labels, scores)):
            marker = Marker()
            marker.header = header
            marker.id = i
            marker.type = Marker.CUBE
            marker.action = Marker.ADD

            x1, y1, x2, y2 = box
            marker.pose.position.x = float((x1 + x2) / 2) / 100.0  # Scale to meters
            marker.pose.position.y = float((y1 + y2) / 2) / 100.0
            marker.pose.position.z = 0.0

            marker.scale.x = float(x2 - x1) / 100.0
            marker.scale.y = float(y2 - y1) / 100.0
            marker.scale.z = 0.1

            # Color based on confidence
            marker.color.r = 1.0 - float(score)
            marker.color.g = float(score)
            marker.color.b = 0.0
            marker.color.a = 0.7

            marker_array.markers.append(marker)

        self.detections_pub.publish(marker_array)

        # Publish raw data
        labels_msg = Int32MultiArray()
        labels_msg.data = labels

        scores_msg = Float32MultiArray()
        scores_msg.data = scores

        self.labels_pub.publish(labels_msg)
        self.confidence_pub.publish(scores_msg)


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)

    try:
        node = CustomPerceptionNode()
        rclpy.spin(node)
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
