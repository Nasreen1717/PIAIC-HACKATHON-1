# Exercise 7.1: URDF Physics Tuning

## Overview

Tune a humanoid robot's physics parameters in Isaac Sim to match expected real-world behavior. You'll adjust gravity, friction, restitution, and timestep to achieve stable bipedal walking simulation without divergence or excessive energy loss.

**Difficulty**: Intermediate
**Duration**: 2-3 hours
**Learning Outcomes**:
- Understand PhysX physics engine parameters and their effects
- Calibrate friction and restitution for realistic contact simulation
- Detect and fix physics instability (divergence, tunneling)
- Validate physics accuracy against real-world measurements
- Optimize simulation timestep for accuracy vs. performance

**Prerequisites**:
- Completion of Chapter 7.1-7.3
- Access to Isaac Sim 2023.8+
- Sample humanoid URDF file
- Python 3.10+

---

## Problem Statement

You have a humanoid robot URDF with the following properties:
- **Mass**: 65 kg
- **Height**: 1.7 m
- **Feet dimensions**: 0.25m × 0.10m each
- **Expected walking speed**: 0.5 m/s
- **Stride length**: 0.35-0.45m

The robot is currently simulated with default PhysX parameters, but exhibits:
1. ❌ Feet slipping excessively during walking (no grip on floor)
2. ❌ Large bounces when feet contact ground (too much restitution)
3. ❌ Occasional physics divergence (bodies flying apart)
4. ⚠️ Slow simulation (need to run faster than real-time)

Your task is to find optimal parameter values that achieve:
- ✅ Stable, realistic walking gait
- ✅ No physics divergence
- ✅ Feet don't slip excessively
- ✅ Minimal energy loss
- ✅ Simulation runs faster than real-time (>200 Hz)

---

## Step-by-Step Instructions

### Step 1: Load and Inspect Robot (30 min)

1. Load humanoid.urdf in Isaac Sim
2. Inspect the robot structure:
   - List all links and their masses
   - Check joint limits
   - Verify mesh files load correctly

3. **Template code**:
```python
# Load URDF
from omni.isaac.core.utils.stage import add_reference_to_stage

robot = add_reference_to_stage(
    usd_path="./humanoid.usd",
    prim_path="/World/humanoid"
)

# Print robot info
print(robot.get_links())  # TODO: Complete
print(robot.get_joints())  # TODO: Complete
```

### Step 2: Establish Baseline Measurements (1 hour)

1. Run simulation with default physics for 5 seconds (real time)
2. Measure and record:
   - Robot's maximum forward velocity
   - Foot contact forces
   - Center of mass trajectory
   - Number of simulation steps completed (to estimate speed)

3. **What to measure**:
   - Actual stride length vs. expected (0.35-0.45m)
   - Contact friction during walking
   - Bounce height when foot hits ground
   - Simulation runtime (should be < 5 seconds of real time)

### Step 3: Tune Friction Parameters (45 min)

Friction affects how much the robot's feet grip the floor.

**Friction tuning process**:

| Parameter | Range | Effect |
|-----------|-------|--------|
| **Static Friction** | 0.4-1.0 | Higher = less slipping |
| **Dynamic Friction** | 0.3-0.9 | Usually ≤ static friction |
| **Restitution** | 0.0-0.3 | Higher = more bounce |

1. Start with humanoid preset: `friction=0.8, restitution=0.1`
2. Test 5 different friction values
3. For each value, measure:
   - Does robot slip during walking?
   - What's the max walking speed achieved?
   - Any physics instability?

4. **Acceptance Criteria**:
   - ✅ Walking speed ≥ 0.4 m/s
   - ✅ Feet don't slip more than 10% during stance
   - ✅ No physics divergence after 10s simulation

### Step 4: Tune Restitution (45 min)

Restitution controls bounce during contact.

1. Test values from 0.0 to 0.3 (humanoid feet typically have low bounce)
2. For each value, observe:
   - Bounce height when foot lands
   - Energy loss over walking cycle
   - Stability during walking

