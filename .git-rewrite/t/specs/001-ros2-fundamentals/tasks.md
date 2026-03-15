---
description: "Task list for Module 1 - ROS 2 Fundamentals implementation"
---

# Tasks: Module 1 - ROS 2 Fundamentals

**Input**: Design documents from `/specs/001-ros2-fundamentals/`
**Prerequisites**: plan.md ✅, spec.md ✅, clarifications ✅
**Branch**: `001-ros2-fundamentals`

**Organization**: Tasks grouped by user story (4 P1/P2 stories) + foundational setup. Each story is independently implementable and testable.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Task can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4)
- All file paths are absolute from repository root

---

## Phase 1: Setup & Infrastructure

**Purpose**: Project initialization, Docusaurus setup, tooling configuration

- [ ] T001 Initialize Docusaurus 3.x project with npx create-docusaurus@latest Front-End-Book classic
- [ ] T002 [P] Create project directory structure per plan.md: `docs/`, `examples/`, `exercises/`, `scripts/`, `tests/`
- [ ] T003 [P] Create configuration files: `.flake8`, `pytest.ini`, `.github/workflows/ci.yml`
- [ ] T004 [P] Setup GitHub Actions CI/CD pipeline for code validation and documentation build
- [ ] T005 Create `docs/index.md` with Module 1 landing page and navigation structure
- [ ] T006 [P] Create setup and validation scripts:
  - `scripts/install-ros2-humble.sh` (Ubuntu 22.04 installation)
  - `scripts/setup-colcon-workspace.sh` (workspace initialization)
  - `scripts/verify-installation.sh` (verification script)
  - `scripts/validate-examples.sh` (run all examples and tests)
- [ ] T007 Create `examples/README.md` with example index and setup instructions
- [ ] T008 Create `tests/conftest.py` with pytest fixtures for ROS 2 testing (mocks, environment setup)

**Checkpoint**: Project structure ready; Docusaurus buildable; CI/CD pipeline operational

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Content infrastructure and shared resources needed by all stories

**⚠️ CRITICAL**: No chapter content can begin until this phase completes

- [ ] T009 Create `docs/module-1/intro.md` with module overview, learning objectives, prerequisites, time estimates
- [ ] T010 [P] Create `docs/module-1/glossary.md` with ROS 2 terminology reference (nodes, topics, services, actions, URDF, etc.)
- [ ] T011 Create `docs/module-1/assessments/` directory structure with quiz and mini-project templates
- [ ] T012 Create citation style guide and bibliography template for IEEE format validation
- [ ] T013 [P] Setup content quality test suite in `tests/test_content_quality.py`:
  - IEEE citation format validation
  - Flesch-Kincaid readability level check (target: 12-14)
  - Markdown structure validation (heading hierarchy, code blocks)
  - Spelling and grammar checks
- [ ] T014 Create content metadata schema documentation (`specs/001-ros2-fundamentals/contracts/chapter-structure.json`)
- [ ] T015 Create code example metadata schema (`specs/001-ros2-fundamentals/contracts/code-example-format.json`)
- [ ] T016 Create exercise metadata schema (`specs/001-ros2-fundamentals/contracts/exercise-format.json`)

**Checkpoint**: Content infrastructure ready; quality checks operational; all chapters can now be authored

---

## Phase 3: User Story 1 - Understand ROS 2 Core Architecture (Priority: P1) 🎯

**Goal**: Students understand ROS 2 fundamentals (nodes, topics, pub/sub) and can run working examples

**Independent Test**: Student reads Chapter 1, runs "Hello World" publisher/subscriber example, modifies code, passes Exercise 1.1 automated tests

### Chapter 1 Implementation: ROS 2 Architecture

- [ ] T017 Write `docs/module-1/chapter-1.md` with learning objectives, content outline:
  - Section 1: What is ROS 2? (history, use cases, comparison to ROS 1)
  - Section 2: Nodes - Computational units (definition, lifecycle, creation in Python)
  - Section 3: Topics - Publish-Subscribe communication (async, many-to-many, topic list/echo/info)
  - Section 4: Publishers and Subscribers (rclpy API, message types, QoS settings)
  - Section 5: Running and Visualizing ROS 2 (graphing, ros2 CLI tools)
  - Inline code examples with proper citations

