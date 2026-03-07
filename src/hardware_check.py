"""
T017: Hardware detection utility for Module 3 setup validation.

Detects GPU, CUDA version, VRAM, and system capabilities.
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Optional


class HardwareDetector:
    """Detect and report hardware capabilities for Module 3."""

    def __init__(self):
        """Initialize hardware detector."""
        self.results = {}

    def detect_gpu(self) -> Dict[str, str]:
        """Detect NVIDIA GPU and return details."""
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=index,name,memory.total"],
                universal_newlines=True
            )
            lines = output.strip().split('\n')
            if lines:
                parts = lines[0].split(', ')
                return {
                    'gpu_available': True,
                    'gpu_name': parts[1] if len(parts) > 1 else 'Unknown',
                    'vram_mb': parts[2] if len(parts) > 2 else 'Unknown',
                }
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return {'gpu_available': False}

    def detect_cuda(self) -> Dict[str, str]:
        """Detect CUDA version."""
        try:
            output = subprocess.check_output(
                ["nvcc", "--version"],
                universal_newlines=True
            )
            for line in output.split('\n'):
                if 'release' in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'release':
                            return {'cuda_version': parts[i + 1].rstrip(',')}
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return {'cuda_available': False}

    def detect_python(self) -> Dict[str, str]:
        """Detect Python version."""
        import sys
        return {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'python_path': sys.executable
        }

    def detect_ros2(self) -> Dict[str, bool]:
        """Detect ROS 2 installation."""
        ros2_setup = Path("/opt/ros/humble/setup.bash")
        return {'ros2_humble_available': ros2_setup.exists()}

    def detect_isaac_sim(self) -> Dict[str, str]:
        """Detect Isaac Sim installation."""
        isaac_paths = [
            Path.home() / "isaac-sim/isaac-sim-2023.8.1-linux",
            Path.home() / "isaac-sim",
            Path("/opt/nvidia/isaac-sim"),
        ]

        for path in isaac_paths:
            if path.exists():
                return {'isaac_sim_path': str(path), 'isaac_sim_available': True}

        return {'isaac_sim_available': False, 'isaac_sim_path': 'Not found'}

    def check_pytorch(self) -> Dict[str, bool]:
        """Check if PyTorch is installed and GPU-enabled."""
        try:
            import torch
            return {
                'pytorch_available': True,
                'pytorch_cuda': torch.cuda.is_available()
            }
        except ImportError:
            return {'pytorch_available': False}

    def check_opencv(self) -> Dict[str, bool]:
        """Check if OpenCV is installed."""
        try:
            import cv2
            return {'opencv_available': True}
        except ImportError:
            return {'opencv_available': False}

    def generate_report(self) -> str:
        """Generate comprehensive hardware report."""
        self.results.update(self.detect_gpu())
        self.results.update(self.detect_cuda())
        self.results.update(self.detect_python())
        self.results.update(self.detect_ros2())
        self.results.update(self.detect_isaac_sim())
        self.results.update(self.check_pytorch())
        self.results.update(self.check_opencv())

        report = "Module 3 Hardware Detection Report\n"
        report += "=" * 50 + "\n\n"

        report += "GPU & CUDA:\n"
        report += f"  GPU Available: {self.results.get('gpu_available', False)}\n"
        if self.results.get('gpu_available'):
            report += f"  GPU Name: {self.results.get('gpu_name', 'Unknown')}\n"
            report += f"  VRAM: {self.results.get('vram_mb', 'Unknown')}\n"
        report += f"  CUDA Version: {self.results.get('cuda_version', 'Not found')}\n"

        report += "\nPython:\n"
        report += f"  Version: {self.results.get('python_version', 'Unknown')}\n"
        report += f"  Path: {self.results.get('python_path', 'Unknown')}\n"

        report += "\nROS 2:\n"
        report += f"  Humble Available: {self.results.get('ros2_humble_available', False)}\n"

        report += "\nIsaac Sim:\n"
        report += f"  Available: {self.results.get('isaac_sim_available', False)}\n"
        report += f"  Path: {self.results.get('isaac_sim_path', 'Not found')}\n"

        report += "\nDependencies:\n"
        report += f"  PyTorch: {self.results.get('pytorch_available', False)}\n"
        if self.results.get('pytorch_available'):
            report += f"  PyTorch CUDA: {self.results.get('pytorch_cuda', False)}\n"
        report += f"  OpenCV: {self.results.get('opencv_available', False)}\n"

        return report


def main():
    """Run hardware detection."""
    detector = HardwareDetector()
    print(detector.generate_report())


if __name__ == '__main__':
    main()
