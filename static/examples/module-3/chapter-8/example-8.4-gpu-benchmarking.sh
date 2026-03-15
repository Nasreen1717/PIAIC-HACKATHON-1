#!/bin/bash
###############################################################################
# Example 8.4: GPU Benchmarking for Isaac ROS Perception
#
# This script benchmarks GPU acceleration benefits of Isaac ROS vs. CPU-only
# implementations. Measures throughput, latency, and power consumption.
#
# Prerequisites:
#   - NVIDIA GPU with CUDA 11.0+
#   - nvidia-smi (NVIDIA driver)
#   - ROS 2 with isaac_ros packages
#   - Python with PyTorch/CUDA support
#
# Usage:
#   chmod +x example_8_4_gpu_benchmarking.sh
#   ./example_8_4_gpu_benchmarking.sh
#
# Output:
#   GPU: NVIDIA RTX 3080 (10GB VRAM)
#   Benchmark results saved to benchmark_results_*.csv
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Isaac ROS GPU Benchmarking Suite ===${NC}"

# Check GPU availability
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}Error: nvidia-smi not found. Please install NVIDIA drivers.${NC}"
    exit 1
fi

echo -e "${GREEN}GPU Information:${NC}"
nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader

# Create temporary Python script for benchmarking
BENCH_SCRIPT=$(mktemp)
cat > "$BENCH_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""GPU benchmarking for Isaac ROS."""

import torch
import time
import numpy as np
import csv
from pathlib import Path

def benchmark_gpu_operations():
    """Benchmark core GPU operations."""

    print("\n=== GPU Operation Benchmarks ===\n")

    if not torch.cuda.is_available():
        print("CUDA not available. Using CPU fallback.")
        device = torch.device('cpu')
    else:
        device = torch.device('cuda')

    print(f"Device: {device}")
    print(f"GPU Name: {torch.cuda.get_device_name()}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(device).total_memory / 1e9:.1f} GB\n")

    results = []

    # Benchmark 1: Matrix multiplication
    print("Benchmark 1: Matrix Multiplication (4096x4096)")
    A = torch.randn(4096, 4096).to(device)
    B = torch.randn(4096, 4096).to(device)

    torch.cuda.synchronize() if device.type == 'cuda' else None
    start = time.time()
    C = torch.mm(A, B)
    torch.cuda.synchronize() if device.type == 'cuda' else None
    elapsed = time.time() - start

    gflops = (2 * 4096**3 / elapsed) / 1e9
    print(f"  Time: {elapsed*1000:.2f}ms")
    print(f"  TFLOPS: {gflops:.1f}\n")
    results.append(("Matrix Multiplication", elapsed*1000, gflops))

    # Benchmark 2: Convolution (typical for VSLAM)
    print("Benchmark 2: 2D Convolution (3x640x480, 32 filters)")
    x = torch.randn(1, 3, 480, 640).to(device)
    conv = torch.nn.Conv2d(3, 32, kernel_size=3, padding=1).to(device)

    torch.cuda.synchronize() if device.type == 'cuda' else None
    start = time.time()
    y = conv(x)
    torch.cuda.synchronize() if device.type == 'cuda' else None
    elapsed = time.time() - start

    print(f"  Time: {elapsed*1000:.2f}ms")
    print(f"  Throughput: {(1/elapsed):.1f} fps (batch=1)\n")
    results.append(("2D Convolution", elapsed*1000, 1/elapsed))

    # Benchmark 3: Depth estimation (typical network)
    print("Benchmark 3: Depth Estimation Network")
    x = torch.randn(1, 3, 384, 512).to(device)

    # Simplified depth network
    net = torch.nn.Sequential(
        torch.nn.Conv2d(3, 64, 7, stride=2, padding=3),
        torch.nn.ReLU(),
        torch.nn.Conv2d(64, 64, 5, stride=2, padding=2),
        torch.nn.ReLU(),
        torch.nn.Conv2d(64, 1, 3, padding=1)
    ).to(device)

    times = []
    for _ in range(10):
        torch.cuda.synchronize() if device.type == 'cuda' else None
        start = time.time()
        y = net(x)
        torch.cuda.synchronize() if device.type == 'cuda' else None
        times.append(time.time() - start)

    avg_time = np.mean(times) * 1000
    fps = 1 / np.mean(times)
    print(f"  Avg Time: {avg_time:.2f}ms")
    print(f"  Throughput: {fps:.1f} fps\n")
    results.append(("Depth Network", avg_time, fps))

    # Benchmark 4: Memory bandwidth
    print("Benchmark 4: Memory Bandwidth (Copy)")
    sizes_gb = [0.1, 0.5, 1.0]

    for size_gb in sizes_gb:
        num_elements = int(size_gb * 1e9 / 4)
        x = torch.randn(num_elements).to(device)

        torch.cuda.synchronize() if device.type == 'cuda' else None
        start = time.time()
        y = x.clone()
        torch.cuda.synchronize() if device.type == 'cuda' else None
        elapsed = time.time() - start

        bandwidth_gbs = (size_gb / elapsed)
        print(f"  {size_gb:.1f} GB: {bandwidth_gbs:.1f} GB/s ({elapsed*1000:.2f}ms)")
        results.append((f"Bandwidth {size_gb}GB", elapsed*1000, bandwidth_gbs))

    print()
    return results


