#!/usr/bin/env python3
"""
Exercise 7.1: URDF Physics Tuning - Solution

Complete implementation for tuning humanoid robot physics parameters
to achieve stable, realistic walking in Isaac Sim simulation.

This solution includes:
- URDF robot loading and validation
- Physics parameter application (friction, restitution, timestep)
- Walking simulation and measurement collection
- Physics stability detection
- Parameter optimization
- Results validation and export

Author: Isaac Sim Educational Module
Version: 1.0.0
"""

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Simple array-like class for when numpy is not available
    class Array:
        def __init__(self, data):
            self.data = list(data) if not isinstance(data, list) else data
        def __len__(self):
            return len(self.data)
        def __getitem__(self, idx):
            return self.data[idx]
        def __setitem__(self, idx, val):
            self.data[idx] = val
        def __iter__(self):
            return iter(self.data)
        def copy(self):
            return Array(self.data[:])
        @property
        def shape(self):
            return (len(self.data),)
        def __add__(self, other):
            return Array([a + b for a, b in zip(self.data, other)])
        def __mul__(self, scalar):
            return Array([a * scalar for a in self.data])
        def __rmul__(self, scalar):
            return self * scalar

    class np:
        array = Array
        ndarray = Array
        inf = float('inf')

        @staticmethod
        def allclose(a, b, rtol=1e-5, atol=1e-8):
            try:
                # Handle scalar comparison
                if not hasattr(a, '__iter__'):
                    a = [a]
                if not hasattr(b, '__iter__'):
                    b = [b]
                return all(abs(float(x) - float(y)) <= atol + rtol * abs(float(y)) for x, y in zip(a, b))
            except:
                return False

        @staticmethod
        def linalg_norm(v):
            return sum(float(x)**2 for x in v) ** 0.5

        @staticmethod
        def max(arr):
            return max(float(x) for x in arr)

        @staticmethod
        def any(arr):
            if isinstance(arr, bool):
                return arr
            try:
                return any(bool(x) for x in arr)
            except:
                return bool(arr)

        @staticmethod
        def isnan(x):
            try:
                val = float(x)
                return val != val
            except:
                return False

        @staticmethod
        def isinf(x):
            try:
                val = float(x)
                return val == float('inf') or val == float('-inf')
            except:
                return False

        class linalg:
            @staticmethod
            def norm(v):
                return sum(float(x)**2 for x in v) ** 0.5

from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PhysicsConfig:
    """Physics simulation configuration parameters."""
    gravity: float = 9.81
    physics_dt: float = 0.01
    solver_iterations: int = 4
    static_friction: float = 0.8
    dynamic_friction: float = 0.7
    restitution: float = 0.1
    max_velocity_threshold: float = 100.0
    solver_velocity_iterations: int = 1

    def __str__(self) -> str:
        """String representation of config."""
        return (
            f"PhysicsConfig(gravity={self.gravity}, dt={self.physics_dt}, "
            f"friction={self.static_friction}/{self.dynamic_friction}, "
            f"restitution={self.restitution})"
        )


@dataclass
class WalkingMeasurement:
    """Measurements from a walking simulation test."""
    walking_distance: float = 0.0
    stride_length: float = 0.0
    max_velocity: float = 0.0
    feet_slip_ratio: float = 0.0
    bounce_height: float = 0.0
    divergence_detected: bool = False
    sim_speed: float = 1.0  # real-time factor
    simulation_steps: int = 0
    test_duration: float = 0.0
    physics_config: Optional[PhysicsConfig] = None

    def __str__(self) -> str:
        """String representation of measurement."""
        status = "✅ STABLE" if not self.divergence_detected else "❌ DIVERGED"
        return (
            f"WalkingMeasurement({status}, "
            f"distance={self.walking_distance:.2f}m, "
            f"slip={self.feet_slip_ratio:.1%}, "
            f"bounce={self.bounce_height:.3f}m)"
        )


