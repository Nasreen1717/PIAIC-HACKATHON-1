#!/usr/bin/env python3
"""
Isaac Sim Installation Validation Script

Purpose:
    Comprehensive GPU and Isaac Sim environment validation for robotics simulation.
    Verifies all critical dependencies, hardware capabilities, and configuration.

Prerequisites:
    - Ubuntu 22.04 LTS
    - NVIDIA GPU (RTX 3070+)
    - NVIDIA drivers 525+ installed
    - Python 3.10+ available

Usage:
    python3 example-7.1-installation-validation.py

Expected Output:
    ✅ GPU Validation Report
    ✅ CUDA Available: True
    ✅ Isaac Sim Package Found
    ✅ All validations passed!

"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple
import json


class IsaacSimValidator:
    """Validates Isaac Sim installation and GPU environment."""

    def __init__(self):
        """Initialize validator."""
        self.results = {
            "nvidia_driver": False,
            "cuda_available": False,
            "pytorch_gpu": False,
            "isaac_sim_package": False,
            "pycuda_available": False,
            "omniverse_launcher": False
        }
        self.versions = {}
        self.warnings = []
        self.errors = []

    def validate_nvidia_driver(self) -> bool:
        """✅ Verify NVIDIA drivers are installed and sufficient version."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                driver_version = result.stdout.strip().split('\n')[0]
                self.versions['nvidia_driver'] = driver_version

                # Check minimum version
                major_version = int(driver_version.split('.')[0])
                if major_version >= 525:
                    print(f"  ✅ NVIDIA Driver: {driver_version}")
                    return True
                else:
                    self.errors.append(f"Driver {driver_version} < 525 minimum")
                    return False
            else:
                self.errors.append("nvidia-smi not found")
                return False
        except Exception as e:
            self.errors.append(f"Driver check failed: {e}")
            return False

    def validate_cuda(self) -> bool:
        """✅ Verify CUDA installation and version."""
        try:
            result = subprocess.run(
                ['nvcc', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Extract CUDA version from output
                output = result.stdout
                if 'release' in output:
                    version = output.split('release')[1].strip().split(',')[0]
                    self.versions['cuda'] = version
                    print(f"  ✅ CUDA: {version}")
                    return True
            else:
                self.warnings.append("CUDA not in PATH")
                return False
        except FileNotFoundError:
            self.warnings.append("nvcc not found in PATH")
            return False
        except Exception as e:
            self.errors.append(f"CUDA check failed: {e}")
            return False

    def validate_pytorch_gpu(self) -> bool:
        """✅ Verify PyTorch with CUDA support."""
        try:
            import torch

            cuda_available = torch.cuda.is_available()
            device_count = torch.cuda.device_count() if cuda_available else 0

            if cuda_available and device_count > 0:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9

                self.versions['pytorch_cuda_version'] = torch.version.cuda
                self.versions['gpu_name'] = gpu_name
                self.versions['gpu_memory_gb'] = f"{gpu_memory:.2f}"

                print(f"  ✅ PyTorch GPU: {gpu_name}")
                print(f"     CUDA: {torch.version.cuda}, Memory: {gpu_memory:.2f} GB")

                # Check minimum VRAM
                if gpu_memory < 8:
                    self.warnings.append(f"GPU memory {gpu_memory:.1f}GB < 8GB recommended")
                    return True
                return True
            else:
                self.errors.append("PyTorch CUDA not available")
                return False
        except ImportError:
            self.errors.append("PyTorch not installed")
            return False
        except Exception as e:
            self.errors.append(f"PyTorch GPU check failed: {e}")
            return False

    def validate_isaac_sim_package(self) -> bool:
        """✅ Verify Isaac Sim installation."""
        try:
            omniverse_path = Path.home() / ".omniverse" / "pkg"

            if omniverse_path.exists():
                # Look for Isaac Sim installation
                isaac_dirs = list(omniverse_path.glob("*isaacsim*"))

                if isaac_dirs:
                    isaac_path = isaac_dirs[0]
                    version = isaac_path.name
                    self.versions['isaac_sim'] = version
                    print(f"  ✅ Isaac Sim: {version}")
                    return True
                else:
                    self.errors.append("Isaac Sim not found in ~/.omniverse/pkg/")
                    return False
            else:
                self.errors.append("Omniverse not installed (~/.omniverse/pkg/)")
                return False
        except Exception as e:
            self.errors.append(f"Isaac Sim check failed: {e}")
            return False

    def validate_pycuda(self) -> bool:
        """✅ Verify PyCUDA installation."""
        try:
            import pycuda.driver as cuda

            cuda.init()
            device_count = cuda.Device.count()

            if device_count > 0:
                device = cuda.Device(0)
                device_name = device.name().decode()
                self.versions['pycuda_device'] = device_name
                print(f"  ✅ PyCUDA: {device_name} ({device_count} device(s))")
                return True
            else:
                self.errors.append("No CUDA devices found")
                return False
        except ImportError:
            self.warnings.append("PyCUDA not installed (optional)")
            return False
        except Exception as e:
            self.errors.append(f"PyCUDA check failed: {e}")
            return False

    def validate_environment_variables(self) -> bool:
        """✅ Check required environment variables."""
        try:
            import os

            cuda_home = os.environ.get('CUDA_HOME')
            ld_library = os.environ.get('LD_LIBRARY_PATH', '')

            all_set = True
            if not cuda_home:
                self.warnings.append("CUDA_HOME not set")
                all_set = False
            else:
                print(f"  ✅ CUDA_HOME: {cuda_home}")

            if 'cuda' not in ld_library.lower():
                self.warnings.append("CUDA lib path not in LD_LIBRARY_PATH")
                all_set = False

            return all_set
        except Exception as e:
            self.errors.append(f"Environment check failed: {e}")
            return False

    def run_all_validations(self) -> bool:
        """🚀 Execute all validation checks."""
        print("\n🔍 Isaac Sim Installation Validator")
        print("=" * 50)

        print("\n📋 System Checks:")
        self.results['nvidia_driver'] = self.validate_nvidia_driver()
        self.results['cuda_available'] = self.validate_cuda()
        self.results['pytorch_gpu'] = self.validate_pytorch_gpu()
        self.results['pycuda_available'] = self.validate_pycuda()

        print("\n🎯 Isaac Sim Checks:")
        self.results['isaac_sim_package'] = self.validate_isaac_sim_package()

        print("\n⚙️  Environment Checks:")
        self.validate_environment_variables()

        return self._print_results()

    def _print_results(self) -> bool:
        """📊 Print comprehensive results."""
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)

        print("\n✅ Passed Checks:")
        passed_count = 0
        for check, result in self.results.items():
            if result:
                print(f"  • {check}")
                passed_count += 1

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.errors:
            print("\n❌ Failed Checks:")
            for error in self.errors:
                print(f"  • {error}")

        print("\n📈 Detected Versions:")
        for key, value in self.versions.items():
            print(f"  • {key}: {value}")

        # Overall result
        print("\n" + "=" * 50)
        all_passed = all(self.results.values())
        if all_passed:
            print("✅ All critical validations PASSED!")
            print("System is ready for Isaac Sim simulation.")
            return True
        else:
            print("❌ Some validations FAILED.")
            print("Please address errors before using Isaac Sim.")
            return False

    def export_report(self, output_file: str = "validation_report.json"):
        """💾 Export validation report to JSON."""
        report = {
            "timestamp": str(Path.cwd()),
            "results": self.results,
            "versions": self.versions,
            "warnings": self.warnings,
            "errors": self.errors,
            "overall_status": all(self.results.values())
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Report saved to: {output_file}")


def main():
    """Main entry point."""
    validator = IsaacSimValidator()

    try:
        success = validator.run_all_validations()
        validator.export_report()

        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(3)


if __name__ == '__main__':
    main()
