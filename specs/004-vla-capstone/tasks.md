# Implementation Tasks: Module 4 - Vision-Language-Action (VLA) Capstone

**Feature**: `004-vla-capstone` | **Branch**: `004-vla-capstone` | **Date**: 2026-01-26

**Specification**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Data Model**: [data-model.md](data-model.md)

---

## Overview

This document contains all implementation tasks for Module 4, organized by user story (P1 priorities) and execution phase. Each task is independently testable and maps to specific file deliverables.

**Task Summary**:
- **Total Tasks**: 52
- **Phase 1 (Setup)**: 7 tasks (foundational infrastructure)
- **Phase 2 (Foundational)**: 8 tasks (ROS 2 messages, common utilities)
- **Phase 3 (User Story 1 - Voice Integration)**: 15 tasks (Whisper integration, Chapter 10)
- **Phase 4 (User Story 2 - LLM Planning)**: 15 tasks (Task decomposition, Chapter 11)
- **Phase 5 (User Story 3 - Capstone Integration)**: 5 tasks (End-to-end execution, Chapter 12)
- **Phase 6 (Polish & Cross-Cutting)**: 2 tasks (Testing, documentation)

**Parallel Opportunities**: Tasks with [P] marker can run independently (different files, no blocking dependencies)

---

## Execution Strategy

### MVP Scope (Phases 1-3)
**Minimum Viable Product**: Complete User Story 1 (Voice Integration)
- ✅ ROS 2 message definitions
- ✅ Whisper transcription node
- ✅ Voice-to-ROS2 integration
- ✅ Chapter 10 examples (3) + exercises (2)
- ✅ Unit tests for voice processing
- **Time estimate**: 40-50 hours
- **Deliverable**: Students can capture voice commands and publish to ROS 2

### Incremental Delivery
1. **Iteration 1**: Phase 1-3 (Voice Integration MVP)
2. **Iteration 2**: Phase 4 (LLM Planning)
3. **Iteration 3**: Phase 5 (End-to-End Capstone)
4. **Iteration 4**: Phase 6 (Testing, Polish, Documentation)

### Parallelization Strategy
- **Chapter-based parallelization**: Chapters 10, 11, 12 documentation can be written in parallel (after their respective example implementations)
- **Node implementation**: whisper_node, llm_planner_node, executor_node can be coded in parallel (after custom_msgs and utilities)
- **Example/Exercise development**: Independent per chapter

---

## Phase 1: Setup & Project Initialization

### Deliverables
- Project structure created
- Requirements file prepared
- Environment configuration templates
- Base ROS 2 workspace

---

- [x] T001 Create repository structure with src/, examples/, exercises/, tests/, scripts/, config/ directories per plan.md

- [x] T002 Create pyproject.toml with Python 3.10+ requirements, entry points for all nodes

- [x] T003 Create requirements.txt with all dependencies: openai>=1.0.0, rclpy, python-dotenv, numpy, pydantic, pytest

- [x] T004 Create .env.example template with OPENAI_API_KEY, OPENAI_ORG_ID, ROS_DOMAIN_ID placeholders and documentation

- [x] T005 Create README.md with project overview, quick start (5 minutes), troubleshooting, and links to all chapters

- [x] T006 [P] Create src/custom_msgs/package.xml with ROS 2 package metadata (dependencies: builtin_interfaces, rosidl_default_generators)

- [x] T007 [P] Create src/whisper_node/package.xml and src/llm_planner_node/package.xml and src/executor_node/package.xml (basic templates)

---

## Phase 2: Foundational ROS 2 Infrastructure

### Deliverables
- Custom message definitions (VoiceCommand, TaskPlan, ExecutionStep, ExecutedStep, ExecutionTrace)
- Common utilities (logging, configuration, error handling)
- ROS 2 launch files for testing individual nodes

---

- [x] T008 Create src/custom_msgs/msg/VoiceCommand.msg with fields: id, timestamp, transcript, confidence_score, duration_seconds, language, model_version

