# Phase 0 Research: Module 4 - Vision-Language-Action (VLA) Integration

**Date**: 2026-01-26 | **Feature**: 004-vla-capstone | **Branch**: 004-vla-capstone

## Overview

This document consolidates research findings addressing technical unknowns and integration patterns for Module 4. All decisions are informed by current best practices, official documentation, and reference implementations.

---

## 1. OpenAI Whisper Integration with ROS 2

### Decision
Use **OpenAI Whisper API** (cloud-based) with a custom ROS 2 node wrapper that:
- Captures audio via PyAudio or PulseAudio
- Sends audio chunks to Whisper API
- Publishes transcribed text to ROS 2 topics
- Handles API rate limiting and errors

### Rationale
- **Official Support**: OpenAI Whisper is production-ready and documented extensively
- **Accuracy**: 90%+ on clear speech, robust to accents and background noise
- **Simplicity**: API-based avoids local model overhead (faster iteration for students)
- **Cost**: Predictable usage-based pricing; ~$0.02 per 15 minutes of audio
- **Integration**: Python-based, compatible with ROS 2 colcon workflows

### Alternatives Considered
1. **Local Whisper (Hugging Face)**: Lower latency, no API calls. Rejected: requires 4-8GB VRAM, adds deployment complexity, students may have underpowered laptops.
2. **Google Speech-to-Text**: Similar to OpenAI. Rejected: less aligned with curriculum (GPT focus), less documented for ROS 2.
3. **Azure Speech Services**: Enterprise-ready. Rejected: overkill for educational use, adds authentication complexity.

### Implementation Details
- **Library**: `openai` Python package (v1.0+), `pyaudio` for audio capture
- **ROS 2 Node**: Python, uses rclpy lifecycle management
- **Topic Contract**: Publishes `std_msgs/String` to `/voice/transcribed_command`
- **Error Handling**: Retry logic (3 attempts), exponential backoff for rate limits
- **Latency Target**: <2 seconds from speech-end to topic publication

### References
- OpenAI Whisper documentation: https://platform.openai.com/docs/guides/speech-to-text
- ROS 2 Python APIs: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Cpp-Publisher-And-Subscriber.html

---

## 2. LLM-to-ROS Task Decomposition

### Decision
Use **OpenAI GPT-4** via API to decompose natural language goals into structured task plans, then execute via ROS 2 action clients targeting:
- **Navigation**: Nav2 `SendGoal` action
- **Perception**: Module 3 vision services (object detection, pose estimation)
- **Manipulation**: MoveIt 2 arm control or mock arm controller

### Rationale
- **State-of-the-Art**: GPT-4 excels at complex task decomposition and reasoning
- **Consistency**: Deterministic structured outputs via function calling / JSON mode
- **Flexibility**: Can adapt to ambiguous commands, request clarification
- **Integration**: Native Python support, seamless with ROS 2
- **Student-Friendly**: Familiar interface (ChatGPT-like usage)

### Alternatives Considered
1. **Open-source LLMs (LLaMA 2, Mistral)**: Free, deployable locally. Rejected: lower reasoning ability (especially for ambiguous goals), adds infrastructure complexity, variable accuracy.
2. **Claude API (Anthropic)**: Comparable to GPT-4. Rejected: slightly higher latency, less adoption in robotics community.
3. **Specialized Task Planning Models**: Fine-tuned for robotics. Rejected: niche models, limited documentation, unstable API support.

### Implementation Details
- **Library**: `openai` Python package (v1.0+) with function calling
- **Prompt Structure**: System prompt defines robot capabilities (navigation, perception, manipulation)
- **LLM Response Format**: JSON with task_plan containing ordered steps, each with action_type, parameters, expected_outcome
- **Fallback**: If LLM cannot decompose, request clarification from user
- **Latency Target**: <5 seconds for plan generation (including API round-trip)

### References
- OpenAI GPT-4 documentation: https://platform.openai.com/docs/guides/gpt-best-practices
- Function Calling: https://platform.openai.com/docs/guides/function-calling

---

## 3. ROS 2 Action Pipeline Design

### Decision
Implement a stateful **Task Executor** that:
1. Receives a structured task plan from LLM
2. Iterates through steps sequentially
3. Translates each step to appropriate ROS 2 action/service calls
4. Monitors execution, captures outcomes
5. Logs failures and triggers fallback behaviors (retry, skip, request help)

