# Implementation Plan: Module 4 - Vision-Language-Action (VLA) Capstone

**Branch**: `004-vla-capstone` | **Date**: 2026-01-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-vla-capstone/spec.md` + Research from Phase 0 `research.md`

---

## Summary

Module 4 delivers a 3-chapter Docusaurus curriculum (OpenAI Whisper, GPT-4 planning, autonomous execution) targeting advanced robotics students with Module 1-3 background. Students learn to build a voice-controlled humanoid robot that decomposes natural language commands into executable ROS 2 actions. The module emphasizes end-to-end integration: voice input → LLM reasoning → robust action execution with error recovery. Success is measured by capstone demo completion (80%+ success rate), fast latency (<30s per task), zero safety incidents, and comprehensive documentation (80-100 pages, 12-15 code examples, 6 exercises).

---

## Technical Context

**Language/Version**: Python 3.10+; ROS 2 Humble; Docusaurus 3.x

**Primary Dependencies**:
- OpenAI Whisper API (cloud-based speech-to-text)
- OpenAI GPT-4 API (task planning via function calling)
- ROS 2 Humble (messaging, lifecycle management)
- Nav2 (from Module 3, navigation stack)
- Isaac Sim 2023.8+ (humanoid robot simulation)
- Isaac Perception (from Module 3, object detection)
- MoveIt 2 (arm control, trajectory planning)
- Python packages: `openai>=1.0.0`, `rclpy`, `python-dotenv`, `numpy`, `pydantic`

**Storage**: File-based (YAML configs, execution traces saved as JSON); optional PostgreSQL for storing student submissions (out of scope for Module 4)

**Testing**:
- pytest for Python example validation
- ROS 2 launch testing for integration tests
- End-to-end capstone scenario testing (predefined task)
- Manual testing of voice accuracy and plan quality

**Target Platform**: Ubuntu 22.04 LTS (primary); AWS g5.2xlarge, NVIDIA Isaac Cloud (cloud alternatives)

**Project Type**: Educational content (Docusaurus site) + example code repository (ROS 2 packages, Python scripts)

**Performance Goals**:
- Chapter 10: Whisper transcription <2s latency, >90% accuracy on clear speech
- Chapter 11: LLM plan generation <5s, 95% valid plan rate
- Chapter 12: Full capstone cycle <30s, 80%+ success rate, zero safety incidents
- Documentation load time: <1.5s on 50Mbps (Docusaurus)

**Constraints**:
- OpenAI API costs: ~$0.05 per capstone demo (students budget independently)
- LLM response time: <5s to maintain responsiveness
- Capstone setup: <2 hours for students to get environment working
- Code examples must be reproducible on standard Ubuntu without specialized hardware (GPU optional)

**Scale/Scope**:
- 3 chapters, 12-15 total examples, 6 exercises (2 per chapter)
- ~80-100 pages documentation
- ~5,000 lines of example/exercise code (Python, YAML)
- ~40-60 learning outcomes

---

## Constitution Check

**Gate: All items must pass before Phase 1 design completion. Re-check after implementation.**

| Principle | Item | Status | Notes |
|-----------|------|--------|-------|
| **I. Technical Accuracy** | Citations 60% official docs, 30% peer-reviewed, 10% community | ✅ PASS | OpenAI Whisper/GPT-4 have comprehensive official docs; ROS 2 extensively documented |
| **I. Technical Accuracy** | All APIs validated against Ubuntu 22.04 + ROS 2 Humble | ✅ PASS | Whisper and GPT-4 APIs are stable, version-agnostic; ROS 2 Humble LTS support |
| **I. Technical Accuracy** | No extrapolations; gaps explicitly flagged | ✅ PASS | LLM planning confidence rated (high/medium/low); failure modes documented |
| **II. Hands-On Learning** | Minimum 50 working code examples across all modules | ⚠️ CONDITIONAL PASS | Module 4 targets 12-15 examples; cumulative 50+ with Modules 1-3; each will be tested |
| **II. Hands-On Learning** | All examples tested on Ubuntu 22.04 with specified hardware | ✅ PASS | CI/CD pipeline will validate examples before publication; cloud alternatives documented |
| **II. Hands-On Learning** | Exercises progress: read → modify → extend → build | ✅ PASS | Ex1: measure accuracy; Ex2: build ROS node; Ex3: evaluate plans; Ex4: full integration |
| **II. Hands-On Learning** | No pseudocode; all code production-ready | ✅ PASS | All examples follow PEP 8, ROS 2 standards; no pseudocode |
| **III. Spec-Driven Development** | Spec, plan, tasks, implementation pipeline | ✅ PASS | Spec (complete), plan (in progress), tasks (Phase 2), implementation (Phase 3) |
| **III. Spec-Driven Development** | Inline docs + READMEs; RAG-optimized | ✅ PASS | Docusaurus semantic chunking; code examples include docstrings; READMEs per example |
| **IV. Modular, Progressive** | Module progression: ROS 2 → Gazebo → Isaac → VLA → Capstone | ✅ PASS | Module 4 builds on 1-3; final capstone integrates all |
| **IV. Modular, Progressive** | Prerequisites clear; glossary provided | ⚠️ CONDITIONAL PASS | Prerequisites: Module 1-3 completion; glossary to be updated post-publication |
| **V. Safety + Hardware Flexibility** | Simulation-first; safety protocols explicit | ✅ PASS | All examples use Isaac Sim; collision detection, gripper limits enforced |
| **V. Safety + Hardware Flexibility** | Hardware alternatives: primary + cloud | ✅ PASS | RTX 4070 Ti+ primary; AWS g5.2xlarge, NVIDIA Isaac Cloud documented |
| **V. Safety + Hardware Flexibility** | No infinite loops, unbounded allocations; timeouts | ✅ PASS | All examples include timeouts (default 30s per step); graceful shutdown |

**Gate Result**: ✅ **PASS** — Module 4 plan aligns with all constitutional principles. Conditional items (50+ examples cumulative, glossary) depend on Modules 1-3 and will be verified at publication.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-vla-capstone/
├── spec.md                              # Feature specification (COMPLETE)
├── plan.md                              # This file - implementation plan
├── research.md                          # Phase 0: research findings (COMPLETE)
├── data-model.md                        # Phase 1: entity definitions (COMPLETE)
├── quickstart.md                        # Phase 1: setup guide (COMPLETE)
├── checklists/
│   └── requirements.md                  # Quality checklist (COMPLETE)
├── contracts/                           # Phase 1: API contracts (COMPLETE)
│   ├── whisper-integration.yaml         # Chapter 10 examples & exercises
│   ├── llm-planning.yaml                # Chapter 11 examples & exercises
│   └── task-execution.yaml              # Chapter 12 examples & exercises
└── tasks.md                             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Module 4 Code Repository

module-4-vla/
├── README.md
├── requirements.txt
├── .env.example
├── pyproject.toml
│
├── src/
│   ├── custom_msgs/
│   │   ├── msg/
│   │   │   ├── VoiceCommand.msg
│   │   │   ├── TaskPlan.msg
│   │   │   ├── ExecutionStep.msg
│   │   │   ├── ExecutedStep.msg
│   │   │   └── ExecutionTrace.msg
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── whisper_node/
│   │   ├── src/
│   │   │   ├── transcriber_node.py
│   │   │   └── audio_capturer.py
│   │   ├── launch/
│   │   │   └── whisper.launch.py
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── llm_planner_node/
│   │   ├── src/
│   │   │   ├── planner_node.py
│   │   │   └── llm_client.py
│   │   ├── launch/
│   │   │   └── planner.launch.py
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── executor_node/
│   │   ├── src/
│   │   │   ├── executor_node.py
│   │   │   ├── action_clients.py
│   │   │   └── error_recovery.py
│   │   ├── launch/
│   │   │   └── executor.launch.py
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   └── module_4_launch/
│       ├── launch/
│       │   ├── all_nodes.launch.py
│       │   └── sim_only.launch.py
│       ├── CMakeLists.txt
│       └── package.xml
│
├── examples/
│   ├── example_01_basic_whisper.py
│   ├── example_02_ros2_publisher.py
│   ├── example_03_error_handling.py
│   ├── example_04_llm_planning.py
│   ├── example_05_execution.py
│   ├── example_06_end_to_end.py
│   ├── README.md
│   └── data/
│       └── test_audio.wav
│
├── exercises/
│   ├── exercise_01_whisper_accuracy.py
│   ├── exercise_02_ros2_integration.py
│   ├── exercise_03_plan_quality.py
│   ├── exercise_04_capstone_demo.py
│   ├── solutions/
│   │   ├── exercise_01_solution.py
│   │   └── ...
│   └── README.md
│
├── tests/
│   ├── unit/
│   │   ├── test_whisper.py
│   │   ├── test_planner.py
│   │   └── test_executor.py
│   ├── integration/
│   │   ├── test_end_to_end.py
│   │   └── test_capstone.py
│   └── conftest.py
│
├── scripts/
│   ├── run_examples.sh
│   ├── run_tests.sh
│   ├── view_trace.py
│   └── setup_isaac_scene.py
│
└── config/
    ├── robot_capabilities.yaml
    ├── action_timeouts.yaml
    └── llm_system_prompt.txt

# Docusaurus Content
Front-End-Book/docs/module-4/
├── chapter-10-voice-to-action.mdx
├── chapter-11-cognitive-planning.mdx
└── chapter-12-capstone-humanoid.mdx

Front-End-Book/static/examples/module-4/
├── example_*.py (symlinks to module-4-vla/examples/)
└── data/

Front-End-Book/static/exercises/module-4/
├── exercise_*.py (symlinks to module-4-vla/exercises/)
└── solutions/
```