- [ ] T018 [P] Create code examples for Chapter 1:
  - [ ] T018a Create `examples/1-hello-world-pub.py` - Working publisher node (publishes "Hello World" to topic)
  - [ ] T018b Create `examples/1-hello-world-sub.py` - Working subscriber node (receives and prints messages)
  - [ ] T018c Create `examples/1-topic-introspection.sh` - Shell script demonstrating `ros2 topic list`, `echo`, `info`

- [ ] T019 [P] Write tests for Chapter 1 code examples in `tests/test_chapter_1.py`:
  - Test publisher node initializes and publishes to correct topic
  - Test subscriber node initializes and receives messages
  - Test message format matches specification
  - Test CLI tools work correctly
  - All tests use ROS 2 testing patterns (mocks, fixtures from conftest.py)

- [ ] T020 [P] Create Exercise 1.1 in `exercises/1-1-create-publisher/`:
  - [ ] T020a Write `exercises/1-1-create-publisher/README.md`:
    - Problem: Create a ROS 2 publisher node that publishes integer counter to `counter_topic` every 1 second
    - Learning objectives: Understand nodes, publishers, message types, rclpy API
    - Acceptance criteria: Node runs, publishes on correct topic, messages have correct type and frequency
    - Estimated time: 20-30 minutes
  - [ ] T020b Write `exercises/1-1-create-publisher/solution.py` (reference implementation)
  - [ ] T020c Write `exercises/1-1-create-publisher/test_solution.py` (pytest acceptance tests)

- [ ] T021 [P] Create Exercise 1.2 in `exercises/1-2-modify-subscriber/`:
  - [ ] T021a Write `exercises/1-2-modify-subscriber/README.md`:
    - Problem: Create subscriber that listens to `counter_topic`, filters even numbers, prints to console
    - Learning objectives: Understand subscribers, callbacks, filtering logic
    - Acceptance criteria: Subscriber runs, receives messages, filters correctly, no crashes
    - Estimated time: 25-30 minutes
  - [ ] T021b Write `exercises/1-2-modify-subscriber/solution.py` (reference implementation)
  - [ ] T021c Write `exercises/1-2-modify-subscriber/test_solution.py` (pytest acceptance tests)

- [ ] T022 Create `docs/module-1/assessments/quiz-1.md`:
  - 10-15 questions on Chapter 1 concepts (nodes, topics, pub/sub, CLI tools)
  - Mix of multiple choice and short answer
  - Answer key for instructors

**Checkpoint**: Chapter 1 complete with 3 working code examples, 2 exercises with tests, formative quiz. Story 1 is independently testable.

---

## Phase 4: User Story 2 - Set Up Development Environment (Priority: P1)

**Goal**: Students can install ROS 2 Humble on Ubuntu 22.04, create colcon workspace, build packages

**Independent Test**: Student follows installation script, verifies installation with `ros2 --version`, creates workspace with colcon, builds example package successfully

### Chapter 0 Implementation: Setup & Installation

- [ ] T023 Write `docs/module-1/chapter-0-setup.md` (supplementary chapter):
  - Section 1: System requirements (Ubuntu 22.04, Python 3.10+, disk space)
  - Section 2: ROS 2 Humble installation on Ubuntu 22.04 (official package method)
  - Section 3: Colcon workspace setup and initialization
  - Section 4: Building your first ROS 2 package
  - Section 5: Troubleshooting common installation issues
  - Section 6: Cloud alternatives (AWS RoboMaker, NVIDIA Isaac Cloud)
  - All citations from official ROS 2 docs

