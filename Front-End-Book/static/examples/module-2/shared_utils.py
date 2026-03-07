#!/usr/bin/env python3
"""
Shared utilities for Module 2 - The Digital Twin (Gazebo & Unity)

This module provides common helper functions for Gazebo simulation, ROS 2 integration,
and sensor data processing used across Chapter 4, 5, and 6 examples.

Author: Educational Module
Date: 2026-01-22
License: MIT
"""

import time
import subprocess
import sys
from typing import List, Optional, Dict, Any
import logging

import rclpy
from rclpy.node import Node
from rcl_interfaces.srv import GetParameters


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_urdf_gazebo(
    urdf_path: str,
    timeout: int = 30
) -> bool:
    """
    Verify that a URDF file can be loaded in Gazebo.

    Args:
        urdf_path: Absolute path to URDF file
        timeout: Maximum seconds to wait for verification (default: 30)

    Returns:
        bool: True if URDF loads successfully, False otherwise

    Raises:
        FileNotFoundError: If URDF file does not exist
        TimeoutError: If verification exceeds timeout
    """
    import os
    if not os.path.exists(urdf_path):
        raise FileNotFoundError(f"URDF file not found: {urdf_path}")

    logger.info(f"Loading URDF: {urdf_path}")
    try:
        # Verify URDF syntax using ros2 utility
        result = subprocess.run(
            ["ros2", "run", "urdf_parser_py", "urdf_parser", urdf_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            logger.info(f"✅ URDF syntax valid: {urdf_path}")
            return True
        else:
            logger.error(f"❌ URDF parse error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"❌ URDF parsing timeout (>{timeout}s)")
        raise TimeoutError(f"URDF parsing exceeded {timeout}s")
    except Exception as e:
        logger.error(f"❌ URDF parsing failed: {e}")
        return False


def launch_gazebo_world(
    world_file: Optional[str] = None,
    headless: bool = False,
    timeout: int = 20
) -> bool:
    """
    Launch Gazebo with optional world file.

    Args:
        world_file: Optional path to .world SDF file (uses default if None)
        headless: If True, run without GUI (server only)
        timeout: Maximum seconds to wait for Gazebo startup (default: 20)

    Returns:
        bool: True if Gazebo launches successfully, False otherwise
    """
    logger.info(f"Launching Gazebo (headless={headless})...")

    cmd = ["gazebo"]
    if headless:
        cmd.append("--verbose")
    if world_file:
        cmd.append(world_file)

    try:
        # Start Gazebo in background
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Gazebo process started (PID: {proc.pid})")

        # Give Gazebo time to initialize
        time.sleep(timeout)

        # Check if process is still running
        if proc.poll() is None:
            logger.info("✅ Gazebo initialized successfully")
            return True
        else:
            stdout, stderr = proc.communicate()
            logger.error(f"❌ Gazebo failed to start: {stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to launch Gazebo: {e}")
        return False


def verify_ros2_topic(
    topic_name: str,
    expected_type: Optional[str] = None,
    timeout: int = 10,
    node: Optional[Node] = None
) -> bool:
    """
    Verify that a ROS 2 topic exists and optionally check its message type.

    Args:
        topic_name: Name of ROS 2 topic (e.g., '/joint_states')
        expected_type: Optional expected message type (e.g., 'sensor_msgs/JointState')
        timeout: Maximum seconds to wait for topic (default: 10)
        node: Optional ROS 2 Node instance for type checking

    Returns:
        bool: True if topic exists (and matches type if specified), False otherwise
    """
    logger.info(f"Verifying ROS 2 topic: {topic_name}")

    try:
        # Use ros2 topic command to verify existence
        result = subprocess.run(
            ["ros2", "topic", "list"],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if topic_name in result.stdout:
            logger.info(f"✅ Topic exists: {topic_name}")

            # Check type if specified
            if expected_type:
                result = subprocess.run(
                    ["ros2", "topic", "info", topic_name],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if expected_type in result.stdout:
                    logger.info(f"✅ Topic type matches: {expected_type}")
                    return True
                else:
                    logger.warning(f"⚠️  Topic type mismatch (expected {expected_type})")
                    return False
            return True
        else:
            logger.warning(f"⚠️  Topic not found: {topic_name}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"❌ Topic verification timeout (>{timeout}s)")
        return False
    except Exception as e:
        logger.error(f"❌ Topic verification failed: {e}")
        return False


def wait_for_simulation_ready(
    timeout: int = 30,
    required_topics: Optional[List[str]] = None
) -> bool:
    """
    Wait for Gazebo simulation to be fully ready.

    Args:
        timeout: Maximum seconds to wait (default: 30)
        required_topics: Optional list of required ROS 2 topics

    Returns:
        bool: True if simulation ready, False if timeout or topics missing

    Raises:
        TimeoutError: If simulation not ready after timeout seconds
    """
    logger.info("Waiting for simulation to be ready...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Check gazebo is running
            result = subprocess.run(
                ["ros2", "topic", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Check for Gazebo topics
            if "/gazebo" not in result.stdout:
                logger.debug("Gazebo not yet ready...")
                time.sleep(1)
                continue

            # Check required topics if specified
            if required_topics:
                all_found = True
                for topic in required_topics:
                    if topic not in result.stdout:
                        logger.debug(f"Waiting for topic: {topic}")
                        all_found = False
                        break
                if not all_found:
                    time.sleep(1)
                    continue

            logger.info("✅ Simulation is ready!")
            return True

        except subprocess.TimeoutExpired:
            logger.debug("ROS 2 query timeout, retrying...")
            time.sleep(1)
        except Exception as e:
            logger.debug(f"Simulation check error: {e}, retrying...")
            time.sleep(1)

    raise TimeoutError(
        f"Simulation not ready after {timeout}s. "
        "Verify Gazebo is running and ROS 2 is configured correctly."
    )


def get_ros2_parameter(
    param_name: str,
    node_name: str = "/gazebo",
    timeout: int = 10
) -> Optional[Any]:
    """
    Get a ROS 2 parameter value from a node.

    Args:
        param_name: Parameter name (e.g., '/gazebo/gravity')
        node_name: Name of node to query (default: '/gazebo')
        timeout: ROS 2 service call timeout (default: 10)

    Returns:
        Parameter value if found, None otherwise
    """
    logger.info(f"Getting ROS 2 parameter: {param_name}")

    try:
        result = subprocess.run(
            ["ros2", "param", "get", node_name, param_name],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            logger.info(f"✅ Parameter value: {result.stdout.strip()}")
            return result.stdout.strip()
        else:
            logger.warning(f"⚠️  Parameter not found: {param_name}")
            return None

    except subprocess.TimeoutExpired:
        logger.error(f"❌ Parameter retrieval timeout (>{timeout}s)")
        return None
    except Exception as e:
        logger.error(f"❌ Parameter retrieval failed: {e}")
        return None


def validate_simulation_performance(
    measurement_duration: int = 10,
    min_fps: float = 30.0
) -> Dict[str, float]:
    """
    Measure Gazebo simulation performance (FPS and latency).

    Args:
        measurement_duration: How long to measure (seconds, default: 10)
        min_fps: Minimum acceptable FPS for warning (default: 30.0)

    Returns:
        dict: Performance metrics {'fps': float, 'latency_ms': float}
    """
    logger.info(f"Measuring simulation performance for {measurement_duration}s...")

    try:
        # Count messages on /gazebo/model_states topic
        result = subprocess.run(
            ["ros2", "topic", "hz", "/gazebo/model_states"],
            capture_output=True,
            text=True,
            timeout=measurement_duration + 5
        )

        metrics = {"fps": 0.0, "latency_ms": 0.0}

        # Parse hz output for frequency
        if "average rate:" in result.stdout:
            parts = result.stdout.split("average rate:")
            if len(parts) > 1:
                freq_str = parts[1].split()[0]
                try:
                    metrics["fps"] = float(freq_str)
                    metrics["latency_ms"] = 1000.0 / metrics["fps"]
                except ValueError:
                    pass

        if metrics["fps"] < min_fps:
            logger.warning(
                f"⚠️  Performance below target: {metrics['fps']:.1f} FPS "
                f"(expected >{min_fps:.1f})"
            )
        else:
            logger.info(
                f"✅ Performance acceptable: {metrics['fps']:.1f} FPS, "
                f"{metrics['latency_ms']:.1f}ms latency"
            )

        return metrics

    except subprocess.TimeoutExpired:
        logger.error("❌ Performance measurement timeout")
        return {"fps": 0.0, "latency_ms": 0.0}
    except Exception as e:
        logger.error(f"❌ Performance measurement failed: {e}")
        return {"fps": 0.0, "latency_ms": 0.0}


if __name__ == "__main__":
    """
    Quick test of shared utilities.
    Usage: python3 shared_utils.py
    """
    print("Module 2 Shared Utilities - Quick Test")
    print("=" * 50)

    # Example: Verify ROS 2 is available
    print("\nChecking ROS 2 availability...")
    result = subprocess.run(
        ["ros2", "--version"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"✅ {result.stdout.strip()}")
    else:
        print("❌ ROS 2 not found. Please install ROS 2 Humble.")

    print("\n" + "=" * 50)
    print("For detailed usage, see docstrings in this file.")
    print("Import functions: from shared_utils import <function_name>")
