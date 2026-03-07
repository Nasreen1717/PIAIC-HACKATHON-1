# Implementation Plan: Module 2 - The Digital Twin (Gazebo & Unity)

**Branch**: `002-digital-twin` | **Date**: 2026-01-22 | **Spec**: [specs/002-digital-twin/spec.md](./spec.md)
**Input**: Feature specification from `specs/002-digital-twin/spec.md`

---

## Summary

Module 2 extends Module 1 (ROS 2 Fundamentals) by teaching students how to simulate robots in physics engines (Gazebo) and render them in professional 3D engines (Unity), with comprehensive sensor simulation. The module comprises 3 chapters (80-100 pages), 13-16 working code examples, and 6 student exercises, progressing from physics simulation → rendering → sensor integration → full digital twin pipeline.

**Technical Approach:**
- **Architecture**: Gazebo (physics simulation backend) → ROS 2 (communication middleware) → Unity (rendering frontend)
- **Content Structure**: Docusaurus with Markdown chapters, embedded code blocks, side-by-side examples
- **Examples Organization**: Chapter-numbered files (4-*.py for Gazebo, 5-*.cs for Unity, 6-*.py for sensors)
- **Exercise Progression**: Guided (step-by-step) → semi-open (design choices) → open-ended (build from scratch)
- **Integration with Module 1**: Reuse ROS 2 concepts (nodes, topics, services, actions, URDF from Ch1)

---

## Technical Context

**Language/Version**: Python 3.10+ (Gazebo, ROS 2, sensor processing); C# 10.0 (Unity 2022.3+)
**Primary Dependencies**:
- Gazebo 11+ (physics engine)
- ROS 2 Humble (communication middleware, rclpy, rcl bindings)
- Unity 2022.3 LTS (rendering, animation)
- Python libraries: numpy, scipy (sensor processing), opencv-python (depth image processing)

**Storage**: File-based (URDF, SDF, launch files); ROS 2 parameter server for configuration
**Testing**: pytest (Python examples), automated test suites for exercises
**Target Platform**: Ubuntu 22.04 LTS (primary); headless/cloud alternatives documented
**Project Type**: Educational multi-chapter module (Docusaurus site + code examples + exercises)
**Performance Goals**:
- Chapter 4 (Gazebo): Simulation runs at physics timestep (default 1000 Hz internal, 30-50 Hz visual)
- Chapter 5 (Unity): Real-time rendering at 60+ FPS on standard GPU
- Chapter 6 (Sensors): LiDAR/depth camera at ≥10 Hz; integrated pipeline at >30 FPS
- Gazebo ↔ ROS 2 ↔ Unity latency: <100ms (network + processing)

**Constraints**:
- Gazebo 11 (not cutting-edge Fortress) for stability; Unity 2022.3+ for robotics support
- Headless rendering requires X11/VNC in cloud environments
- Sensor point cloud density capped at 1M points/frame for computational feasibility
- Code examples must be copy-paste runnable without project setup overhead

**Scale/Scope**:
- 3 chapters, 80-100 pages total
- 13-16 code examples (4-5 per chapter)
- 6 student exercises (2 per chapter)
- Target: 2-3 weeks of study (8-10 hours/week)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Alignment

| Principle | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| **I. Technical Accuracy** | All claims traceable to official docs (ROS 2, Gazebo, Unity) | ✅ PASS | Will cite official documentation; version-specific (Humble, Gazebo 11, Unity 2022.3) |
| **II. Hands-On Learning** | Min 50 working examples; all tested on Ubuntu 22.04 | ✅ PASS | 13-16 examples in Module 2 (part of 50+ total); all must pass PEP 8 + linting |
| **III. Spec-Driven Development** | Full spec, plan, tasks; inline documentation; RAG-ready | ✅ PASS | Spec complete; plan in progress; tasks will be detailed; README per chapter |
| **IV. Progressive Content** | Module 2 follows Module 1 (ROS 2) and precedes Module 3 (Isaac) | ✅ PASS | Explicit dependency on Module 1 concepts (nodes, URDF); preps for Isaac Sim |
| **V. Safety & Simulation-First** | All code has guards, timeouts; simulation validated before hardware | ✅ PASS | Gazebo-first approach; sensor noise modeled realistically; no infinite loops |