- [ ] T024 [P] Create installation and setup scripts with inline documentation:
  - [ ] T024a Enhance `scripts/install-ros2-humble.sh`:
    - Automates: apt-key, apt-sources, ros-humble-desktop-full installation
    - Handles errors gracefully with informative messages
    - Tested on clean Ubuntu 22.04 docker image
  - [ ] T024b Enhance `scripts/setup-colcon-workspace.sh`:
    - Creates workspace directory structure
    - Initializes colcon workspace with rosdep
    - Installs Python dependencies (rclpy, colcon-common-extensions)
    - Sources setup.bash correctly
  - [ ] T024c Enhance `scripts/verify-installation.sh`:
    - Check `ros2 --version` output
    - Verify ROS 2 environment variables set
    - Test `colcon build` in sample workspace
    - Report success/failure with diagnostics

- [ ] T025 [P] Write tests for setup scripts in `tests/test_setup.py`:
  - Test installation script runs without errors on Ubuntu 22.04 docker image
  - Test workspace creation produces correct directory structure
  - Test verification script detects successful and failed installations
  - Use github.com/osrf/ros_docker_images as test environment

- [ ] T026 Create `docs/module-1/quickstart.md`:
  - Step-by-step walkthrough: install → verify → create workspace → build example
  - Copy-paste commands for students without shell expertise
  - Screenshots/terminal output examples

**Checkpoint**: Setup chapter complete with automated installation scripts, verification suite, quickstart guide. Story 2 is independently testable.

---

## Phase 5: User Story 3 - Bridge Python AI Code to ROS Control (Priority: P2)

**Goal**: Students write Python nodes that integrate with ROS controllers (publish goals, subscribe to state feedback)

**Independent Test**: Student writes node that publishes to `goal_position` topic, subscribes to `actual_position` topic, implements feedback loop, code runs without errors

### Chapter 2 Implementation: Communication Patterns

- [ ] T027 Write `docs/module-1/chapter-2.md` with learning objectives, content outline:
  - Section 1: Topic patterns deep dive (async, QoS, message filtering)
  - Section 2: Services - Synchronous request-reply (definition, client/server pattern, blocking behavior)
  - Section 3: Actions - Goal-based communication with feedback (long-running tasks, preemption)
  - Section 4: Custom message types (.msg file syntax, generated Python classes)
  - Section 5: Launch files and parameter configuration (XML syntax, parameters, remapping)
  - Section 6: Integrating AI/ML code with ROS control (practical example: joint controller)
  - Inline code examples with proper citations to ROS 2 docs

- [ ] T028 [P] Create code examples for Chapter 2:
  - [ ] T028a Create `examples/2-service-server.py` - ROS 2 service server (arithmetic service)
  - [ ] T028b Create `examples/2-service-client.py` - ROS 2 service client calling service
  - [ ] T028c Create `examples/2-custom-message.msg` - Custom message definition file (Point3D with x,y,z)
  - [ ] T028d Create `examples/2-action-server.py` - Action server for long-running task (fibonacci)
  - [ ] T028e Create `examples/2-action-client.py` - Action client calling action server
  - [ ] T028f Create `examples/2-joint-controller.py` - AI/ML example: subscribe joint state, publish goals

- [ ] T029 [P] Write tests for Chapter 2 code examples in `tests/test_chapter_2.py`:
  - Test service server initializes and responds to requests
  - Test service client calls and receives responses
  - Test custom message serialization/deserialization
  - Test action server initializes with goal/feedback/result
  - Test action client calls action and receives feedback
  - Test joint controller subscribes/publishes correctly

- [ ] T030 [P] Create Exercise 2.1 in `exercises/2-1-service-integration/`:
  - [ ] T030a Write `exercises/2-1-service-integration/README.md`:
    - Problem: Create service server that takes two floats, returns their sum; create client that calls it
    - Learning objectives: Understand ROS 2 services, request-reply pattern, blocking calls
    - Acceptance criteria: Server runs, client calls, result correct, no crashes
    - Estimated time: 25-30 minutes
  - [ ] T030b Write `exercises/2-1-service-integration/solution.py` (reference implementation)
  - [ ] T030c Write `exercises/2-1-service-integration/test_solution.py` (pytest acceptance tests)

