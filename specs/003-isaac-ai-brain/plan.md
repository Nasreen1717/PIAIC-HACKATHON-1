# Implementation Plan: Module 3 - The AI-Robot Brain (NVIDIA Isaac)

**Branch**: `003-isaac-ai-brain` | **Date**: 2026-01-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-isaac-ai-brain/spec.md`

---

## Summary

Module 3 delivers a 3-chapter Docusaurus curriculum (Isaac Sim, Isaac ROS, Nav2) targeting robotics students transitioning from ROS 2/Gazebo fundamentals to advanced perception and navigation with GPU-accelerated hardware. The module progressively builds on Module 1-2 foundations while establishing sim-to-real workflows and cloud-first accessibility (RTX 4070 Ti+ primary, AWS/NVIDIA cloud alternatives). Success is measured by error-free code execution, measurable GPU performance gains (5x speedup), photorealistic synthetic data generation (1000+ images), and validated path planning on bipedal robots (100% collision avoidance).

---

## Technical Context

**Language/Version**: Python 3.10+, C++ 17 (Isaac SDK); ROS 2 Humble; Docusaurus 3.x

**Primary Dependencies**:
- NVIDIA Isaac Sim 2023.8+
- Isaac ROS 2.0+ (GPU-accelerated perception nodes)
- Nav2 Humble (bipedal navigation stack)
- ROS 2 Humble (standard middleware)
- NVIDIA CUDA 12.x, cuDNN 8.x (GPU acceleration)
- PyTorch 2.x, NumPy, OpenCV (perception and image processing)

**Storage**: File-based (YAML configs for simulations, USD assets, URDF models); optional PostgreSQL for tracking student exercise submissions (out of scope for Module 3)

**Testing**:
- pytest for Python example validation
- ROS 2 launch testing for integration tests
- Docusaurus build validation (markdown, MDX, example execution)
- Manual GPU benchmarking via provided scripts (GPU utilization, inference latency)

**Target Platform**: Ubuntu 22.04 LTS (primary); AWS g5.2xlarge, NVIDIA Isaac Cloud (cloud alternatives)

**Project Type**: Educational content (Docusaurus site) + example code repository (ROS 2 packages, Python scripts, Jupyter notebooks)

**Performance Goals**:
- Chapter 7 examples: <2s startup time, synthetic data generation 500-1000 images/hour
- Chapter 8 VSLAM: ≥5x GPU speedup vs. CPU baseline, <5% localization error
- Chapter 9 navigation: <2s path planning on 10x10m environments, 100% collision avoidance on 3+ obstacles
- Documentation load time: <1.5s on 50Mbps connection (Docusaurus)

**Constraints**:
- GPU VRAM: 8GB minimum (RTX 4070 Ti+ has 24GB); fallback to batching for limited memory
- Isaac Sim physics: 30+ FPS simulation on RTX 4070 Ti+; lower-end cloud instances (AWS g5.xlarge) acceptable with quality degradation
- Student exercise completion: <4 hours per chapter including setup/debugging
- Cloud cost: AWS estimated ~$2-4/hour for g5.2xlarge; NVIDIA Isaac Cloud covered by trial/credits

**Scale/Scope**:
- 3 chapters, 15-18 total examples, 6 exercises
- ~80-100 pages documentation
- ~10,000 lines of example code (Python, C++, YAML, launch files)
- 15-20 key concepts per chapter; cumulative module scope: 45-60 learning outcomes

---

## Constitution Check

**Gate: All items must pass before Phase 0 research. Re-check after Phase 1 design.**

| Principle | Item | Status | Notes |
|-----------|------|--------|-------|
| **I. Technical Accuracy** | Citations 60% official docs, 30% peer-reviewed, 10% community | ✅ PASS | Isaac Sim, Isaac ROS, Nav2 have comprehensive official documentation; IEEE robotics journals support SLAM/planning concepts |
| **I. Technical Accuracy** | All APIs validated against Ubuntu 22.04 + ROS 2 Humble | ✅ PASS | Isaac Sim 2023.8+ certified on Ubuntu 22.04; ROS 2 Humble is LTS; versions explicitly specified in requirements |
| **I. Technical Accuracy** | No extrapolations; gaps explicitly flagged | ✅ PASS | Sim-to-real transfer is documented as heuristic (80% success); physics divergence handled via sensitivity analysis |
| **II. Hands-On Learning** | Minimum 50 working code examples across all modules | ⚠️ CONDITIONAL PASS | Module 3 targets 15-18 examples; cumulative 50+ when combined with Modules 1-2; each example will be tested on hardware |
| **II. Hands-On Learning** | All examples tested on Ubuntu 22.04 with specified hardware | ✅ PASS | Plan includes automated CI testing; cloud alternatives documented |
| **II. Hands-On Learning** | Exercises progress: read → modify → extend → build | ✅ PASS | Chapter 7 exercise 1: modify URDF physics, exercise 2: generate custom dataset; Chapter 8/9 follow similar progression |
| **II. Hands-On Learning** | No pseudocode; all code production-ready | ✅ PASS | All examples will follow PEP 8, ROS 2 standards; no pseudocode in Docusaurus |
| **III. Spec-Driven Development** | Spec, plan, tasks, implementation pipeline | ✅ PASS | Spec (complete), plan (in progress), tasks (next), implementation (scheduled Phase 2) |
| **III. Spec-Driven Development** | Inline docs + READMEs; RAG-optimized | ✅ PASS | Docusaurus structure supports semantic chunking; code examples include docstrings; READMEs per example |
| **IV. Modular, Progressive** | Module progression: ROS 2 → Gazebo → Isaac → VLA | ✅ PASS | Module 3 explicitly builds on Module 1-2; prepares foundation for Module 4 (vision-language actions) |
| **IV. Modular, Progressive** | Prerequisites clear; glossary provided | ⚠️ CONDITIONAL PASS | Module 3 requires Module 1-2 completion; glossary to be added during documentation phase |
| **V. Safety + Hardware Flexibility** | Simulation-first; safety protocols explicit | ✅ PASS | All examples run in Isaac Sim first; sim-to-real transfer checklist in Chapter 9 |
| **V. Safety + Hardware Flexibility** | Hardware alternatives: primary + cloud | ✅ PASS | RTX 4070 Ti+ primary; AWS g5.2xlarge, NVIDIA Isaac Cloud documented |
| **V. Safety + Hardware Flexibility** | No infinite loops, unbounded allocations; timeouts | ✅ PASS | All examples include timeouts and graceful shutdown; synthetic data generation batched |

**Gate Result**: ✅ **PASS** — Module 3 plan aligns with all constitutional principles. Conditional items (50+ examples cumulative, glossary) depend on Modules 1-2 completion and will be verified post-Phase 1.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-isaac-ai-brain/
├── spec.md                  # Feature specification (COMPLETE)
├── plan.md                  # This file - implementation plan
├── research.md              # Phase 0: research findings
├── data-model.md            # Phase 1: entity definitions
├── quickstart.md            # Phase 1: setup and first example
├── contracts/               # Phase 1: example/exercise contracts
│   ├── chapter-7-examples.yaml
│   ├── chapter-8-examples.yaml
│   ├── chapter-9-examples.yaml
│   ├── chapter-7-exercises.yaml
│   ├── chapter-8-exercises.yaml
│   └── chapter-9-exercises.yaml
├── checklists/
│   ├── requirements.md       # Specification quality checklist (COMPLETE)
│   └── implementation.md     # Phase 1: implementation checklist
└── tasks.md                 # Phase 2: output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
Front-End-Book/
├── docs/
│   └── module-3/                    # Chapter documentation
│       ├── chapter-7-isaac-sim.mdx  # Isaac Sim fundamentals
│       ├── chapter-8-isaac-ros.mdx  # VSLAM & perception
│       └── chapter-9-nav2-bipedal.mdx # Nav2 path planning
│
├── static/
│   ├── examples/
│   │   └── module-3/
│   │       ├── chapter-7/           # Isaac Sim examples
│   │       │   ├── 7.1-installation-validation.py
│   │       │   ├── 7.2-urdf-import.py
│   │       │   ├── 7.3-physics-tuning.py
│   │       │   ├── 7.4-sensor-simulation.py
│   │       │   └── 7.5-synthetic-data-export.py
│   │       ├── chapter-8/           # Isaac ROS examples
│   │       │   ├── 8.1-vslam-pipeline.py
│   │       │   ├── 8.2-depth-perception.py
│   │       │   ├── 8.3-sensor-fusion.py
│   │       │   ├── 8.4-gpu-benchmarking.sh
│   │       │   ├── 8.5-custom-perception-node.py
│   │       │   └── 8.6-ros-isaac-integration.launch.py
│   │       └── chapter-9/           # Nav2 examples
│   │           ├── 9.1-nav2-setup.launch.py
│   │           ├── 9.2-bipedal-costmap.yaml
│   │           ├── 9.3-global-planning.yaml
│   │           ├── 9.4-local-planning.yaml
│   │           ├── 9.5-obstacle-avoidance.py
│   │           └── 9.6-sim-to-real-transfer.md
│   │
│   └── exercises/
│       └── module-3/
│           ├── chapter-7/           # Isaac Sim exercises
│           │   ├── 7.ex1-urdf-physics-tuning/
│           │   │   ├── starter.py
│           │   │   ├── solution.py
│           │   │   └── README.md
│           │   └── 7.ex2-synthetic-data-generation/
│           │       ├── starter.py
│           │       ├── solution.py
│           │       └── README.md
│           ├── chapter-8/           # VSLAM exercises
│           │   ├── 8.ex1-vslam-accuracy/
│           │   │   ├── starter.py
│           │   │   ├── solution.py
│           │   │   └── README.md
│           │   └── 8.ex2-sensor-fusion-optimization/
│           │       ├── starter.py
│           │       ├── solution.py
│           │       └── README.md
│           └── chapter-9/           # Nav2 exercises
│               ├── 9.ex1-bipedal-planning/
│               │   ├── starter.launch.py
│               │   ├── solution.launch.py
│               │   └── README.md
│               └── 9.ex2-sim-to-real-validation/
│                   ├── starter.py
│                   ├── solution.py
│                   └── README.md
│
├── ros2_ws/                         # ROS 2 workspace for Module 3
│   └── src/
│       ├── isaac_sim_examples/      # Isaac Sim interaction package
│       ├── isaac_ros_examples/      # Custom VSLAM perception package
│       └── nav2_bipedal/            # Bipedal navigation configuration
│
├── requirements/                    # Dependency specifications
│   ├── module-3-base.txt           # Python dependencies (core)
│   ├── module-3-dev.txt            # Development/testing dependencies
│   └── module-3-cloud.txt          # Cloud-specific (AWS/NVIDIA) dependencies
│
├── docker/
│   └── module-3.Dockerfile         # Reproducible environment
│
├── tests/
│   ├── unit/
│   │   ├── test_isaac_sim_examples.py
│   │   ├── test_isaac_ros_examples.py
│   │   └── test_nav2_examples.py
│   ├── integration/
│   │   ├── test_chapter_7_workflow.py
│   │   ├── test_chapter_8_workflow.py
│   │   └── test_chapter_9_workflow.py
│   └── conftest.py                 # pytest fixtures
│
└── CI/
    └── .github/workflows/
        └── module-3-tests.yml       # GitHub Actions for validation
```