### Content Standards Compliance

| Standard | Requirement | Status | Implementation Notes |
|----------|-------------|--------|----------------------|
| **Citation** | IEEE format, all APIs cited, version numbers | ✅ PLAN | Every chapter section will include "Citation:" block with ROS 2, Gazebo, Unity official docs |
| **Code Quality** | PEP 8 compliance, unit tests, CI validation | ✅ PLAN | All Python code via `flake8 --max-line-length=100`; exercise tests via pytest |
| **Exercises** | 30+ total across modules; formative (quizzes) + summative (projects) | ✅ PASS | Module 2 contributes 6 exercises; quizzes per chapter; mini-project in assessments |
| **Readability** | Flesch-Kincaid 12-14 grade level | ✅ PLAN | Technical prose for CS/AI students; glossary for ROS 2 / Gazebo / Unity terms |

### Gate Evaluation

**Result**: ✅ **PASS** - All core principles and content standards aligned. No constitution violations.

---

## Project Structure

### Documentation (Docusaurus Module 2)

```text
Front-End-Book/docs/module-2/
├── intro.md                          # Module overview, learning objectives, prerequisites
├── glossary.md                        # ROS 2, Gazebo, Unity, sensor terminology
├── chapter-4.md                       # Gazebo physics simulation (~25 pages)
├── chapter-5.md                       # Unity rendering (~25 pages)
├── chapter-6.md                       # Sensor simulation (~30 pages)
├── README.md                          # Module landing page
├── assessments/
│   ├── quiz-4.md                     # Chapter 4 formative assessment
│   ├── quiz-5.md                     # Chapter 5 formative assessment
│   ├── quiz-6.md                     # Chapter 6 formative assessment
│   └── mini-project.md               # Capstone: Digital Twin Controller
└── [created by existing Module 1 tasks]

specs/002-digital-twin/
├── spec.md                            # Feature specification
├── plan.md                            # This file
├── research.md                        # Phase 0 (research output)
├── data-model.md                      # Phase 1 (entity definitions)
├── quickstart.md                      # Phase 1 (getting started guide)
├── contracts/
│   ├── gazebo-sdf-schema.json        # SDF file structure documentation
│   ├── ros2-sensor-messages.json     # PointCloud2, Image, Imu schema
│   └── unity-prefab-schema.json      # Robot prefab structure
└── checklists/
    └── requirements.md                # Quality validation

history/prompts/002-digital-twin/
├── 001-module2-specification.spec.prompt.md
├── 002-module2-planning.plan.prompt.md           # [Will be created by this command]
└── ...
```

### Source Code (Examples & Exercises)

```text
Front-End-Book/static/examples/module-2/
├── README.md                          # Examples index and setup instructions
├── 4-gazebo-world.launch.xml         # Gazebo world launch file
├── 4-humanoid-sim.py                 # Load humanoid URDF in Gazebo
├── 4-simple-control.py               # Basic joint control via ROS 2
├── 4-gripper-simulation.py           # Gripper sensor simulation
├── 4-physics-tuning.py               # Adjust friction, gravity, collisions
├── 5-urdf-to-unity.py                # Python tool: convert URDF → Unity prefab
├── 5-joint-animator.cs               # C# script: animate from ROS 2 joint state
├── 5-material-setup.cs               # C# script: realistic materials and lighting
├── 5-keyboard-controller.cs          # C# script: interactive joint control
├── 6-lidar-sim.py                    # LiDAR point cloud processing
├── 6-depth-camera.py                 # RealSense-style depth camera simulation
├── 6-imu-sensor.py                   # Accelerometer + gyroscope data
├── 6-sensor-fusion.py                # Fuse multiple sensors (EKF example)
└── [~13-16 total across chapters]

Front-End-Book/static/exercises/module-2/
├── 4-1-gazebo-tutorial/
│   ├── README.md                     # Problem statement, learning objectives, acceptance criteria
│   ├── solution.py                   # Reference implementation
│   └── test_solution.py              # Pytest acceptance tests
├── 4-2-robot-control/
│   ├── README.md
│   ├── solution.py
│   └── test_solution.py
├── 5-1-unity-import/
│   ├── README.md
│   ├── solution.cs
│   └── test_solution.py              # Visual + functional validation
├── 5-2-animation/
│   ├── README.md
│   ├── solution.cs
│   └── test_solution.py
├── 6-1-lidar-processing/
│   ├── README.md
│   ├── solution.py
│   └── test_solution.py
└── 6-2-sensor-fusion/
    ├── README.md
    ├── solution.py
    └── test_solution.py

tests/
├── test_chapter_4.py                 # Integration tests for Gazebo examples
├── test_chapter_5.py                 # Integration tests for Unity C# scripts
└── test_chapter_6.py                 # Integration tests for sensor examples
```