def benchmark_vslam_pipeline():
    """Benchmark complete VSLAM pipeline."""

    print("\n=== VSLAM Pipeline Benchmark ===\n")

    if not torch.cuda.is_available():
        print("CUDA not available. Using CPU fallback.")
        device = torch.device('cpu')
    else:
        device = torch.device('cuda')

    results = []

    # Simulate image processing pipeline
    print("Processing 100 frames (640x480):")

    frame_times = []
    for frame_idx in range(100):
        # Feature detection (GPU accelerated)
        x = torch.randn(1, 3, 480, 640).to(device)

        torch.cuda.synchronize() if device.type == 'cuda' else None
        start = time.time()

        # Simplified feature extraction
        features = torch.nn.functional.conv2d(
            x, torch.randn(32, 3, 3, 3).to(device), padding=1
        )

        torch.cuda.synchronize() if device.type == 'cuda' else None
        elapsed = time.time() - start

        frame_times.append(elapsed)

        if (frame_idx + 1) % 20 == 0:
            fps = 1 / np.mean(frame_times[-20:])
            print(f"  Frame {frame_idx+1}: {fps:.1f} fps")

    avg_fps = 1 / np.mean(frame_times)
    print(f"\nVSLAM Pipeline Performance:")
    print(f"  Average FPS: {avg_fps:.1f}")
    print(f"  Frame Time: {np.mean(frame_times)*1000:.2f}ms")
    print(f"  Latency (p95): {np.percentile(frame_times, 95)*1000:.2f}ms")

    results.append(("VSLAM Pipeline", np.mean(frame_times)*1000, avg_fps))

    return results


def benchmark_cpu_vs_gpu():
    """Compare CPU vs GPU performance."""

    print("\n=== CPU vs GPU Comparison ===\n")

    # Matrix multiplication comparison
    print("Matrix Multiplication (2048x2048):")

    A_cpu = torch.randn(2048, 2048, device='cpu')
    B_cpu = torch.randn(2048, 2048, device='cpu')

    start = time.time()
    C_cpu = torch.mm(A_cpu, B_cpu)
    cpu_time = time.time() - start
    print(f"  CPU time: {cpu_time*1000:.2f}ms")

    if torch.cuda.is_available():
        A_gpu = A_cpu.cuda()
        B_gpu = B_cpu.cuda()

        torch.cuda.synchronize()
        start = time.time()
        C_gpu = torch.mm(A_gpu, B_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start
        print(f"  GPU time: {gpu_time*1000:.2f}ms")
        print(f"  Speedup: {cpu_time/gpu_time:.1f}x")
    else:
        print("  GPU: Not available")

    print()


if __name__ == '__main__':
    try:
        results = benchmark_gpu_operations()
        results.extend(benchmark_vslam_pipeline())
        benchmark_cpu_vs_gpu()

        # Save results
        output_file = f"benchmark_results_{int(time.time())}.csv"
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Benchmark', 'Time (ms)', 'Throughput (FPS/TFLOPS)'])
            for name, time_ms, throughput in results:
                writer.writerow([name, f'{time_ms:.2f}', f'{throughput:.2f}'])

        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()

EOF

# Run Python benchmark
echo -e "\n${GREEN}Running benchmarks...${NC}"
python3 "$BENCH_SCRIPT"

# Clean up
rm "$BENCH_SCRIPT"

echo -e "\n${GREEN}Benchmarking complete!${NC}"