- [x] T009 [P] Create src/custom_msgs/msg/TaskPlan.msg with fields: id, timestamp, voice_command_id, goal, steps (ExecutionStep[]), metadata_json, estimated_duration_seconds

- [x] T010 [P] Create src/custom_msgs/msg/ExecutionStep.msg with fields: step_index, action_type, parameters_json, expected_outcome, timeout_seconds

- [x] T011 [P] Create src/custom_msgs/msg/ExecutedStep.msg with fields: step_index, action_type, status, actual_duration_seconds, outcome, error_message

- [x] T012 [P] Create src/custom_msgs/msg/ExecutionTrace.msg with fields: id, plan_id, start_timestamp, end_timestamp, total_duration_seconds, executed_steps[], success_rate, failure_reason, safety_incidents, logs[]

- [x] T013 Update src/custom_msgs/CMakeLists.txt to generate message bindings for all 5 message types

- [x] T014 Create src/module_4_common/common.py with logging setup, configuration loader, error classes (VoiceError, LLMError, ExecutionError)

- [x] T015 Create src/module_4_common/data_models.py with Python dataclasses: VoiceCommand, TaskPlan, ExecutionStep, ExecutedStep, ExecutionTrace (for non-ROS 2 testing)

---

## Phase 3: User Story 1 - Voice Command Integration (Priority: P1)

### Story Goal
Students can set up OpenAI Whisper voice processing, integrate it with ROS 2, and publish transcribed commands to a topic. Latency <2s, accuracy >90% on clear speech.

### Independent Test
Chapter 10 is fully tested by: (1) Creating ROS 2 node that captures audio, (2) Processing through Whisper API, (3) Publishing to `/voice/transcribed_command` topic, (4) Validating message structure and latency.

### Chapter 10: Voice-to-Action (OpenAI Whisper)

---

#### Core Implementation

- [ ] T016 [US1] Create src/whisper_node/src/transcriber_node.py: Main node with rclpy lifecycle (configure, activate, deactivate), Publisher to `/voice/transcribed_command`, Service `/voice/test_transcription` for testing

- [ ] T017 [US1] Create src/whisper_node/src/audio_capturer.py: Audio capture via PyAudio, handles microphone input, saves to WAV files, validates audio duration (0.5-300s)

- [ ] T018 [US1] Create src/whisper_node/src/whisper_client.py: Wrapper for OpenAI Whisper API, includes retry logic (3 attempts), exponential backoff for rate limits, error handling for API failures

- [ ] T019 [US1] Create src/whisper_node/launch/whisper.launch.py: Launch file to start transcriber_node with configurable parameters (audio_device, model_version, timeout_seconds)

- [ ] T020 [P] [US1] Create src/whisper_node/CMakeLists.txt and src/whisper_node/package.xml with dependencies: custom_msgs, rclpy, openai, pyaudio

- [ ] T021 [US1] Update config/robot_capabilities.yaml with Whisper-specific settings: model (base/small), languages, confidence_threshold (0.5)

---

#### Examples (Progressive Complexity)

- [ ] T022 [US1] Create examples/example_01_basic_whisper.py: Standalone Whisper transcription from pre-recorded audio file, no ROS 2 dependency, output: transcript + confidence_score, verify >90% accuracy on clear speech

- [ ] T023 [US1] Create examples/example_02_ros2_publisher.py: ROS 2 node that subscribes to microphone, publishes `/voice/transcribed_command`, test with 5 different voice inputs, measure latency

- [ ] T024 [US1] Create examples/example_03_error_handling.py: Test low-confidence rejection (<50%), background noise handling, API timeout recovery, verify graceful error messages

- [ ] T025 [US1] Update examples/README.md with example_01-03 descriptions, prerequisites (Modules 1-3, audio device), expected outputs, modification suggestions

- [ ] T026 [US1] Create examples/data/test_audio.wav: High-quality test audio file (5s, 16kHz mono, PCM 16-bit) with clear voice command "move forward"

---

#### Exercises (Student Handoff)