**Structure Decision**:
- **Docusaurus chapters**: Live in Front-End-Book/docs/module-2/ as Markdown files
- **Examples**: Organized by chapter in Front-End-Book/static/examples/module-2/
- **Exercises**: Directory per exercise with README, solution, and test suite in Front-End-Book/static/exercises/module-2/
- **Specification artifacts**: Keep in specs/002-digital-twin/ (research.md, data-model.md, contracts/)
- **Tests**: Centralized in tests/ directory with chapter-specific files

This structure mirrors Module 1 (chapters/examples/exercises separate) and is Docusaurus-compatible.

---

## Content Architecture

### Chapter 4: Physics Simulation with Gazebo

**Sections:**
1. Introduction: What is Gazebo? (use case, alternatives: Isaac Sim, V-REP)
2. Installation & Setup (Ubuntu 22.04, ROS 2 Humble integration)
3. Gazebo Architecture (client-server model, world files, SDF format)
4. World & Environment (adding objects, gravity, physics parameters)
5. Humanoid Robot Simulation (loading URDF, setting up links/joints)
6. Physics Simulation (gravity, friction, contact detection, joint constraints)
7. ROS 2 Integration (publishing joint states, subscribing to commands, /gazebo namespace topics)
8. Debugging & Monitoring (gzclient visualization, RViz2 TF tree, topic inspection)
9. Working Examples (4-5 progressively complex, from "hello world" to full controller)
10. Exercises (2 total: basic setup, then joint control with feedback)

**Key Concepts from Module 1 Reused:**
- URDF format (already learned in Ch3)
- Nodes and topics (already learned in Ch1)
- Launch files (already learned in Ch1)
- Joint definitions and frames (already learned in Ch3)

**Code Examples (4-5):**
- 4-humanoid-sim.py: Load humanoid URDF in default Gazebo world
- 4-simple-control.py: Subscribe to `/joint_commands`, apply to simulator
- 4-gripper-simulation.py: Add gripper sensor, detect contact
- 4-physics-tuning.py: Demonstrate gravity, friction, collision parameters
- 4-ros2-integration.py: Full example with multiple ROS 2 nodes (publisher, subscriber, service)

---

### Chapter 5: High-Fidelity Rendering with Unity

**Sections:**
1. Introduction: Why Unity for Robotics? (use case, rendering quality, interactivity)
2. Unity 2022.3 Setup (installation, robotics packages, ROS 2 support)
3. 3D Assets & Materials (importing URDF-generated meshes, realistic materials)
4. Skeletal Animation Basics (joint hierarchies, animation controllers)
5. URDF to Unity Conversion (tool overview, hierarchy mapping, material setup)
6. ROS 2 Integration in Unity (subscribing to joint state, commanding via topics)
7. Real-Time Joint Animation (converting joint angles to Euler rotations, animator parameters)
8. Lighting & Rendering (realistic lighting models, shadows, HDR, post-processing)
9. Human-Robot Interaction (interactive mode for manual control, debugging visualization)
10. Performance Optimization (LOD, batching, profiling for target FPS)
11. Working Examples (4-5 demonstrating animation, lighting, interaction)
12. Exercises (2 total: basic import and animation, then full HRI demo)