- [ ] T031 [P] Create Exercise 2.2 in `exercises/2-2-custom-messages/`:
  - [ ] T031a Write `exercises/2-2-custom-messages/README.md`:
    - Problem: Define custom message type (Robot3DPosition with x,y,z,roll,pitch,yaw); create pub/sub nodes using it
    - Learning objectives: Understand .msg file syntax, message code generation, using custom messages
    - Acceptance criteria: .msg file valid, publisher/subscriber use custom message correctly, messages transmit correctly
    - Estimated time: 30-35 minutes
  - [ ] T031b Write `exercises/2-2-custom-messages/solution.py` (reference implementation using custom msg)
  - [ ] T031c Write `exercises/2-2-custom-messages/test_solution.py` (pytest acceptance tests)

- [ ] T032 Create `docs/module-1/assessments/quiz-2.md`:
  - 10-15 questions on Chapter 2 concepts (services, actions, custom messages, launch files, AI integration)
  - Mix of multiple choice and short answer
  - Answer key for instructors

**Checkpoint**: Chapter 2 complete with 6 working code examples, 2 exercises with tests, formative quiz. Story 3 is independently testable.

---

## Phase 6: User Story 4 - Learn URDF for Humanoid Robot Description (Priority: P2)

**Goal**: Students understand URDF format and can write humanoid robot descriptions, visualize in RViz2

**Independent Test**: Student writes URDF with torso (link), 2 arms and 2 legs (links+joints), loads in RViz2, visualizes correctly

### Chapter 3 Implementation: URDF & Robot Description

- [ ] T033 Write `docs/module-1/chapter-3.md` with learning objectives, content outline:
  - Section 1: What is URDF? (XML-based format, use cases, comparison to STEP/CAD)
  - Section 2: URDF components - Links (rigid bodies, inertia, geometry, collision/visual)
  - Section 3: URDF components - Joints (revolute, prismatic, fixed, frames, axes)
  - Section 4: Humanoid robot anatomy (torso, arms, legs, joint types for each)
  - Section 5: Visualization in RViz2 (launch files, TF trees, frame visualization)
  - Section 6: Validating URDF (syntax checking, parsing errors, common mistakes)
  - Section 7: From URDF to simulation (preview for Module 2)
  - Inline code examples with proper citations to ROS/URDF documentation

- [ ] T034 [P] Create code examples for Chapter 3:
  - [ ] T034a Create `examples/3-simple-humanoid.urdf` - Simple humanoid URDF:
    - Torso (body_link)
    - 2 arms (left_arm_link, right_arm_link with shoulder revolute joints)
    - 2 legs (left_leg_link, right_leg_link with hip revolute joints)
    - All with visual and collision geometry
  - [ ] T034b Create `examples/3-humanoid-extended.urdf` - Extended humanoid with more joints:
    - Add elbow, wrist joints to arms
    - Add knee, ankle joints to legs
    - More realistic inertia and geometry
  - [ ] T034c Create `examples/3-urdf-viz-launch.xml` - Launch file for RViz2 visualization

- [ ] T035 [P] Write tests for Chapter 3 URDF files in `tests/test_chapter_3.py`:
  - Test URDF files parse without XML syntax errors
  - Test URDF contains expected links and joints
  - Test joint types are valid (revolute, fixed, etc.)
  - Test URDF is loadable in RViz2 (ROS 2 URDF parser test)
  - Test inertia and geometry are properly defined

- [ ] T036 [P] Create Exercise 3.1 in `exercises/3-1-basic-urdf/`:
  - [ ] T036a Write `exercises/3-1-basic-urdf/README.md`:
    - Problem: Write URDF for simple 2-DOF robot (base + arm with 2 joints)
    - Learning objectives: Understand URDF syntax, links, revolute joints, frames
    - Acceptance criteria: URDF syntactically valid, parses correctly, visualizes in RViz2
    - Estimated time: 25-30 minutes
  - [ ] T036b Write `exercises/3-1-basic-urdf/solution.urdf` (reference implementation)
  - [ ] T036c Write `exercises/3-1-basic-urdf/test_urdf.py` (pytest acceptance tests for URDF validity)