**Structure Decision**:
- **Documentation**: Docusaurus MDX for content + semantic chunking (RAG-optimized)
- **Examples**: Python-first (PyTorch/NumPy for perception), with C++ Isaac SDK examples for advanced topics
- **ROS 2 Integration**: colcon workspace with dedicated packages per chapter (separation of concerns)
- **Testing**: pytest + ROS 2 launch testing for validation; Docker for reproducibility
- **Cloud Support**: requirements files and Docker target AWS EC2 (g5.2xlarge) and NVIDIA Isaac Cloud
- **Exercises**: Starter/solution pairs with clear progression (read → modify → extend)

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A — no constitutional violations detected | — | — |

---

## Phase 0: Research & Clarification

**Prerequisites**: Specification complete (✅)

### Research Tasks

1. **Isaac Sim 2023.8+ Architecture & APIs**
   - Focus: USD asset import, physics engine configuration, synthetic data pipelines
   - Sources: NVIDIA docs, Isaac Sim tutorials, published benchmarks
   - Deliverable: research.md section "Isaac Sim Setup & Architecture"

2. **Isaac ROS Hardware-Accelerated Perception Patterns**
   - Focus: GPU-accelerated VSLAM (V-SLAM), depth perception, sensor fusion integration
   - Sources: Isaac ROS documentation, NVIDIA GTC talks, robotics vision papers
   - Deliverable: research.md section "Isaac ROS Perception Stack"