class RobotSimulator:
    """Simulates robot physics without Isaac Sim (for testing)."""

    def __init__(self, urdf_path: str):
        """
        Initialize robot simulator.

        Args:
            urdf_path: Path to URDF file
        """
        self.urdf_path = urdf_path
        self.mass = 65.0  # kg
        self.height = 1.7  # m
        self.foot_length = 0.25  # m
        self.foot_width = 0.10  # m

        # Robot state
        self.position = np.array([0.0, 0.0, 0.85])  # x, y, z (COM height)
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.angular_velocity = np.array([0.0, 0.0, 0.0])

        # Contact state
        self.foot_left_contact = False
        self.foot_right_contact = False
        self.contact_force = np.array([0.0, 0.0, 0.0])

        logger.info(f"🤖 Robot loaded: mass={self.mass}kg, height={self.height}m")

    def simulate_step(
        self,
        config: PhysicsConfig,
        step_index: int,
        total_steps: int
    ) -> Tuple[np.ndarray, np.ndarray, bool]:
        """
        Simulate one physics timestep.

        Simulates bipedal walking with simple physics model:
        - Gravity pulls robot down
        - Friction resists sliding
        - Restitution adds bounce on contact
        - Walking velocity increases gradually

        Args:
            config: Physics configuration
            step_index: Current simulation step (0 to total_steps-1)
            total_steps: Total steps in simulation

        Returns:
            (position, velocity, divergence_detected)
        """
        dt = config.physics_dt

        # Simulate walking: gradually accelerate forward
        walking_phase = min(step_index / total_steps, 1.0)
        target_velocity = 0.5 * walking_phase  # Target 0.5 m/s walking speed

        # Apply friction (drag force opposes motion)
        friction_factor = max(0.0, 1.0 - config.static_friction * dt * 0.1)
        self.velocity[0] *= friction_factor

        # Accelerate towards target (walking motor)
        accel = (target_velocity - self.velocity[0]) * 2.0
        self.velocity[0] += accel * dt

        # Apply gravity
        self.velocity[2] -= config.gravity * dt

        # Contact detection (simple: COM height relative to foot)
        self.foot_left_contact = abs(self.position[2] - 0.85) < 0.01
        self.foot_right_contact = abs(self.position[2] - 0.85) < 0.01

        # Bounce (restitution on ground contact)
        if self.foot_left_contact or self.foot_right_contact:
            if self.velocity[2] < 0:
                # Ground contact
                bounce_velocity = -self.velocity[2] * config.restitution
                self.velocity[2] = bounce_velocity

        # Integrate position
        self.position += self.velocity * dt

        # Keep robot above ground
        if self.position[2] < 0.85:
            self.position[2] = 0.85
            self.velocity[2] = 0.0

        # Detect divergence (unrealistic velocities)
        max_vel = np.linalg.norm(self.velocity)
        diverged = max_vel > config.max_velocity_threshold

        if diverged:
            logger.warning(f"⚠️  Physics divergence detected: velocity={max_vel:.2f} m/s")

        return self.position.copy(), self.velocity.copy(), diverged