3. **Acceptance Criteria**:
   - ✅ Bounce < 5cm on foot contact
   - ✅ Gait appears natural (no bouncy walking)
   - ✅ Stable contact forces (no oscillations > 50%)

### Step 5: Optimize Timestep (30 min)

Physics accuracy depends on simulation timestep.

| Timestep (dt) | Frequency | Stability | Speed |
|---------------|-----------|-----------|-------|
| 0.001 s | 1000 Hz | Excellent | Slow |
| 0.005 s | 200 Hz | Good | Medium |
| 0.01 s | 100 Hz | Fair | Fast |

1. Test dt values: 0.01, 0.005, 0.001
2. For each, measure:
   - Simulation speed (real-time factor)
   - Physics stability
   - Accuracy vs. 0.001s baseline

3. **Acceptance Criteria**:
   - ✅ dt selected maintains > 200 Hz (real-time capable)
   - ✅ Accuracy loss < 5% vs. fine timestep
   - ✅ No stability issues

### Step 6: Validate Final Configuration (30 min)

1. Run 30-second walking simulation with optimal parameters
2. Measure:
   - Total distance walked
   - Number of divergence events (should be 0)
   - Feet contact stability
   - Simulation speed

3. **Acceptance Criteria**:
   - ✅ No physics divergence in 30s
   - ✅ Walking distance ≥ 10 meters
   - ✅ Simulation runs > 1x real-time

---

## Acceptance Criteria Checklist

| Criterion | Met? | Notes |
|-----------|------|-------|
| **Physics Stability** | ☐ | No divergence, valid velocities |
| **Walking Accuracy** | ☐ | Stride matches expected 0.35-0.45m |
| **Friction** | ☐ | Feet grip floor (slip < 10%) |
| **Restitution** | ☐ | Bounce minimal (< 5cm) |
| **Timestep** | ☐ | Real-time capable (> 100 Hz) |
| **Documentation** | ☐ | Parameters saved, measurements recorded |
| **Tests Pass** | ☐ | pytest solution achieves > 80% |

---

## Hints (5 Levels)

### Hint 1: Getting Started
Start with the humanoid material preset:
```python
static_friction=0.8
dynamic_friction=0.7
restitution=0.1
```

### Hint 2: Detecting Slip
Measure slip by comparing foot velocity vs. contact velocity:
```python
slip_ratio = foot_velocity / contact_velocity if contact_velocity > 0 else 0
if slip_ratio > 0.1:  # 10% slip threshold
    print("⚠️  Foot is slipping")
```

### Hint 3: Physics Divergence
Detect unstable physics:
```python
max_vel = 100  # m/s - anything higher is divergence
if np.linalg.norm(robot_velocity) > max_vel:
    print("❌ Physics divergence detected!")
    # Reduce timestep or increase solver iterations
```

### Hint 4: Timestep Selection
Use this formula to estimate good timestep:
```python
# dt = 1 / desired_frequency
# For humanoid walking: 100-200 Hz is typical
dt = 0.005  # 200 Hz
```

### Hint 5: Validation
Create a test that confirms stable walking:
```python
for step in range(300):  # 3 seconds at 100 Hz
    sim_step()
    if is_diverged():
        return False
return True  # Passed validation
```

---

## Template Code