- [ ] T037 [P] Create Exercise 3.2 in `exercises/3-2-humanoid-extension/`:
  - [ ] T037a Write `exercises/3-2-humanoid-extension/README.md`:
    - Problem: Extend simple humanoid URDF with additional joints (e.g., add elbow, knee joints)
    - Learning objectives: Understand joint hierarchies, multi-DOF kinematic chains, frame relationships
    - Acceptance criteria: Extended URDF valid, visualizes in RViz2, structure matches specification
    - Estimated time: 30-35 minutes
  - [ ] T037b Write `exercises/3-2-humanoid-extension/solution.urdf` (reference implementation extending simple humanoid)
  - [ ] T037c Write `exercises/3-2-humanoid-extension/test_urdf.py` (pytest acceptance tests)

- [ ] T038 Create `docs/module-1/assessments/quiz-3.md`:
  - 10-15 questions on Chapter 3 concepts (URDF syntax, links, joints, humanoid anatomy, RViz2 visualization)
  - Mix of multiple choice and short answer
  - Answer key for instructors

**Checkpoint**: Chapter 3 complete with 3 working URDF examples, 2 exercises with tests, formative quiz. Story 4 is independently testable.

---

## Phase 7: Module Integration & Assessments

**Purpose**: Complete module assessments, validate all content, prepare for publication

- [ ] T039 Create `docs/module-1/assessments/mini-project.md`:
  - Capstone project: "Build a Simple Humanoid Controller in Simulation"
  - Integrates: Chapter 1 concepts (pub/sub), Chapter 2 patterns (services/actions), Chapter 3 URDF
  - Project scope: Create URDF for humanoid, implement ROS 2 nodes to publish joint goals, simulate in RViz2
  - Grading rubric: URDF validity, code functionality, documentation, creativity
  - Estimated time: 2-3 hours

- [ ] T040 [P] Run complete content quality validation:
  - [ ] T040a Run `tests/test_content_quality.py` (IEEE citations, readability, Markdown structure)
  - [ ] T040b Run `tests/test_chapter_1.py`, `test_chapter_2.py`, `test_chapter_3.py` (code example tests)
  - [ ] T040c Run all exercise test suites (automated acceptance tests for all 6 exercises)
  - [ ] T040d Validate all example scripts with `scripts/validate-examples.sh`
  - [ ] T040e Generate content readability metrics (Flesch-Kincaid report)

- [ ] T041 [P] Docusaurus build and deployment:
  - [ ] T041a Build Docusaurus site: `docusaurus build`
  - [ ] T041b Verify build output in `build/` directory
  - [ ] T041c Test local serving: `docusaurus serve`
  - [ ] T041d Validate navigation, search, code block rendering

- [ ] T042 Create student learning guide in `docs/module-1/student-guide.md`:
  - How to use the module (reading order, estimated times per chapter)
  - How to set up environment
  - How to run examples and exercises
  - How to get help (office hours, discussion forums)
  - Success tips and common pitfalls

- [ ] T043 Create instructor guide in `docs/module-1/instructor-guide.md`:
  - Module overview and learning outcomes
  - Time estimates and sequencing suggestions
  - Exercise grading rubrics and answer keys
  - Assessment strategies and sample student feedback
  - Tips for teaching ROS 2 to AI/ML students

- [ ] T044 Create `docs/module-1/README.md` with:
  - Module summary
  - Learning outcomes
  - Prerequisites and time commitment
  - Links to chapters, exercises, assessments

**Checkpoint**: All content complete, validated, ready for publication

---

## Phase 8: Documentation & Release

**Purpose**: Final polish, documentation, and release preparation

- [ ] T045 Update root `README.md` with Module 1 information:
  - Module 1 overview and link to content
  - Installation/setup instructions
  - How to contribute
  - Citation and attribution for sources