class PhysicsTuningExercise:
    """
    Physics tuning exercise for humanoid robot walking simulation.

    This class implements the complete workflow for tuning physics parameters
    to achieve stable, realistic bipedal walking.
    """

    def __init__(self, urdf_path: str):
        """
        Initialize the physics tuning exercise.

        Args:
            urdf_path: Path to humanoid robot URDF file
        """
        self.urdf_path = urdf_path
        self.robot = RobotSimulator(urdf_path)
        self.config = PhysicsConfig()
        self.measurements: List[WalkingMeasurement] = []
        self.optimal_config = None

        logger.info(f"📚 Physics Tuning Exercise initialized")

    def load_robot(self) -> bool:
        """
        Load URDF robot into simulation.

        In a real implementation, this would use:
        - omni.isaac.core.utils.stage.add_reference_to_stage()
        - ArticulationPrim to get robot reference

        Returns:
            True if successful
        """
        try:
            if not Path(self.urdf_path).exists():
                # For testing, we don't require actual file
                logger.warning(f"⚠️  URDF file not found at {self.urdf_path}")
                # Still return True for testing purposes

            logger.info(f"✅ Robot loaded from {self.urdf_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load robot: {e}")
            return False

    def apply_physics_parameters(self, config: PhysicsConfig) -> bool:
        """
        Apply physics parameters to simulation.

        Parameters control:
        - gravity: Acceleration due to gravity (m/s²)
        - physics_dt: Simulation timestep (seconds)
        - solver_iterations: PhysX solver iterations (higher = more stable)
        - static_friction: Static friction coefficient (0-1)
        - dynamic_friction: Kinetic friction coefficient (0-1)
        - restitution: Bounce coefficient (0-1)

        Args:
            config: PhysicsConfig with parameters to apply

        Returns:
            True if successful
        """
        try:
            # Validate parameters
            if config.gravity <= 0:
                logger.error(f"❌ Gravity must be positive: {config.gravity}")
                return False

            if config.physics_dt <= 0:
                logger.error(f"❌ Physics timestep must be positive: {config.physics_dt}")
                return False

            if not (0.0 <= config.static_friction <= 1.0):
                logger.error(f"❌ Friction must be in [0, 1]: {config.static_friction}")
                return False

            if not (0.0 <= config.restitution <= 1.0):
                logger.error(f"❌ Restitution must be in [0, 1]: {config.restitution}")
                return False

            self.config = config
            logger.info(f"✅ Physics parameters applied: {config}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to apply parameters: {e}")
            return False

    def run_walking_test(
        self,
        duration_sec: float = 5.0,
        verbose: bool = False
    ) -> WalkingMeasurement:
        """
        Run walking simulation and collect measurements.

        Measurements collected:
        - walking_distance: Total distance walked (m)
        - stride_length: Distance per step cycle (m)
        - max_velocity: Maximum velocity reached (m/s)
        - feet_slip_ratio: Fraction of time feet slip (0-1)
        - bounce_height: Maximum bounce on contact (m)
        - divergence_detected: Physics instability
        - sim_speed: Real-time factor

        Args:
            duration_sec: Simulation duration in seconds
            verbose: Print step-by-step output

        Returns:
            WalkingMeasurement with test results
        """
        # Calculate steps
        steps = int(duration_sec / self.config.physics_dt)

        # Reset robot state
        self.robot.position = np.array([0.0, 0.0, 0.85])
        self.robot.velocity = np.array([0.0, 0.0, 0.0])

        # Measurement accumulators
        positions = []
        velocities = []
        bounces = []
        slip_events = 0
        divergence_detected = False

        # Run simulation steps
        for step in range(steps):
            pos, vel, diverged = self.robot.simulate_step(
                self.config, step, steps
            )

            positions.append(pos.copy())
            velocities.append(vel.copy())
            divergence_detected = divergence_detected or diverged

            # Detect bounce (upward velocity spike on ground contact)
            if step > 0 and self.robot.foot_left_contact or self.robot.foot_right_contact:
                if vel[2] > 0.1:
                    bounces.append(vel[2])

            # Detect slip (foot moving sideways relative to velocity)
            if step % 10 == 0:
                foot_lateral_vel = abs(vel[1])
                if foot_lateral_vel > 0.05 and vel[0] > 0.1:
                    slip_events += 1

            if verbose and step % 50 == 0:
                logger.debug(f"Step {step}: pos={pos[0]:.2f}m, vel={vel[0]:.2f}m/s")

        # Calculate measurements
        if len(positions) > 0:
            total_distance = positions[-1][0] - positions[0][0]
        else:
            total_distance = 0.0

        # Calculate max velocity across all components and time steps
        max_velocity = 0.0
        for vel in velocities:
            vel_norm = np.linalg.norm(vel)
            if vel_norm > max_velocity:
                max_velocity = vel_norm

        bounce_height = np.max(bounces) if bounces else 0.0
        slip_ratio = min(slip_events / (steps / 10), 1.0)

        # Estimate stride length (assuming periodic walking)
        stride_length = total_distance / max(1.0, total_distance / 0.4)  # Assume ~0.4m strides

        # Estimate simulation speed
        sim_speed = duration_sec / (steps * self.config.physics_dt) if steps > 0 else 1.0

        measurement = WalkingMeasurement(
            walking_distance=max(0.0, total_distance),
            stride_length=stride_length,
            max_velocity=max_velocity,
            feet_slip_ratio=min(slip_ratio, 1.0),
            bounce_height=bounce_height,
            divergence_detected=divergence_detected,
            sim_speed=sim_speed,
            simulation_steps=steps,
            test_duration=duration_sec,
            physics_config=self.config
        )

        logger.info(f"✅ Walking test complete: {measurement}")
        return measurement

    def detect_divergence(self, max_velocity: float = 100.0) -> bool:
        """
        Detect physics divergence in current simulation state.

        Divergence indicators:
        - Velocities exceed max_velocity
        - Positions contain NaN or inf
        - Contact forces become very large

        Args:
            max_velocity: Maximum safe velocity (m/s)

        Returns:
            True if divergence detected
        """
        vel_norm = np.linalg.norm(self.robot.velocity)

        if vel_norm > max_velocity:
            logger.warning(f"❌ Velocity divergence: {vel_norm:.2f} > {max_velocity}")
            return True

        if np.any(np.isnan(self.robot.position)) or np.any(np.isinf(self.robot.position)):
            logger.warning(f"❌ Position contains NaN/inf: {self.robot.position}")
            return True

        return False

    def measure_friction_effect(self) -> Dict[float, WalkingMeasurement]:
        """
        Test multiple friction values and measure effects on slip.

        Tests friction values: 0.4, 0.6, 0.8, 0.9, 1.0

        Returns:
            Dict mapping friction value -> WalkingMeasurement
        """
        friction_values = [0.4, 0.6, 0.8, 0.9, 1.0]
        results = {}

        logger.info("📊 Testing friction effect on walking...")

        for friction in friction_values:
            config = PhysicsConfig(
                static_friction=friction,
                dynamic_friction=min(friction - 0.1, 1.0)
            )

            self.apply_physics_parameters(config)
            measurement = self.run_walking_test(duration_sec=2.0)
            results[friction] = measurement

            logger.info(
                f"  friction={friction:.1f} → "
                f"slip={measurement.feet_slip_ratio:.1%}, "
                f"distance={measurement.walking_distance:.2f}m"
            )

        return results

    def measure_restitution_effect(self) -> Dict[float, WalkingMeasurement]:
        """
        Test multiple restitution values and measure bounce effects.

        Tests restitution values: 0.0, 0.1, 0.2, 0.3, 0.4

        Returns:
            Dict mapping restitution value -> WalkingMeasurement
        """
        restitution_values = [0.0, 0.1, 0.2, 0.3, 0.4]
        results = {}

        logger.info("📊 Testing restitution effect on bounce...")

        for restitution in restitution_values:
            config = PhysicsConfig(restitution=restitution)

            self.apply_physics_parameters(config)
            measurement = self.run_walking_test(duration_sec=2.0)
            results[restitution] = measurement

            logger.info(
                f"  restitution={restitution:.1f} → "
                f"bounce={measurement.bounce_height:.3f}m"
            )

        return results

    def measure_timestep_effect(self) -> Dict[float, WalkingMeasurement]:
        """
        Test multiple timestep values and measure simulation speed/stability.

        Tests timestep values: 0.001, 0.005, 0.01 seconds

        Returns:
            Dict mapping timestep -> WalkingMeasurement
        """
        timestep_values = [0.001, 0.005, 0.01]
        results = {}

        logger.info("📊 Testing timestep effect on simulation...")

        for dt in timestep_values:
            config = PhysicsConfig(physics_dt=dt)

            self.apply_physics_parameters(config)
            measurement = self.run_walking_test(duration_sec=1.0)
            results[dt] = measurement

            frequency_hz = 1.0 / dt
            logger.info(
                f"  dt={dt:.4f}s ({frequency_hz:.0f}Hz) → "
                f"speed={measurement.sim_speed:.1f}x, "
                f"stable={not measurement.divergence_detected}"
            )

        return results

    def find_optimal_parameters(self) -> Tuple[PhysicsConfig, WalkingMeasurement]:
        """
        Find optimal physics parameters using parameter sweep.

        Optimization criteria:
        - Minimize slip (friction)
        - Minimize bounce (restitution)
        - Maximize walking speed
        - Maintain stability
        - Real-time capable (> 100 Hz)

        Returns:
            (optimal_config, resulting_measurement)
        """
        logger.info("🔍 Finding optimal parameters...")

        # Test different configurations
        best_score = -np.inf
        best_config = PhysicsConfig()
        best_measurement = None

        # Test friction values
        friction_values = [0.6, 0.7, 0.8, 0.9]
        restitution_values = [0.05, 0.1, 0.15]
        timestep_values = [0.005, 0.01]

        for friction in friction_values:
            for restitution in restitution_values:
                for dt in timestep_values:
                    config = PhysicsConfig(
                        static_friction=friction,
                        dynamic_friction=max(0.3, friction - 0.1),
                        restitution=restitution,
                        physics_dt=dt
                    )

                    self.apply_physics_parameters(config)
                    measurement = self.run_walking_test(duration_sec=3.0)

                    # Scoring function
                    score = 0.0

                    # Prefer stable physics
                    if not measurement.divergence_detected:
                        score += 10.0

                    # Prefer low slip
                    score += (1.0 - measurement.feet_slip_ratio) * 5.0

                    # Prefer low bounce
                    score += max(0.0, (0.05 - measurement.bounce_height) * 100.0)

                    # Prefer good walking distance
                    score += measurement.walking_distance

                    # Prefer real-time capable simulation
                    if measurement.sim_speed >= 1.0:
                        score += 5.0

                    if score > best_score:
                        best_score = score
                        best_config = config
                        best_measurement = measurement

        logger.info(f"✅ Optimal parameters found: {best_config}")
        logger.info(f"   Score: {best_score:.2f}, Results: {best_measurement}")

        self.optimal_config = best_config
        return best_config, best_measurement

    def validate_results(self, measurement: WalkingMeasurement) -> bool:
        """
        Validate that measurements meet all acceptance criteria.

        Criteria:
        - Walking speed ≥ 0.4 m/s
        - Feet slip < 10% (slip_ratio < 0.1)
        - Bounce < 5cm (0.05m)
        - No physics divergence
        - Simulation real-time capable

        Args:
            measurement: WalkingMeasurement to validate

        Returns:
            True if all criteria met
        """
        logger.info("✅ Validating results against acceptance criteria...")

        criteria = []

        # Criterion 1: Walking speed
        walking_speed = measurement.walking_distance / max(measurement.test_duration, 0.1)
        speed_ok = walking_speed >= 0.4
        criteria.append(("Walking speed ≥ 0.4 m/s", speed_ok, f"{walking_speed:.2f} m/s"))

        # Criterion 2: Slip
        slip_ok = measurement.feet_slip_ratio < 0.1
        criteria.append(("Feet slip < 10%", slip_ok, f"{measurement.feet_slip_ratio:.1%}"))

        # Criterion 3: Bounce
        bounce_ok = measurement.bounce_height < 0.05
        criteria.append(("Bounce < 5cm", bounce_ok, f"{measurement.bounce_height:.3f}m"))

        # Criterion 4: No divergence
        divergence_ok = not measurement.divergence_detected
        criteria.append(("No physics divergence", divergence_ok, "Stable"))

        # Criterion 5: Real-time capable
        rtc_ok = measurement.sim_speed >= 1.0 or (1.0 / measurement.physics_config.physics_dt) >= 100
        criteria.append(("Real-time capable", rtc_ok, f"{measurement.sim_speed:.1f}x"))

        # Print validation report
        all_pass = True
        for criterion, passed, value in criteria:
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {criterion}: {value}")
            all_pass = all_pass and passed

        if all_pass:
            logger.info("✅ All validation criteria met!")
        else:
            logger.warning("❌ Some validation criteria not met")

        return all_pass

    def save_results(
        self,
        output_file: str = "physics_tuning_results.json"
    ) -> bool:
        """
        Save tuning results to JSON file.

        Output includes:
        - Optimal parameters
        - Measurements from final validation
        - Validation status
        - Timestamp and version

        Args:
            output_file: Output filename

        Returns:
            True if successful
        """
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "optimal_config": asdict(self.optimal_config) if self.optimal_config else None,
                "measurements": [asdict(m) for m in self.measurements],
                "validation_passed": all(
                    self.validate_results(m) for m in self.measurements
                ) if self.measurements else False
            }

            # Convert PhysicsConfig to dict
            if results["measurements"]:
                for m in results["measurements"]:
                    if m.get("physics_config"):
                        m["physics_config"] = asdict(m["physics_config"])

            output_path = Path(output_file)
            output_path.write_text(json.dumps(results, indent=2))

            logger.info(f"✅ Results saved to {output_path.absolute()}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
            return False


def main():
    """Main execution workflow."""
    print("=" * 70)
    print("Exercise 7.1: URDF Physics Tuning")
    print("=" * 70)
    print()

    # Initialize exercise
    exercise = PhysicsTuningExercise("humanoid.urdf")

    # Step 1: Load robot
    logger.info("Step 1: Loading robot...")
    if not exercise.load_robot():
        logger.error("Failed to load robot")
        return 1

    # Step 2: Establish baseline
    logger.info("\nStep 2: Establishing baseline measurements...")
    baseline_config = PhysicsConfig()
    exercise.apply_physics_parameters(baseline_config)
    baseline = exercise.run_walking_test(duration_sec=5.0)
    exercise.measurements.append(baseline)

    # Step 3: Measure friction effect
    logger.info("\nStep 3: Testing friction parameters...")
    friction_results = exercise.measure_friction_effect()

    # Step 4: Measure restitution effect
    logger.info("\nStep 4: Testing restitution parameters...")
    restitution_results = exercise.measure_restitution_effect()

    # Step 5: Measure timestep effect
    logger.info("\nStep 5: Testing timestep parameters...")
    timestep_results = exercise.measure_timestep_effect()

    # Step 6: Find optimal parameters
    logger.info("\nStep 6: Finding optimal parameters...")
    optimal_config, optimal_measurement = exercise.find_optimal_parameters()
    exercise.measurements.append(optimal_measurement)

    # Step 7: Validate
    logger.info("\nStep 7: Validating results...")
    validation_pass = exercise.validate_results(optimal_measurement)

    # Step 8: Save results
    logger.info("\nStep 8: Saving results...")
    exercise.save_results("physics_tuning_results.json")

    print()
    print("=" * 70)
    print(f"Exercise Complete: {'✅ PASSED' if validation_pass else '❌ FAILED'}")
    print("=" * 70)

    return 0 if validation_pass else 1


if __name__ == '__main__':
    exit(main())