**Key Concepts from Previous Chapters:**
- Robot kinematics (from Module 1 Ch3 - URDF)
- Joint state messages (from Module 2 Ch4 - Gazebo)
- ROS 2 topics and subscription (from Module 1 Ch2)

**Code Examples (4-5, C# and supporting Python):**
- 5-urdf-to-unity.py: Convert URDF → Unity prefab (Python helper tool)
- 5-joint-animator.cs: C# script subscribing to `/joint_states`, animating robot
- 5-material-setup.cs: C# script applying realistic materials
- 5-keyboard-controller.cs: C# script for manual joint control
- 5-hri-demo.cs: Interactive demo showing robot + environment feedback

---

### Chapter 6: Sensor Simulation

**Sections:**
1. Introduction: Sensors in Digital Twins (use cases, standard ROS 2 message types)
2. LiDAR Simulation (2D/3D laser scanners, point cloud generation, noise models)
3. Depth Camera Simulation (RealSense-style, depth image extraction, camera intrinsics)
4. IMU Simulation (accelerometer, gyroscope, bias and noise)
5. Sensor Data in ROS 2 (PointCloud2, Image, Imu message types)
6. Processing Point Clouds (filtering, downsampling, registration basics)
7. Processing Depth Images (depth to point cloud conversion, segmentation)
8. Sensor Fusion Basics (time alignment, EKF for state estimation)
9. Visualizing Sensor Data (RViz2 integration, PointCloud2 plugin)
10. Working Examples (5-6 covering all sensor types and fusion)
11. Exercises (2 total: individual sensor processing, then sensor fusion task)

**Key Concepts from Previous Chapters:**
- ROS 2 topics and messages (from Module 1 Ch2, Module 2 Ch4)
- Point cloud data structures (from computer vision background)
- Gazebo sensor plugins (from Module 2 Ch4)

**Code Examples (5-6, all Python with ROS 2 integration):**
- 6-lidar-sim.py: Subscribe to `/scan` (LaserScan), process point clouds
- 6-depth-camera.py: Subscribe to `/camera/depth/image_raw`, extract metrics
- 6-imu-sensor.py: Subscribe to `/imu/data`, integrate for pose estimation
- 6-sensor-fusion.py: Implement simple EKF fusing LiDAR + IMU
- 6-visualization.py: Visualize multiple sensors in RViz2
- 6-point-cloud-pipeline.py: End-to-end pipeline (capture → filter → register)

---

## Integration with Module 1

### Explicit Dependencies on Module 1

**Chapter 4 (Gazebo) depends on:**
- Module 1, Chapter 1: Node concepts, topic pub/sub basics
- Module 1, Chapter 2: Services, launch files, parameters
- Module 1, Chapter 3: URDF format, links, joints, coordinate frames

**Chapter 5 (Unity) depends on:**
- Module 1, Chapter 1: ROS 2 nodes, topics, callbacks
- Module 1, Chapter 2: Message types (especially sensor_msgs/JointState)
- Module 1, Chapter 3: Robot kinematics, URDF hierarchy
- Module 2, Chapter 4: Physics simulation basics (to understand what Unity is rendering)

**Chapter 6 (Sensors) depends on:**
- Module 1, Chapter 1: Topic pub/sub, message types
- Module 1, Chapter 2: Custom messages, message serialization
- Module 2, Chapter 4: Gazebo sensor plugins

### Reuse Patterns

1. **URDF Files**: Use humanoid URDF from Module 1 Ch3 throughout Module 2
2. **Launch Files**: Apply launch file patterns from Module 1 Ch2 in Module 2 Ch4
3. **ROS 2 Nodes**: Extend ROS 2 node patterns from Module 1 Ch1 with sensor processing
4. **Message Types**: Reuse Module 1 custom message understanding; introduce sensor_msgs types
5. **Glossary**: Extend Module 1 glossary with Gazebo, Unity, sensor terminology

---

## Execution Strategy

### Phase-Based Implementation

**Phase 0 (Research, this command)**:
- Resolve any technical clarifications in research.md
- Document Gazebo/Unity version compatibility
- Finalize content outline for each chapter

**Phase 1 (Design & Contracts)**:
- Create data-model.md (entity definitions for worlds, robots, sensors)
- Create contracts/ (schema for SDF, ROS 2 messages, Unity prefabs)
- Create quickstart.md (getting started in 30 minutes)

**Phase 2 (Task Generation, next command)**:
- Generate detailed tasks.md with T001-T0XX items
- Break each chapter into: introduction → core sections → examples → exercises
- Define testable acceptance criteria and dependencies

**Implementation**:
- Follow tasks.md sequentially
- Commit after each task (or logical group)
- Run tests continuously; report failures immediately

### Dependency Graph

```
CH4 Introduction (T00X)
  ↓
CH4 Architecture & Setup (T00X)
  ↓
CH4 Examples (T00X) — [parallel with exercises]
  ↓
CH4 Exercises (T00X)
  ├→ CH5 Introduction (T00X) [start after Ch4 Arch]
  │  ↓
  │  CH5 Examples (T00X) — [parallel with exercises]
  │  ↓
  │  CH5 Exercises (T00X)
  │
  ├→ CH6 Introduction (T00X) [start after Ch4 Arch]
  │  ↓
  │  CH6 Examples (T00X) — [parallel with exercises]
  │  ↓
  │  CH6 Exercises (T00X)
  │
  └→ Capstone / Integration (T00X)
```

**Parallelization**:
- Ch4 foundational (must start first)
- Ch5 and Ch6 can develop in parallel once Ch4 architecture is documented
- Final capstone exercise integrates all three

---

## Quality Assurance

### Testing Strategy

1. **Unit Tests**: All functions with >5 lines of code
2. **Integration Tests**: Each example tested on Ubuntu 22.04 + ROS 2 Humble + Gazebo 11
3. **Exercise Tests**: Automated test suites (pytest) for each exercise
4. **Content Tests**:
   - Markdown linting (no broken links, proper structure)
   - Code syntax validation (flake8 for Python, Unity API checks for C#)
   - Citation validation (all external links accessible)

### Success Metrics

- ✅ All 13-16 code examples run without errors on target platform
- ✅ All 6 exercises have passing test suites (80%+ pass rate expected)
- ✅ All Python code passes PEP 8 linting
- ✅ All chapters build in Docusaurus without errors
- ✅ All external citations are valid and accessible
- ✅ Content readability: Flesch-Kincaid 12-14
- ✅ Estimated reading time: 2-3 weeks at 8-10 hours/week

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| Gazebo 11 deprecation or instability | Examples don't run | Medium | Document fallback (Isaac Sim), keep Humble LTS support active until 2027 |
| Unity version incompatibility | C# scripts break | Low | Lock to Unity 2022.3 LTS; test on launch; document upgrade path |
| ROS 2 ↔ Gazebo/Unity latency > 100ms | Integration example fails | Medium | Use DDS QoS tuning, document network bottlenecks, provide headless alternative |
| Hardware requirements too high | Students can't run examples | Medium | Provide cloud alternatives (NVIDIA Isaac Cloud, AWS); document minimum specs |
| Sensor simulation doesn't match reality | Students confused about real vs. simulated | Low | Include "simulation vs. reality" section; explain noise models, sensor gaps |

---

## Next Steps

1. **Phase 0 (This command)**: Complete and approve this plan.md
2. **Phase 0 Research**: Generate research.md with any unresolved technical questions
3. **Phase 1 Design**: Create data-model.md, contracts/, quickstart.md
4. **Phase 2 Tasks**: Run `/sp.tasks` to generate detailed task breakdown
5. **Implementation**: Execute tasks.md in order; commit + test regularly
6. **Validation**: Run full test suite; validate in Docusaurus build
7. **Release**: Create GitHub release notes for Module 2 v1.0.0

---

**Status**: ✅ **READY FOR PHASE 1 DESIGN**

This plan provides clear architectural guidance, dependency resolution, and execution strategy. No constitution violations detected. Proceed to research.md (Phase 0 output) and then Phase 1 (design & contracts).