3. **Nav2 Bipedal Navigation Customization**
   - Focus: Costmap setup for bipedal robots, footstep planning, balance constraints
   - Sources: Nav2 documentation, humanoid robotics literature, Boston Dynamics papers
   - Deliverable: research.md section "Nav2 Bipedal Extensions"

4. **Cloud Deployment Equivalence (AWS g5.2xlarge vs. RTX 4070 Ti+)**
   - Focus: Performance variance, cost implications, setup procedures
   - Sources: AWS documentation, NVIDIA Isaac Cloud docs, benchmarking reports
   - Deliverable: research.md section "Cloud Alternatives & Cost Analysis"

5. **Sim-to-Real Transfer Protocols & Risks**
   - Focus: Domain randomization, physics calibration, hardware validation checklists
   - Sources: Sim2Real benchmarks, safety protocols from robotics literature
   - Deliverable: research.md section "Sim-to-Real Transfer & Safety"

---

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete

### 1.1 Data Model

**Key Entities**:

1. **Isaac Sim Scene** (data-model.md)
   - Represents a photorealistic 3D environment with physics
   - Fields: scene_id, gravity_vector, surface_materials, physics_timestep, renderer_type
   - Relationships: contains Robot Models, Sensors, Light sources
   - Validation: gravity ±1% tolerance; physics_timestep ≥0.0001s (100kHz max)