### Rationale
- **Robustness**: Stateful design handles mid-execution failures gracefully
- **Observability**: Logging enables debugging and learning (student reflection)
- **Modularity**: Decouples LLM reasoning from ROS 2 execution
- **Scalability**: Can be extended to parallel execution, complex dependencies

### Alternatives Considered
1. **Direct LLM-to-ROS Mapping**: Simpler, skips intermediate planning. Rejected: no error recovery, less flexibility for students to debug.
2. **SMCPL/PDDL-based Planning**: Formal verification possible. Rejected: steep learning curve, overkill for capstone scope.

### Implementation Details
- **State Machine**: States = IDLE, EXECUTING, SUCCESS, FAILURE
- **Step Execution**: Async action calls with timeout (default 30s per step)
- **Failure Handling**: Retry once, then fail with diagnostic log
- **Data Structure**: `ExecutionTrace` captures task_id, steps, outcomes, latencies

### References
- ROS 2 Action documentation: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Cpp-Action-Server-And-Client.html
- Nav2 Actions: https://navigation.ros.org/configuration/index.html

---

## 4. API Configuration and Secrets Management

### Decision
Store OpenAI and any other API credentials in **environment variables** (`.env` file) loaded via `python-dotenv` package. Documentation includes:
- `.env.example` template
- Setup instructions for students
- Warning about not committing `.env` to git

### Rationale
- **Security**: Prevents accidental credential exposure
- **Portability**: Easy to switch keys across environments
- **Simplicity**: Industry-standard practice, well-documented

### Alternatives Considered
1. **Config files (YAML/JSON)**: Not secure, prone to accidental commits.
2. **Kubernetes Secrets / AWS Secrets Manager**: Overkill for student machines.

### Implementation Details
- **Package**: `python-dotenv` (v1.0+)
- **File Structure**: Root `.gitignore` includes `.env`
- **Example**: `.env.example` shows required keys
- **Code Pattern**: `load_dotenv()` at module startup

### References
- python-dotenv: https://python-dotenv.readthedocs.io/

---

## 5. Docusaurus Content Structure for Module 4

### Decision
Organize Module 4 as 3 Docusaurus chapters in `/Front-End-Book/docs/module-4/`:
- `chapter-10-voice-to-action.mdx` (Whisper integration)
- `chapter-11-cognitive-planning.mdx` (LLM task decomposition)
- `chapter-12-capstone-humanoid.mdx` (end-to-end demo)

Each chapter includes:
- Learning objectives (top of page)
- Conceptual overview (500-800 words)
- 4-6 progressively complex code examples
- 2 hands-on exercises
- Assessment rubric

### Rationale
- **Consistency**: Follows Module 1-3 patterns established in constitution
- **Progression**: Chapter 10 → 11 → 12 builds toward capstone
- **Accessibility**: Docusaurus MDX supports interactive code examples, live demos
- **RAG Optimization**: Semantic chunking via section headings

### Alternatives Considered
1. **Jupyter Notebooks**: More interactive but less suitable for RAG chatbot grounding.
2. **GitHub Wiki**: No semantic chunking, harder to version control.