- [ ] T046 Create citation reference library in `docs/module-1/citations.bib`:
  - All IEEE-formatted citations used in Module 1
  - Organized by chapter
  - Includes version numbers for ROS 2, Python, Ubuntu

- [ ] T047 Create GitHub release notes for Module 1 v1.0.0:
  - Summary of content (3 chapters, 12 code examples, 6 exercises)
  - Key features and learning outcomes
  - Installation/usage instructions
  - Known limitations or future improvements

- [ ] T048 [P] Final validation checklist:
  - [ ] T048a All 15 functional requirements (FR-001 through FR-015) implemented
  - [ ] T048b All 4 user stories independently testable and complete
  - [ ] T048c All 10 success criteria measurable and verified
  - [ ] T048d Content volume: 80-100 pages (verified from Docusaurus build)
  - [ ] T048e All 12 code examples tested and passing on Ubuntu 22.04 + ROS 2 Humble
  - [ ] T048f All 6 exercises with solutions and automated acceptance tests
  - [ ] T048g All citations in IEEE format with working links
  - [ ] T048h Content readability: Flesch-Kincaid 12-14 (verified by test suite)
  - [ ] T048i No plagiarism detected (original writing with citations)

- [ ] T049 Create CHANGELOG.md documenting Module 1 v1.0.0 release

**Checkpoint**: Module 1 complete and ready for publication

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Status |
|-------|-----------|--------|
| Phase 1: Setup | None | Start immediately |
| Phase 2: Foundational | Phase 1 completion | BLOCKS all chapter work |
| Phase 3: US1 (Architecture) | Phase 2 completion | Can start after foundational |
| Phase 4: US2 (Setup) | Phase 2 completion | Can start after foundational (independent of US1) |
| Phase 5: US3 (Communication) | Phase 2 completion | Can start after foundational (depends on US1 concepts) |
| Phase 6: US4 (URDF) | Phase 2 completion | Can start after foundational (independent of other stories) |
| Phase 7: Integration | All stories completion | Runs after all chapter content complete |
| Phase 8: Release | Phase 7 completion | Final polish and publication |

### Critical Path

1. **Phase 1**: Setup (2-3 days)
2. **Phase 2**: Foundational - BLOCKING (1-2 days) ⚠️ Must complete before chapter writing
3. **Parallel Phases 3-6**: All 4 user stories can proceed in parallel after Phase 2:
   - Team member A: Chapter 1 (US1) - 3-4 days
   - Team member B: Chapter 0 Setup + Chapter 2 (US2 + US3) - 4-5 days
   - Team member C: Chapter 3 (US4) - 3-4 days
4. **Phase 7**: Integration & validation (2-3 days)
5. **Phase 8**: Documentation & release (1-2 days)

**Total estimated timeline**: 14-18 days with parallel team execution

### Parallel Opportunities

**Within Phase 1 (Setup)**:
- T002, T003, T004, T006 can run in parallel (different files/systems)
- T007, T008 can run in parallel

**Within Phase 2 (Foundational)**:
- T010, T013 can run in parallel (glossary and quality tests)
- T014, T015, T016 can run in parallel (metadata schemas)

**Within Phase 3 (US1)**:
- T018 (code examples) can run in parallel with T019 (tests) after examples created
- T020, T021 (exercises) can run in parallel
- After T020/T021 tests are written, T022 (quiz) can proceed in parallel

**Within Phase 4 (US2)**:
- T024 setup scripts can be developed in parallel
- T025 tests can run in parallel with T026 quickstart after scripts drafted

**Within Phase 5 (US3)**:
- T028 code examples can run in parallel
- T029 tests can run in parallel with examples
- T030, T031 exercises can run in parallel

**Within Phase 6 (US4)**:
- T034 URDF examples can run in parallel
- T035 tests can run in parallel with examples
- T036, T037 exercises can run in parallel

**Across Stories** (after Phase 2):
- US1, US2, US3, US4 can all be worked on simultaneously by different team members
- Integration only happens in Phase 7

---

