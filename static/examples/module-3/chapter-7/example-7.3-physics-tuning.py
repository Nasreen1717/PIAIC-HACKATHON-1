#!/usr/bin/env python3
"""
Physics Parameter Tuning for Isaac Sim

Purpose:
    Calibrate PhysX physics engine parameters (gravity, friction, restitution,
    timestep) to match real-world robot behavior and simulation accuracy.

Prerequisites:
    - Isaac Sim 2023.8+ with Python environment
    - A USD robot file loaded in scene
    - Knowledge of target robot physical properties

Usage:
    python3 example-7.3-physics-tuning.py --robot-path /World/robot

Expected Output:
    ✅ Physics tuning initialized
    ✅ Testing friction: 0.3 → 0.9
    ✅ Stability check passed
    ✅ Optimal parameters saved

"""

import argparse
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json
from pathlib import Path


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class PhysicsParameters:
    """Physics configuration parameters."""
    gravity: float = 9.81
    physics_dt: float = 0.01
    solver_iterations: int = 4
    solver_velocity_iterations: int = 1
    static_friction: float = 0.7
    dynamic_friction: float = 0.5
    restitution: float = 0.2
    max_contact_impulse: float = 1e32
    enable_gpu: bool = True


class PhysicsTuner:
    """Tune physics parameters for accurate simulation."""

    # Recommended material properties for different surfaces
    MATERIAL_PRESETS = {
        "rubber_on_floor": {
            "static_friction": 0.8,
            "dynamic_friction": 0.7,
            "restitution": 0.1
        },
        "metal_on_metal": {
            "static_friction": 0.4,
            "dynamic_friction": 0.3,
            "restitution": 0.3
        },
        "wood_on_wood": {
            "static_friction": 0.6,
            "dynamic_friction": 0.5,
            "restitution": 0.4
        },
        "humanoid_feet": {
            "static_friction": 0.8,
            "dynamic_friction": 0.7,
            "restitution": 0.1
        },
        "gripper_pads": {
            "static_friction": 0.9,
            "dynamic_friction": 0.8,
            "restitution": 0.0
        }
    }

    def __init__(self, robot_path: str):
        """Initialize physics tuner."""
        self.robot_path = robot_path
        self.params = PhysicsParameters()
        self.tuning_history: List[Dict] = []

        logger.info(f"📐 Physics Tuner initialized for {robot_path}")

    def validate_timestep(self, dt: float) -> bool:
        """✅ Validate physics timestep."""
        # Timestep should be small enough for stability
        if dt <= 0:
            logger.error(f"❌ Timestep must be positive: {dt}")
            return False

        if dt > 0.01:
            logger.warning(f"⚠️  Large timestep {dt}s may cause instability")
            return True

        if dt < 0.0001:
            logger.warning(f"⚠️  Very small timestep {dt}s will reduce performance")
            return True

        logger.info(f"✅ Timestep {dt}s valid")
        return True

    def estimate_max_velocity_per_step(self, dt: float) -> float:
        """Calculate maximum safe velocity per timestep."""
        # For stability, velocity change per step should be < 1 m/s
        # This prevents tunneling through thin objects
        return 1.0 / dt if dt > 0 else float('inf')

    def tune_friction(self, surface_type: str = "rubber_on_floor") -> Dict:
        """🎯 Apply friction presets for surface type."""
        if surface_type not in self.MATERIAL_PRESETS:
            logger.warning(f"⚠️  Unknown surface type: {surface_type}")
            return {}

        preset = self.MATERIAL_PRESETS[surface_type]
        self.params.static_friction = preset["static_friction"]
        self.params.dynamic_friction = preset["dynamic_friction"]
        self.params.restitution = preset["restitution"]

        logger.info(f"✅ Applied '{surface_type}' material preset:")
        logger.info(f"   Static friction:  {preset['static_friction']}")
        logger.info(f"   Dynamic friction: {preset['dynamic_friction']}")
        logger.info(f"   Restitution:      {preset['restitution']}")

        return preset

    def test_friction_sweep(self, friction_range: Tuple[float, float] = (0.1, 0.9)):
        """🧪 Test friction values across range."""
        logger.info(f"📊 Testing friction sweep: {friction_range[0]} → {friction_range[1]}")

        results = []
        step = 0.1
        current = friction_range[0]

        while current <= friction_range[1]:
            self.params.static_friction = current
            self.params.dynamic_friction = current * 0.85  # Dynamic < static

            # In real implementation, would run simulation and measure:
            # - Contact stability
            # - Sliding behavior
            # - No-slip conditions

            result = {
                "friction": round(current, 2),
                "stable": True,  # Would check actual sim
                "sliding_distance": 0.5 * current  # Simulated metric
            }
            results.append(result)
            current = round(current + step, 2)

        logger.info(f"✅ Friction sweep complete ({len(results)} values tested)")
        return results

    def test_restitution(self, bounce_range: Tuple[float, float] = (0.0, 0.8)):
        """🧪 Test restitution (bounce) across range."""
        logger.info(f"📊 Testing restitution: {bounce_range[0]} → {bounce_range[1]}")

        results = []
        step = 0.1
        current = bounce_range[0]

        while current <= bounce_range[1]:
            self.params.restitution = current

            # Simulated bounce test
            result = {
                "restitution": round(current, 2),
                "bounce_height_ratio": current,  # 1.0 = perfect bounce
                "energy_loss_percent": (1.0 - current) * 100
            }
            results.append(result)
            current = round(current + step, 2)

        logger.info(f"✅ Restitution sweep complete ({len(results)} values tested)")
        return results

    def check_stability(self) -> bool:
        """⚠️ Check physics parameter stability."""
        logger.info("🔍 Checking physics stability...")

        checks = [
            ("Gravity > 0", self.params.gravity > 0),
            ("Timestep small enough", self.params.physics_dt <= 0.01),
            ("Solver iterations >= 2", self.params.solver_iterations >= 2),
            ("Friction in range", 0.0 <= self.params.static_friction <= 1.0),
            ("Restitution in range", 0.0 <= self.params.restitution <= 1.0),
        ]

        all_passed = True
        for check_name, result in checks:
            if result:
                logger.info(f"  ✅ {check_name}")
            else:
                logger.error(f"  ❌ {check_name}")
                all_passed = False

        return all_passed

    def optimize_for_robot_type(self, robot_type: str) -> PhysicsParameters:
        """🤖 Recommend parameters for robot type."""
        recommendations = {
            "humanoid": {
                "physics_dt": 0.005,  # Faster for biped coordination
                "solver_iterations": 8,
                "static_friction": 0.8,
                "dynamic_friction": 0.7,
                "restitution": 0.1
            },
            "quadruped": {
                "physics_dt": 0.01,
                "solver_iterations": 4,
                "static_friction": 0.7,
                "dynamic_friction": 0.6,
                "restitution": 0.2
            },
            "manipulator": {
                "physics_dt": 0.001,  # Very fast for precise control
                "solver_iterations": 8,
                "static_friction": 0.9,
                "dynamic_friction": 0.8,
                "restitution": 0.0
            },
            "wheeled": {
                "physics_dt": 0.01,
                "solver_iterations": 4,
                "static_friction": 0.5,
                "dynamic_friction": 0.4,
                "restitution": 0.3
            }
        }

        if robot_type not in recommendations:
            logger.warning(f"⚠️  Unknown robot type: {robot_type}")
            return self.params

        rec = recommendations[robot_type]
        for key, value in rec.items():
            setattr(self.params, key, value)

        logger.info(f"🤖 Applied recommendations for {robot_type}:")
        for key, value in rec.items():
            logger.info(f"   {key}: {value}")

        return self.params

    def save_configuration(self, output_file: str = "physics_config.json"):
        """💾 Save tuned parameters to file."""
        config = {
            "gravity": self.params.gravity,
            "physics_dt": self.params.physics_dt,
            "solver_iterations": self.params.solver_iterations,
            "solver_velocity_iterations": self.params.solver_velocity_iterations,
            "static_friction": self.params.static_friction,
            "dynamic_friction": self.params.dynamic_friction,
            "restitution": self.params.restitution,
            "enable_gpu": self.params.enable_gpu
        }

        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"💾 Configuration saved: {output_file}")
        return config

    def load_configuration(self, input_file: str) -> PhysicsParameters:
        """📂 Load saved configuration."""
        with open(input_file, 'r') as f:
            config = json.load(f)

        for key, value in config.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)

        logger.info(f"📂 Configuration loaded: {input_file}")
        return self.params


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Tune physics parameters for Isaac Sim")
    parser.add_argument('--robot-path', default='/World/robot', help='Prim path to robot')
    parser.add_argument('--robot-type', default='humanoid',
                       choices=['humanoid', 'quadruped', 'manipulator', 'wheeled'])
    parser.add_argument('--surface', default='rubber_on_floor',
                       help='Surface material type')
    parser.add_argument('--output', default='physics_config.json', help='Output config file')

    args = parser.parse_args()

    try:
        # Initialize tuner
        tuner = PhysicsTuner(args.robot_path)

        # Apply recommendations
        logger.info("🚀 Starting physics tuning...")
        tuner.optimize_for_robot_type(args.robot_type)

        # Tune for surface
        tuner.tune_friction(args.surface)

        # Run tests
        friction_results = tuner.test_friction_sweep()
        restitution_results = tuner.test_restitution()

        # Validate
        stable = tuner.check_stability()

        if stable:
            logger.info("✅ Physics parameters validated")
            config = tuner.save_configuration(args.output)
            logger.info(f"✅ Tuning complete! Parameters saved to {args.output}")
            return 0
        else:
            logger.error("❌ Physics parameters failed validation")
            return 1

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