### Implementation Details
- **Markdown Structure**: H2 headers (##) for sections, H3 (###) for subsections
- **Code Blocks**: Language-tagged (python, bash, yaml) with numbered line references
- **Examples Directory**: `/static/examples/module-4/` with runnable scripts
- **Exercises Directory**: `/static/exercises/module-4/` with solution templates

### References
- Docusaurus v3 documentation: https://docusaurus.io/docs/

---

## 6. Integration Pattern: Bridging Modules 1-3 with Module 4

### Decision
Module 4 assumes students have completed Modules 1-3:
- **Module 1 (ROS 2 Fundamentals)**: Students familiar with nodes, topics, services, actions, launch files
- **Module 2 (Gazebo/Simulation)**: Students can launch simulations, understand URDF/SDF
- **Module 3 (Isaac)**: Students have nav2 stack, perception nodes (object detection, pose estimation)

Module 4 integration points:
1. **Navigation**: Use Nav2 actions from Module 3 (no re-implementation)
2. **Perception**: Use Isaac perception services (object detection, segmentation)
3. **Manipulation**: Arm control via MoveIt 2 (intro in Module 3, extended in Module 4)
4. **Simulation**: Launch Isaac Sim environments (Module 3 scenes reused)

### Rationale
- **DRY Principle**: Avoid duplicating Module 1-3 code
- **Progressive Scaffolding**: Students build on known patterns
- **Capstone Cohesion**: Demonstrates full-stack integration

### Implementation Details
- **Prerequisite Check**: Chapter 10 setup validates Module 1-3 environments
- **Imports**: Chapter 12 imports from Module 3 codebase (nav2 clients, perception nodes)
- **Documentation**: Each Chapter 10-12 section includes link to relevant Module 1-3 concepts

### References
- Module 1 spec: `/specs/001-ros2-fundamentals/spec.md`
- Module 2 spec: `/specs/002-digital-twin/spec.md`
- Module 3 spec: `/specs/003-isaac-ai-brain/spec.md`

---

## 7. Example Organization and Complexity Progression

### Decision
Organize examples by complexity level:
- **Level 1 (Beginner)**: Single component in isolation
  - Example: Whisper transcription on pre-recorded audio file
- **Level 2 (Intermediate)**: Component integration
  - Example: Whisper + simple ROS 2 topic publisher
- **Level 3 (Advanced)**: Multi-component workflows
  - Example: Whisper → LLM → ROS 2 action execution

Each example has:
1. **Objective**: 1-sentence learning goal
2. **Prerequisites**: Modules/concepts required
3. **Code**: Runnable script (50-150 lines)
4. **Expected Output**: Screenshot or terminal log
5. **Modifications**: 2-3 suggestions for students to extend

### Rationale
- **Scaffolding**: Meets Bloom's taxonomy (remember → apply → analyze → create)
- **Testability**: Each example independently runnable
- **Reuse**: Students build from previous examples

### Implementation Details
- **Naming**: `example_01_[concept].py`, `example_02_[concept].py`, etc.
- **Documentation**: Docstrings in code; README in example directory
- **Testing**: CI pipeline runs each example (validates syntax, imports)

### References
- Constitution Principle II (Hands-On Learning): `.specify/memory/constitution.md`

---

## 8. Capstone Project Structure and Success Metrics

### Decision
Capstone consists of a single **End-to-End Autonomous Task** scenario:
- **Scenario**: "Voice command 'bring me the red cube from the kitchen table' → humanoid navigates, identifies object, grasps, returns"
- **Metrics**:
  - Success rate: 80%+ task completion
  - Latency: <30 seconds per cycle
  - Safety: 0 collisions / gripper errors
  - Observability: Full execution logs with timestamps

### Rationale
- **Integration**: Exercises all modules (navigation, perception, manipulation, voice, LLM)
- **Measurable**: Clear pass/fail criteria
- **Accessible**: 10 hours guided work achievable for students with Module 1-3 background

### Alternatives Considered
1. **Multiple Capstone Projects**: Flexible but harder to grade, unclear MVP.
2. **Open-Ended Challenge**: Too vague, students may get stuck.

### Implementation Details
- **Setup**: Provided Isaac Sim environment with kitchen scene, objects
- **Starter Code**: Scaffold covering Whisper → LLM pipeline, students implement task executor
- **Rubric**: 40% code quality, 30% task completion, 20% documentation, 10% creativity (optional extensions)
- **Testing**: Automated test suite validates execution traces

### References
- Constitution Principle IV (Modular, Progressive): `.specify/memory/constitution.md`

---

## 9. Technology Stack Summary

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| OS | Ubuntu 22.04 LTS | 22.04 | Standard, long-term support |
| Runtime | Python | 3.10+ | ROS 2 compatible, industry standard for robotics |
| ROS 2 | Humble | LTS | Long-term support, stable API |
| Voice | OpenAI Whisper API | v3 | Production-ready, 90%+ accuracy |
| LLM | OpenAI GPT-4 | latest | State-of-the-art reasoning, function calling |
| Navigation | Nav2 | Humble | Module 3 foundation, mature stack |
| Perception | Isaac Perception | 2023.8+ | Module 3 foundation, GPU-accelerated |
| Simulation | Isaac Sim | 2023.8+ | Module 3 foundation, photorealistic |
| Arm Control | MoveIt 2 | Humble | Standard ROS 2 arm manipulation |
| Documentation | Docusaurus | 3.x | Established platform, RAG-optimized |

---

## Conclusion

All research findings converge on a coherent, production-ready architecture:
1. **Voice Input**: OpenAI Whisper API (proven, industry standard)
2. **Cognitive Planning**: GPT-4 with function calling (best reasoning)
3. **ROS 2 Execution**: Stateful task executor (robust, observable)
4. **Integration**: Builds seamlessly on Modules 1-3 (progressive scaffolding)
5. **Documentation**: Docusaurus + examples (consistent with curriculum)
6. **Capstone**: Single end-to-end scenario (measurable, achievable)

**Ready for Phase 1 (Design & Contracts)** ✅