## Parallel Example: Full Team Execution

```
Phase 1 (Sequential): Setup
  Day 1: T001 → T002-T004, T006 (parallel) → T005
  Day 2: T007-T008 (parallel)

Phase 2 (Sequential with parallels): Foundational
  Day 3: T009 → T010, T013 (parallel) → T011-T012
  Day 4: T014, T015, T016 (parallel)
  ✅ GATE: All foundational tasks complete - chapter work can now begin

Phases 3-6 (Parallel):
  Developer A (Days 5-8):
    - Chapter 1 (US1): T017 → T018 (code) → T019 (tests) → T020, T021 (parallel exercises) → T022 (quiz)

  Developer B (Days 5-9):
    - Chapter 0 + 2 (US2+US3): T023 (setup chapter) → T024-T025 (parallel scripts) → T026 (quickstart) →
                              T027 (Ch2) → T028 (examples) → T029 (tests) → T030, T031 (parallel exercises) → T032 (quiz)

  Developer C (Days 5-8):
    - Chapter 3 (US4): T033 (chapter) → T034 (URDF examples) → T035 (tests) → T036, T037 (parallel exercises) → T038 (quiz)

Phase 7 (Sequential): Integration & Validation
  Day 9: T040 (run all tests in parallel), T041 (build Docusaurus), T042-T044 (guides)
  Day 10: T045-T049 (documentation, release, final checklist)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

To deliver MVP in shortest time:

1. **Phase 1**: Setup (2 days)
2. **Phase 2**: Foundational (1 day)
3. **Phase 3**: US1 - Core Architecture (3 days)
4. **Validate**: Run T040 tests, T041 build
5. **Deploy**: MVP chapter with 2 exercises, ready for students

**MVP Scope**: Chapter 1 + exercises, minimal setup docs (full setup in Phase 4 later)

### Incremental Delivery (All Stories)

1. Complete Phases 1-2 (foundation ready)
2. Deliver Phase 3 (US1) alone → Test independently → Demo
3. Deliver Phase 4+5 (US2+US3) → Test → Demo
4. Deliver Phase 6 (US4) → Test → Demo
5. Run Phase 7 (integration) → Ready for publication

Each story can be paused/released independently; later stories build on earlier content.

---

## Task Checklist Format

All tasks follow format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

**Example task execution**:
```
- [ ] T001 Initialize Docusaurus 3.x project with MDX support in root directory
- [ ] T002 [P] Create project directory structure per plan.md: docs/, examples/, exercises/, scripts/, tests/
- [ ] T018 [P] Create code examples for Chapter 1
- [ ] T018a Create examples/1-hello-world-pub.py - Working publisher node
- [ ] T020 [P] Create Exercise 1.1 in exercises/1-1-create-publisher/
- [ ] T020a Write exercises/1-1-create-publisher/README.md
- [ ] T032 Create docs/module-1/assessments/quiz-2.md
```

---

## Notes

- **[P] marker**: Use only when task touches different files and has no dependencies on incomplete tasks
- **[Story] label**: Required for all user story phase tasks (US1, US2, US3, US4); omit for setup/foundational/polish
- **File paths**: All absolute from repository root; use `examples/`, `exercises/`, `docs/`, `tests/` prefixes
- **Test-first**: Write test tasks before implementation tasks in each phase
- **Independently testable**: Each user story should be independently completable; validate at each checkpoint
- **Parallel execution**: Use [P] marker and stagger work across team to maximize parallelism
- **Commit frequency**: Commit after each task or logical group (e.g., after T020a, T020b, T020c are done)
- **Stop points**: Can stop at any checkpoint (after Phase 1, 2, 3, 4, 5, 6) and validate independently

---

**Version**: 1.0.0 | **Status**: Ready for Implementation | **Branch**: `001-ros2-fundamentals`
**Total Tasks**: 49 base tasks + sub-tasks (approximately 80-100 total with breakdowns)
**Estimated Team Effort**: 14-18 days (parallel team of 3) or 30-40 days (single developer)