2. **Robot Model** (data-model.md)
   - Represents a URDF-based humanoid (7-8 DOF bipedal)
   - Fields: urdf_path, mass_distribution, joint_limits, collision_geometry, sensor_attachments
   - Relationships: imported into Isaac Sim Scene; navigated by Nav2 stack
   - Validation: mass_distribution ±10% tolerance; collision_geometry must avoid self-collision

3. **Perception Pipeline** (data-model.md)
   - Represents Isaac ROS GPU-accelerated VSLAM
   - Fields: vslam_type (V-SLAM), depth_source (camera/depth_sensor), imu_source, output_odometry, gpu_compute_budget
   - Relationships: consumes camera/depth/IMU streams from sensors; produces odometry for Nav2
   - Validation: gpu_compute_budget ≤8GB VRAM; output_odometry frequency ≥10Hz

4. **Navigation Goal** (data-model.md)
   - Represents a path planning request with constraints
   - Fields: start_pose, goal_pose, costmap_resolution, planner_type, footstep_geometry, balance_constraints
   - Relationships: requested by Nav2 client; produces collision-free path
   - Validation: costmap_resolution ≤0.05m; path must avoid obstacles with 0.3m margin (humanoid footprint)

5. **Exercise Submission** (data-model.md - optional, exercise tracking only)
   - Represents student exercise results
   - Fields: student_id, exercise_id, code_submission, execution_output, metrics (error rate, execution time)
   - Relationships: associated with Chapter 7, 8, or 9 exercise
   - Validation: execution_output must match expected outputs within tolerance (5% for metrics)

### 1.2 API Contracts

Generated to `/contracts/` directory:

**Contract: Chapter 7 Examples** (`chapter-7-examples.yaml`)
- **7.1-installation-validation**: Input (Isaac Sim version), Output (installation report)
- **7.2-urdf-import**: Input (URDF file path), Output (scene JSON, visual/collision representation)
- **7.3-physics-tuning**: Input (gravity, friction coefficients), Output (simulation metrics)
- **7.4-sensor-simulation**: Input (camera config), Output (depth maps, RGB images)
- **7.5-synthetic-data-export**: Input (num_samples, output_format), Output (dataset directory)