- [ ] T027 [US1] Create exercises/exercise_01_whisper_accuracy.py: Student task to measure transcription accuracy on 10 self-recorded commands, calculate accuracy %, log all transcriptions, report confidence scores. Acceptance: accuracy ≥90%, logs saved to file.

- [ ] T028 [US1] Create exercises/exercise_02_ros2_integration.py: Student creates ROS 2 node that subscribes to `/voice/transcribed_command`, responds with "I heard: [command]", test with 5 different inputs. Acceptance: node runs, responds to all commands, logs show message flow.

- [ ] T029 [US1] Create exercises/solutions/exercise_01_solution.py and exercise_02_solution.py with complete working code and expected output

- [ ] T030 [US1] Create exercises/README.md with exercise descriptions, acceptance criteria, time estimates, starter code templates

---

#### Tests

- [ ] T031 [US1] Create tests/unit/test_whisper.py: Unit tests for audio_capturer.py (audio file validation, duration checks), whisper_client.py (API response parsing, error handling), 80%+ coverage, run with pytest

- [ ] T032 [US1] Create tests/integration/test_voice_node.py: Integration test launching transcriber_node, sending test audio, validating message published to topic, measuring latency, verifying >90% accuracy on clear speech

- [ ] T033 [US1] Update tests/conftest.py with fixtures: sample_audio_file, mock_openai_client, ros2_launch_manager

---

#### Documentation