```python
#!/usr/bin/env python3
"""Exercise 7.1: URDF Physics Tuning - Template"""

import numpy as np
from pathlib import Path
import json

class PhysicsTuner:
    def __init__(self, urdf_path: str):
        self.urdf_path = urdf_path
        self.measurements = {}  # TODO: Initialize measurement storage

    def load_robot(self):
        """TODO: Load URDF robot into Isaac Sim"""
        pass

    def apply_physics_params(self, friction: float, restitution: float, dt: float):
        """TODO: Set physics parameters"""
        pass

    def run_walking_test(self, duration_sec: float = 5.0) -> dict:
        """
        TODO: Run walking simulation and measure:
        - Walking distance
        - Physics stability
        - Contact forces
        - Simulation speed
        """
        pass

    def validate_results(self) -> bool:
        """TODO: Check if measurements meet acceptance criteria"""
        pass

    def save_optimal_params(self, output_file: str = "physics_params.json"):
        """TODO: Save optimal parameters"""
        pass

if __name__ == '__main__':
    # TODO: Main execution
    # 1. Load robot
    # 2. Test different parameter combinations
    # 3. Record measurements
    # 4. Validate results
    # 5. Save optimal configuration
    pass
```

---

## Solution Code (Summary)

See `solution.py` for complete implementation including:
- PhysX parameter application
- Measurement collection and analysis
- Parameter sweep and optimization
- Validation checks
- Results export

---

## Test Suite

Run with: `pytest test_solution.py -v`

**Test Coverage** (16 tests):
- ✅ Robot loads successfully
- ✅ Parameters apply without error
- ✅ Physics stability detected correctly
- ✅ Walking distance measured accurately
- ✅ Friction affects slip correctly
- ✅ Restitution affects bounce correctly
- ✅ Timestep affects simulation speed
- ✅ Divergence detection works
- ✅ Optimal parameters found
- ✅ Results saved correctly
- ✅ Validation passes with good params
- ✅ Validation fails with bad params
- ✅ Multiple test runs give consistent results
- ✅ Performance meets real-time requirements
- ✅ All measurements in valid ranges
- ✅ Documentation complete

---

## Common Mistakes

| Mistake | How to Avoid |
|---------|-------------|
| **Too high friction** (robot walks backwards) | Friction > 0.95 causes poor motion; stay ≤ 0.9 |
| **Too high restitution** (bouncy gait) | Keep restitution < 0.2 for humanoid feet |
| **Timestep too large** (unstable) | Test with dt=0.001 if dt=0.01 diverges |
| **Not measuring baseline** | Always record default parameters first |
| **Insufficient test duration** | Run at least 10s to detect slow divergence |
| **Ignoring solver iterations** | If unstable, increase from 4 to 8 iterations |
| **Not accounting for gravity** | Always verify gravity=9.81 m/s² |

---

## Extension Challenges

After completing the basic exercise:

1. **Multi-surface tuning**: Create separate material profiles for grass, concrete, mud. Test walking on each.

2. **Gait optimization**: Minimize energy consumption while maintaining walking speed using optimal parameters.

3. **Sensor integration**: Add IMU to measure actual walking stability and correlate with physics parameters.

4. **Parameter sweep**: Systematically test all combinations of 5 friction × 5 restitution × 3 timestep values. Plot results.

5. **Real-world comparison**: Import real robot walking data and match simulation parameters to minimize error.

---

## Grading Rubric

| Aspect | Poor (0-2) | Fair (3-5) | Good (6-8) | Excellent (9-10) |
|--------|-----------|-----------|-----------|-----------------|
| **Physics Tuning** | Parameters not applied | Basic tuning, some instability | Stable, minor issues | Stable, optimized, well-documented |
| **Measurements** | < 50% collected | ~75% collected | > 90% collected | Complete, accurate, validated |
| **Validation** | Failed | Partial pass | Mostly passes | All criteria met |
| **Code Quality** | Incomplete, errors | Working but messy | Clean, commented | Well-structured, documented |
| **Results Analysis** | No analysis | Basic observations | Good analysis | Thorough analysis with insights |

**Total**: _____ / 10 points

---

## References

- Isaac Sim Documentation: https://docs.omniverse.nvidia.com/isaacsim/latest/
- PhysX Parameter Tuning: https://nvidia-omniverse.github.io/isaacsim/
- Physics in Robotics: Anderson et al., "Humanoid Robotics" (2008)

---

*Exercise 7.1: URDF Physics Tuning* | Module 3 - Advanced Robotics