**Contract: Chapter 8 Examples** (`chapter-8-examples.yaml`)
- **8.1-vslam-pipeline**: Input (depth stream), Output (odometry, visual map)
- **8.2-depth-perception**: Input (camera feed), Output (depth estimates, obstacles)
- **8.3-sensor-fusion**: Input (depth + IMU streams), Output (fused odometry, uncertainty estimates)
- **8.4-gpu-benchmarking**: Input (algorithm, hardware), Output (throughput, latency, GPU utilization)
- **8.5-custom-perception-node**: Input (ROS 2 topics), Output (custom perception output)
- **8.6-ros-isaac-integration**: Input (Isaac Sim scene, ROS 2 setup), Output (integrated environment)

**Contract: Chapter 9 Examples** (`chapter-9-examples.yaml`)
- **9.1-nav2-setup**: Input (robot URDF, environment), Output (Nav2 configuration, launch file)
- **9.2-bipedal-costmap**: Input (terrain map, robot footprint), Output (costmap with bipedal constraints)
- **9.3-global-planning**: Input (start, goal, costmap), Output (global path)
- **9.4-local-planning**: Input (local costmap, current pose), Output (velocity command)
- **9.5-obstacle-avoidance**: Input (sensor readings, navigation goal), Output (updated path)
- **9.6-sim-to-real-transfer**: Input (sim parameters, hardware config), Output (transfer checklist, validated)

### 1.3 Quickstart

Generated `quickstart.md`:
- **Section 1**: Installation checklist (Isaac Sim, Isaac ROS, Nav2, Ubuntu 22.04)
- **Section 2**: "Hello Isaac Sim" — first example (load scene, run 5 seconds, export data)
- **Section 3**: "Hello VSLAM" — depth-to-odometry pipeline
- **Section 4**: "Hello Nav2" — simple path planning
- **Section 5**: Cloud setup (AWS, NVIDIA Isaac Cloud)

### 1.4 Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` (or equivalent bash script if available):
- Add Isaac Sim 2023.8+ architecture overview
- Add Isaac ROS GPU-accelerated perception patterns
- Add Nav2 bipedal customization techniques
- Preserve existing Module 1-2 context

---

## Phase 2: Implementation Handoff

**Prerequisite**: Phase 1 complete (data-model.md, contracts/, quickstart.md, agent context updated)

### Next Command

Run `/sp.tasks` to generate detailed, dependency-ordered tasks.md with:
- Docusaurus chapter structure (markdown + MDX)
- Example implementation tasks (5 per chapter)
- Exercise implementation tasks (2 per chapter)
- Testing and validation tasks
- Documentation and RAG optimization tasks

---

## Success Criteria (from Specification)

| Criterion | Measurable Target | Plan Support |
|-----------|-------------------|--------------|
| **SC-001**: Error-free execution | All examples pass on Ubuntu 22.04 + ROS 2 Humble | CI/CD pipeline validates all code; Docker environment ensures reproducibility |
| **SC-002**: Synthetic data generation | 1000+ annotated images in <2 hours | Chapter 7 exercise 2 targets this; batching strategies for GPU memory limits |
| **SC-003**: GPU performance | 5x speedup; <5% localization error | Chapter 8 example 4 (GPU benchmarking) and exercise 1 validate metrics |
| **SC-004**: Planning success | 100% collision-free paths on 3+ obstacles | Chapter 9 examples/exercises validate on test scenarios |
| **SC-005**: Documentation coverage | 80-100 pages, IEEE citations, RAG-optimized | Docusaurus structure supports semantic chunking; all code examples cited |
| **SC-006**: Cloud parity | <10% performance variance | AWS g5.2xlarge and NVIDIA Isaac Cloud documented as equivalents; benchmarking scripts provided |
| **SC-007**: Module 4 foundation | Perception, sim-to-real, vision pipelines established | Chapter 8 (perception) and Chapter 9 (sim-to-real) lay groundwork; integration points documented |
| **SC-008**: Safety protocols | 100% of risks documented | Chapter 9 section 6 "Sim-to-Real Transfer & Safety" explicitly covers all known risks |

---