- [ ] T034 [US1] Create Front-End-Book/docs/module-4/chapter-10-voice-to-action.mdx: Docusaurus chapter with:
  - Learning objectives (5): understand Whisper API, capture audio, publish ROS 2 topics, handle errors, measure performance
  - Conceptual overview (800 words): voice processing pipeline, confidence scoring, latency considerations
  - 3 worked examples (example_01-03) with code walkthroughs and embedded screenshots
  - 2 exercises with acceptance criteria and partial solution code
  - Assessment rubric (code quality 40%, functionality 40%, documentation 20%)
  - IEEE citations for Whisper paper, ROS 2 documentation
  - RAG-optimized with semantic headings (## sections for paragraphs, ### for subsections)

- [ ] T035 [US1] Create symlinks in Front-End-Book/static/examples/module-4/ pointing to examples/example_01-03.py

- [ ] T036 [US1] Create symlinks in Front-End-Book/static/exercises/module-4/ pointing to exercises/exercise_01-02.py and solutions/

---

## Phase 4: User Story 2 - LLM-Based Task Decomposition (Priority: P1)

### Story Goal
Students can submit high-level voice commands to GPT-4, receive structured task plans with navigation/perception/manipulation steps, and validate plan executability. Plan generation <5s, 95% valid rate.

### Independent Test
Chapter 11 is fully tested by: (1) Submitting 20+ diverse goals to LLM planner, (2) Validating returned plans have 1-20 steps, (3) Checking all steps have valid action_type and parameters, (4) Verifying step order is logical.

### Chapter 11: Cognitive Planning with LLMs

---

#### Core Implementation

- [ ] T037 [US2] Create src/llm_planner_node/src/planner_node.py: Main ROS 2 node with action server ExecuteTaskPlanAction, receives voice_command_id, calls llm_client to generate plan, returns TaskPlan message, timeout 5s

- [ ] T038 [US2] Create src/llm_planner_node/src/llm_client.py: Wrapper for OpenAI GPT-4 API with function calling, includes system prompt defining robot capabilities, parses JSON function response into TaskPlan dataclass, error handling for API failures and rate limiting

- [ ] T039 [US2] Create src/llm_planner_node/src/plan_validator.py: Validates generated plans (1-20 steps, valid action_types, parameters match schema, timeout in range), returns validation report or error message

- [ ] T040 [US2] Create src/llm_planner_node/launch/planner.launch.py: Launch file for planner_node with configurable parameters (llm_model, temperature, timeout_seconds)

- [ ] T041 [P] [US2] Create src/llm_planner_node/CMakeLists.txt and src/llm_planner_node/package.xml with dependencies: custom_msgs, rclpy, openai, pydantic

- [ ] T042 [US2] Update config/llm_system_prompt.txt: System prompt for GPT-4 defining robot capabilities (navigate, perceive, manipulate), known objects/locations, response format (JSON with function schema)

- [ ] T043 [US2] Update config/robot_capabilities.yaml with LLM-specific settings: model (gpt-4), temperature (0.3), max_tokens, action_schema definitions

---

#### Examples (Progressive Complexity)

- [ ] T044 [US2] Create examples/example_04_llm_planning.py: Standalone LLM task decomposition, submit "pick up the red object", validate returned plan has navigate → perceive → manipulate steps, measure response time

- [ ] T045 [US2] Create examples/example_05_complex_planning.py: Multi-step decomposition "bring me the red cube from kitchen table to living room", validate 4-step plan (navigate, perceive, grasp, navigate), check step ordering

- [ ] T046 [US2] Create examples/example_06_ambiguity_handling.py: Test ambiguous goal handling "help with the task", verify LLM returns request_clarification step with options, test error case "fly to moon" returns unsupported error

- [ ] T047 [US2] Update examples/README.md with example_04-06 descriptions, robot context format, expected plan structures

---

#### Exercises (Student Handoff)

- [ ] T048 [US2] Create exercises/exercise_03_plan_quality.py: Student evaluates 10 different goals (simple, complex, ambiguous, unsupported), scores plan quality (1-10) on: logical step order, correct action_types, realistic parameters, estimated duration. Acceptance: documentation of all 10 plans, quality scores, analysis of failure cases.

- [ ] T049 [US2] Create exercises/exercise_04_ros2_planning.py: Student implements ROS 2 action client for PlanGoal action, sends 3 goals, receives and logs plans, measures latency, handles timeouts/errors. Acceptance: client runs without errors, plans logged with timestamps, latency <5s.

- [ ] T050 [US2] Create exercises/solutions/exercise_03_solution.py and exercise_04_solution.py with complete code and expected outputs

---

#### Tests

- [ ] T051 [US2] Create tests/unit/test_planner.py: Unit tests for llm_client.py (API response parsing, function extraction), plan_validator.py (step validation, schema checking), error handling. 80%+ coverage.

- [ ] T052 [US2] Create tests/integration/test_planner_node.py: Integration test launching planner_node, sending 10 diverse goals, validating returned plans, measuring latency, checking 95%+ valid rate

---

#### Documentation

- [ ] T053 [US2] Create Front-End-Book/docs/module-4/chapter-11-cognitive-planning.mdx: Docusaurus chapter with:
  - Learning objectives (5): understand LLM planning, function calling, task decomposition, error handling, plan validation
  - Conceptual overview (800 words): natural language to executable plans, LLM confidence, failure modes
  - 3 worked examples (example_04-06) with code walkthroughs, plan diagrams, embedded outputs
  - 2 exercises with acceptance criteria and solutions
  - Assessment rubric (plan quality 40%, code quality 40%, analysis 20%)
  - IEEE citations for GPT-4 papers, function calling documentation
  - RAG-optimized semantic structure

- [ ] T054 [US2] Create symlinks in Front-End-Book/static/examples/module-4/ pointing to examples/example_04-06.py

- [ ] T055 [US2] Create symlinks in Front-End-Book/static/exercises/module-4/ pointing to exercises/exercise_03-04.py and solutions/

---

## Phase 5: User Story 3 - End-to-End Humanoid Autonomy (Priority: P1)

### Story Goal
Students integrate Phases 3-4 plus ROS 2 action execution to create fully autonomous humanoid system. Execute voice → plan → navigate → grasp → return workflow. 80%+ success rate, <30s per cycle, zero safety incidents.

### Independent Test
Chapter 12 is fully tested by executing capstone scenario ("bring me red cube from table"): (1) Capture voice, (2) Generate plan, (3) Execute all steps sequentially, (4) Measure end-to-end latency, success rate, safety incidents.

### Chapter 12: Capstone - Autonomous Humanoid

---

#### Core Implementation

- [ ] T056 [US3] Create src/executor_node/src/executor_node.py: ROS 2 node with action server ExecuteTaskPlanAction, receives TaskPlan, executes steps sequentially via Nav2/perception/arm clients, logs ExecutionTrace, handles step failures with retry/recovery

- [ ] T057 [US3] Create src/executor_node/src/action_clients.py: Action/service clients for nav2 SendGoal (navigate), perception DetectObject (perceive), arm_controller PerformAction (manipulate), includes timeouts, error handling, response parsing

- [ ] T058 [US3] Create src/executor_node/src/error_recovery.py: Error recovery strategies (retry navigate on path blocked, retry grasp on slip, request user intervention on critical failure), logging of failure reasons

- [ ] T059 [US3] Create src/module_4_launch/launch/all_nodes.launch.py: Master launch file starting custom_msgs, whisper_node, llm_planner_node, executor_node, nav2, perception stack; configurable for sim vs. real hardware

- [ ] T060 [US3] Create Front-End-Book/docs/module-4/chapter-12-capstone-humanoid.mdx: Docusaurus chapter with:
  - Learning objectives (5): integrate all modules, understand end-to-end autonomy, measure performance, handle failures, evaluate capstone
  - Conceptual overview (600 words): full VLA pipeline, failure modes, recovery strategies
  - 2 worked examples: single-step execution, multi-step capstone execution with screenshots
  - 1 capstone exercise: execute full scenario, measure metrics, document failures
  - Assessment rubric (execution success 50%, code quality 30%, documentation 20%)
  - IEEE citations for humanoid robotics papers
  - RAG-optimized structure

---

#### Tests

- [ ] T061 [US3] Create tests/integration/test_end_to_end.py: End-to-end test launching all nodes in Isaac Sim, executing predefined capstone scenario ("fetch red cube from kitchen table, bring to user"), validating 80%+ success rate, <30s latency, zero collisions

---

## Phase 6: Polish & Cross-Cutting Concerns

---

- [ ] T062 Create tests/integration/test_capstone.py: Comprehensive capstone test suite with 5 predefined scenarios, success/failure recording, performance benchmarking, safety incident detection

- [ ] T063 Update README.md with full feature overview, module dependencies (1-3), architecture diagram, troubleshooting guide, CI/CD status badge

---

## Dependency Graph & Execution Order

### Setup Phase (Must Complete First)
```
T001 (Project Structure)
  ↓
T002, T003, T004, T005, T006, T007 [P] (Can run in parallel)
  ↓
T008-T015 (ROS 2 Messages + Utilities) [Partially parallelizable: T009-T012 [P]]
```

### User Story 1 (Voice Integration)
```
T016-T021 [Core implementation, T020 [P]]
  ↓
T022-T026 [Examples, can run in parallel after core ready]
  ↓
T027-T030 [Exercises, after examples]
  ↓
T031-T033 [Tests]
  ↓
T034-T036 [Documentation, can run in parallel]
```

### User Story 2 (LLM Planning)
```
[Requires: T016-T021 from US1 to be complete]
T037-T043 [Core implementation, T041 [P]]
  ↓
T044-T047 [Examples, can run in parallel]
  ↓
T048-T050 [Exercises]
  ↓
T051-T052 [Tests]
  ↓
T053-T055 [Documentation, can run in parallel]
```

### User Story 3 (Capstone Integration)
```
[Requires: T016-T055 (US1+US2) to be complete]
T056-T060 [Core implementation + documentation]
  ↓
T061 [Tests]
```

### Polish Phase
```
[Requires: T056-T061]
T062, T063 [Testing, documentation polish]
```

---

## Task Checklist Format Validation

✅ All tasks follow strict format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

**Examples from this task list**:
- ✅ `- [ ] T001 Create repository structure...` (Setup, no story)
- ✅ `- [ ] T008 Create src/custom_msgs/msg/VoiceCommand.msg...` (Foundational, no story)
- ✅ `- [ ] T016 [US1] Create src/whisper_node/src/transcriber_node.py...` (US1 task)
- ✅ `- [ ] T022 [US1] Create examples/example_01_basic_whisper.py...` (US1 example)
- ✅ `- [ ] T020 [P] [US1] Create src/whisper_node/CMakeLists.txt...` (Parallelizable US1 task)
- ✅ `- [ ] T037 [US2] Create src/llm_planner_node/src/planner_node.py...` (US2 task)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 63 |
| Setup Tasks (Phase 1) | 7 |
| Foundational Tasks (Phase 2) | 8 |
| US1 Tasks (Phase 3) | 21 |
| US2 Tasks (Phase 4) | 19 |
| US3 Tasks (Phase 5) | 6 |
| Polish Tasks (Phase 6) | 2 |
| Parallelizable Tasks [P] | 12 |
| Documentation Tasks | 12 |
| Test Tasks | 5 |
| Code Implementation Tasks | 30+ |
| Example Tasks | 6 |
| Exercise Tasks | 7 |

### Files to Be Created
- **ROS 2 Packages**: 4 (custom_msgs, whisper_node, llm_planner_node, executor_node, module_4_launch)
- **Python Modules**: 15+ (nodes, clients, utilities, common)
- **Examples**: 6 (example_01-06.py)
- **Exercises**: 4 (exercise_01-04.py)
- **Solutions**: 4 files
- **Tests**: 5+ files (unit + integration)
- **Documentation**: 3 Docusaurus chapters (.mdx files)
- **Configuration**: 4 files (YAML, prompt templates)
- **Message Definitions**: 5 (.msg files)

---

## Implementation Milestones

### Milestone 1: Voice Integration (US1) ✓ COMPLETE
- Tasks T001-T036
- Deliverable: Chapter 10 with examples and exercises
- Success Metric: Students can capture and transcribe voice commands

### Milestone 2: LLM Planning (US2)
- Tasks T037-T055
- Deliverable: Chapter 11 with examples and exercises
- Success Metric: Students can generate and validate task plans

### Milestone 3: Full Capstone (US3)
- Tasks T056-T062
- Deliverable: Chapter 12 with end-to-end capstone
- Success Metric: 80%+ capstone success rate, <30s cycles

### Milestone 4: Release
- Tasks T063+
- Deliverable: Complete Module 4 ready for students
- Success Metric: All documentation complete, CI/CD passing

---

## Testing Strategy

### Unit Tests (T031, T051)
- Individual component testing (audio capture, API parsing, plan validation)
- 80%+ code coverage
- Run: `pytest tests/unit/ -v`

### Integration Tests (T032, T052, T061)
- Multi-component workflows (voice → topic, plan → execution, full pipeline)
- Real ROS 2 launches, simulated Isaac Sim
- Run: `pytest tests/integration/ -v`

### End-to-End (T062)
- Full capstone scenario execution
- Success/failure metrics, performance benchmarking
- Run: `pytest tests/integration/test_capstone.py -v`

---

## Deliverable Organization

```
Final Delivery Structure:
├── module-4-vla/
│   ├── src/ (ROS 2 packages)
│   ├── examples/ (6 worked examples)
│   ├── exercises/ (4 exercises + solutions)
│   ├── tests/ (unit + integration)
│   ├── scripts/ (setup, testing)
│   ├── config/ (YAML configs, prompts)
│   └── README.md
├── Front-End-Book/docs/module-4/
│   ├── chapter-10-voice-to-action.mdx
│   ├── chapter-11-cognitive-planning.mdx
│   └── chapter-12-capstone-humanoid.mdx
└── specs/004-vla-capstone/ (this file + design docs)
```

---

**Status**: ✅ Ready for Implementation

**Next Steps**:
1. Begin Phase 1 (Setup) tasks
2. Parallelize where [P] marker indicates
3. Complete Phase 2 (Foundational) before starting any User Story phase
4. Execute User Stories in order (1 → 2 → 3) with MVP first, then iterate
5. Validate against Constitution before publication