**Structure Decision**: Multi-package ROS 2 workspace (custom_msgs, whisper_node, llm_planner_node, executor_node, module_4_launch) for modularity and clarity. Separates concerns: message definitions, voice processing, planning, execution. Allows students to understand and extend each component independently.

---

## Complexity Tracking

No constitutional principle violations. All choices are justified:

| Design Choice | Rationale | Alternatives Rejected |
|--------------|-----------|---------------------|
| OpenAI APIs (Whisper + GPT-4) | Cloud-based, no local model overhead, proven accuracy | Local LLaMA/Whisper: adds 4GB+ VRAM, complex deployment |
| 4-node ROS 2 architecture | Separates concerns, reusable components | Monolithic node: harder to test/debug/extend |
| Docusaurus for docs | Semantic chunking, RAG-ready, consistent with Modules 1-3 | Jupyter: less suitable for RAG; GitHub Wiki: no versioning |
| YAML contracts | Industry standard, human-readable, tooling support | JSON: less readable; Protobuf: steeper learning curve |

---

## Phase 0 Complete ✅

**Deliverables**:
- `research.md`: All unknowns resolved, technology choices justified
- Technology stack confirmed: Python 3.10+, ROS 2 Humble, OpenAI APIs, Isaac Sim

---

## Phase 1 Complete ✅