## Key Decisions & Rationale

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **Python 3.10+** as primary language | Dominates ML/robotics; most Isaac examples use Python; students familiar from Module 1-2 | C++ available for advanced SDK examples; JavaScript/Rust not suitable for real-time perception |
| **Docusaurus 3.x** for documentation | Supports MDX (interactive examples), semantic chunking for RAG, GitHub Pages deployment | Sphinx (ROS typical), ReadTheDocs (less customizable); Hugo (less modern) |
| **15-18 examples per module** (5-6 per chapter) | Balances coverage with student time budget (<4 hours/chapter); allows exercise repetition | 25+ examples (overwhelming); 5 total (insufficient depth) |
| **RTX 4070 Ti+ primary, cloud alternatives** | Primary GPU accessible to many CS/robotics labs; cloud ensures global accessibility | Cloud-only (eliminates hands-on debugging); CPU-only (infeasible for real-time perception) |
| **Isaac Sim 2023.8+** over older versions | Latest stable release with NVIDIA support; integrates with Isaac ROS 2.0+ | Older versions (Isaac Sim 2023.1) lack some perception nodes; newer beta versions risk breaking changes |
| **Sim-to-real transfer as protocol, not guarantee** | Honest about 80% success; emphasizes parameter sensitivity and domain randomization | Overselling 100% transfer (irresponsible); avoiding transfer entirely (reduces relevance) |

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Isaac Sim dependencies break on Ubuntu 22.04 LTS | Low | High (blocks all examples) | Docker image locks versions; CI/CD validates weekly; document fallback to cloud |
| GPU memory exhaustion during synthetic data gen | Medium | Medium (exercise 7.2 failure) | Implement batching; provide streaming alternative; document memory requirements |
| Nav2 bipedal planner unstable on custom robots | Medium | Medium (Chapter 9 exercises fail) | Test on standard robot (Boston Dynamics Atlas URDF); provide tuning guide |
| AWS/NVIDIA cloud quota limits or cost overruns | Low | Medium (student access blocked) | Document free tier limits; provide GPU benchmarking to predict costs; alert students |
| Sim-to-real transfer fails on non-idealized hardware | High | Low (noted in spec; Chapter 9 addresses) | Emphasize simulation-first approach; provide extensive parameter tuning guide |

---

## Dependencies & Prerequisites

**Internal Dependencies**:
- Module 1 (ROS 2 Fundamentals): Students must understand ROS 2 architecture, colcon, launch files
- Module 2 (Digital Twin/Gazebo): Students must understand URDF/SDF, simulation, basic physics
- Constitution: Module 3 must follow all constitutional principles (accuracy, hands-on, spec-driven, modular, safety)

**External Dependencies**:
- Ubuntu 22.04 LTS, Python 3.10+, ROS 2 Humble (pre-installed or cloud-provided)
- NVIDIA drivers 525+, CUDA 12.x, cuDNN 8.x (for GPU acceleration)
- Isaac Sim 2023.8+, Isaac ROS 2.0+, Nav2 Humble (installed via standard procedures)
- AWS account (optional; for g5.2xlarge) or NVIDIA Isaac Cloud account

---

## Timeline & Phases

**Phase 0 (Research)**: 1-2 days
- Resolve Isaac Sim/Isaac ROS/Nav2 unknowns
- Document sim-to-real protocols
- Consolidate cloud equivalence data

**Phase 1 (Design & Contracts)**: 2-3 days
- Finalize data model and API contracts
- Create quickstart guide
- Update agent context

**Phase 2 (Implementation)**: 7-10 days
- Run `/sp.tasks` to generate task breakdown
- Implement Docusaurus content + examples
- Develop exercises and test suites

**Phase 3 (Validation & Publishing)**: 3-5 days
- Run CI/CD; validate all examples
- Execute specification quality checklist
- Deploy to Docusaurus site

---

## Next Steps

1. ✅ **Phase 0 Research**: Generate `research.md` with findings on Isaac Sim, Isaac ROS, Nav2, cloud, and sim-to-real
2. ✅ **Phase 1 Design**: Create `data-model.md`, `/contracts/`, `quickstart.md`
3. ✅ **Update Agent Context**: Run context update script
4. **Phase 2 Tasks**: Run `/sp.tasks` to generate `tasks.md` with implementation breakdown
5. **Implementation**: Execute tasks; build Docusaurus content, examples, exercises
6. **Validation**: Run CI/CD; verify all success criteria met
7. **Publishing**: Merge to main; deploy to GitHub Pages