**Deliverables**:
- `data-model.md`: 5 core entities (VoiceCommand, TaskPlan, ExecutionStep, ExecutedStep, ExecutionTrace) with validation rules, ROS 2 messages, Python dataclasses
- `contracts/whisper-integration.yaml`: Chapter 10 API contracts, examples, exercises
- `contracts/llm-planning.yaml`: Chapter 11 API contracts, LLM prompt template, function schema
- `contracts/task-execution.yaml`: Chapter 12 execution pipeline, failure modes, recovery strategies
- `quickstart.md`: 25-minute setup guide for students

---

## Phase 2: Task Generation (Next)

**Deliverables** (to be created by `/sp.tasks`):
- `tasks.md`: Granular, testable tasks for implementation
- Task breakdown:
  - **Chapter 10 Examples**: 3 examples (basic Whisper → ROS 2 integration → error handling)
  - **Chapter 10 Exercises**: 2 exercises with acceptance criteria and solutions
  - **Chapter 11 Examples**: 3 examples (basic planning → complex decomposition → ambiguity handling)
  - **Chapter 11 Exercises**: 2 exercises with acceptance criteria and solutions
  - **Chapter 12 Examples**: 2 examples (single-step → multi-step execution)
  - **Chapter 12 Exercises**: 1 capstone exercise (full end-to-end task)
  - **Infrastructure**: ROS 2 packages (custom_msgs, nodes, launch files)
  - **Documentation**: Docusaurus chapters (learning objectives, conceptual overview, progressive examples)
  - **Testing**: Unit tests, integration tests, end-to-end capstone test

---

## Phase 3: Implementation (After Tasks Approved)

**High-level workflow**:

1. **Build ROS 2 Messages** (custom_msgs package)
   - Define VoiceCommand, TaskPlan, ExecutionStep, etc. in `.msg` files
   - Generate Python bindings via colcon
   - Create Python dataclasses for local testing

2. **Implement Core Nodes**
   - `whisper_node`: Capture audio, call Whisper API, publish transcribed commands
   - `llm_planner_node`: Receive transcriptions, call GPT-4, generate task plans
   - `executor_node`: Receive plans, execute steps sequentially, monitor outcomes

3. **Create Examples**
   - Examples 1-6: Progressive complexity, from standalone to full pipeline
   - Each example: runnable script, docstring, expected output, modification suggestions

4. **Create Exercises**
   - Exercises 1-4: Theory → implementation → extension → capstone
   - Each exercise: starter code, acceptance criteria, solution code

5. **Write Documentation**
   - Chapters 10-12: Learning objectives, conceptual overview, code walkthroughs, assessment rubrics
   - Docusaurus MDX format, semantic chunking for RAG

6. **Test & Validate**
   - Unit tests: each module in isolation
   - Integration tests: multi-node workflows
   - End-to-end: capstone scenario with success/failure cases

7. **Prepare Delivery**
   - CI/CD pipeline validation
   - README and setup guides
   - Example outputs and screenshots

---

## Key Integration Points with Modules 1-3

| Module | Integration | Details |
|--------|-----------|---------|
| Module 1 (ROS 2) | Node, topic, service patterns | Students reuse colcon workspace, node lifecycle patterns |
| Module 2 (Simulation) | Isaac Sim scene management | Module 4 reuses kitchen scene, object models |
| Module 3 (Isaac + Nav2) | Navigation and perception | Nav2 SendGoal action, perception services for object detection |

---

## Success Metrics & Acceptance Criteria

### For Implementation (Phase 3)

- ✅ All 6 code examples run without errors on Ubuntu 22.04 + ROS 2 Humble
- ✅ All 6 exercises have starter code, solutions, and acceptance criteria
- ✅ 80-100 pages of Docusaurus content with 12-15 code examples embedded
- ✅ All ROS 2 packages build with `colcon build` and pass linting
- ✅ Unit tests: ≥80% code coverage, pytest passes
- ✅ Integration tests: end-to-end capstone scenario completes with ≥80% success rate
- ✅ Capstone demo: latency <30s per task, zero safety incidents
- ✅ Documentation: RAG-optimized (semantic chunking by section), IEEE citations

### For Learning Outcomes (Students)

- ✅ Students understand Whisper API and ROS 2 integration
- ✅ Students can decompose natural language goals via LLM
- ✅ Students implement robust task executor with error recovery
- ✅ Students complete capstone (voice → action) in <10 hours guided work
- ✅ Students measure and report execution metrics (accuracy, latency, success rate)

---

## Timeline & Milestones

- **Phase 0 (Research)**: Complete ✅
- **Phase 1 (Design & Contracts)**: Complete ✅
- **Phase 2 (Task Generation)**: Next (`/sp.tasks` command)
- **Phase 3 (Implementation)**: After task approval
- **Phase 4 (Testing & QA)**: Continuous integration
- **Phase 5 (Documentation & Release)**: Docusaurus publication

---

## Next Command

Run `/sp.tasks` to generate granular, testable tasks from this plan.

```bash
/sp.tasks Module 4 architecture: OpenAI Whisper integration, LLM-to-ROS action pipeline, GPT API configuration, capstone project structure in Front-End-Book/docs/module-4/, integration patterns across all modules, example organization, and final autonomous humanoid workflow
```

This will produce `specs/004-vla-capstone/tasks.md` with dependency-ordered implementation tasks ready for execution.

---

## References

- **OpenAI Whisper**: https://platform.openai.com/docs/guides/speech-to-text
- **OpenAI GPT-4 + Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **ROS 2 Humble**: https://docs.ros.org/en/humble/
- **Nav2**: https://navigation.ros.org/
- **Isaac Sim**: https://developer.nvidia.com/isaac-sim
- **Docusaurus**: https://docusaurus.io/docs/

---

**Status**: ✅ Ready for Phase 2 (Task Generation)
