# Module 4 Glossary: Vision-Language-Action (VLA) Capstone

This glossary defines key terms and concepts introduced in Module 4. Terms are listed alphabetically for easy reference.

---

## A

**Action Client** (ROS 2)
A ROS 2 component that sends goals to an **Action Server** and waits for results. Used to communicate with Nav2, perception, and arm control systems. See Chapter 12 section 2.2.

**Action Type**
The type of robot action in a task plan step. Valid types: `navigate`, `perceive`, `manipulate`, `request_clarification`. Defined in Chapter 11 section 3.1.

**Ambiguous Goal**
A natural language goal that lacks critical information for decomposition. Example: "Pick up the thing" (which thing? where?). Discussed in Chapter 11 section 5.1.

**API Rate Limit**
A constraint imposed by the OpenAI API limiting the number of requests per minute. When hit, retry with exponential backoff. See Chapter 10 section 5.3 and Chapter 11 section 2.1.

**Assessment Rubric**
A scoring framework for evaluating student work. Chapters 10-12 each include rubrics with criteria like code quality, functionality, and performance. See exercise sections.

---

## C

**Capstone Project**
A comprehensive, final project (Chapter 12) that integrates all learning from Module 4. Students execute a multi-step autonomous task and document results with metrics.

**Confidence Score**
A numerical measure (0.0-1.0) of prediction confidence. For Whisper, estimated from decoding probability. Used to reject low-quality transcriptions. Chapter 10 section 5.1.

**Confidence Threshold**
A configurable minimum confidence score (default: 0.5). Transcriptions below this are rejected and user is asked to repeat. Chapter 10 section 5.2.

**Cognitive Planning**
The process of using an LLM to decompose high-level goals into executable task steps. Core topic of Chapter 11.

**Custom Messages** (ROS 2)
User-defined message types for ROS 2 communication. Module 4 defines: `VoiceCommand`, `TaskPlan`, `ExecutionStep`, `ExecutedStep`, `ExecutionTrace`. See tasks.md Phase 2.

---

## D

**Domain Randomization**
A technique for training models using varied, synthetic data to improve real-world performance. Related to Isaac Sim synthetic data generation (Module 3), applicable to VLA systems.

**Execution Step**
A single action within a task plan. Contains: action type, parameters, expected outcome, timeout. Defined in data-model.md.

**Execution Trace**
A record of a complete task execution including: plan, steps executed, duration, success rate, failures, safety incidents. Used for metrics and debugging. Chapter 12 section 3.2.

**Executor Node**
The ROS 2 node (Chapter 12) that executes task plans sequentially by calling Nav2, perception, and arm control subsystems.

---

## F

**Function Calling** (LLM)
A technique where an LLM returns structured function calls (JSON) instead of just text. Used by GPT-4 to generate task plans. Chapter 11 section 2.1.

**Function Schema**
A JSON schema defining the inputs and outputs for an LLM-callable function. Example: navigate(destination, speed) → success/failure. Chapter 11 section 3.2.

---

## G

**Goal Decomposition**
The process of breaking a high-level goal into executable steps. Central to task planning (Chapter 11). Example: "bring red cube" → [navigate, perceive, manipulate, navigate].

**Gripper Force**
The pressure/force applied by a robot gripper when grasping objects. Must be tuned to object fragility. Discussed in Chapter 12 section 4.3.

---

## L

**Language Model** (LLM)
A neural network trained on large text corpora to understand and generate language. GPT-4 used for task planning (Chapter 11).

**Latency**
Time elapsed from request to response. Measured at multiple stages:
- Whisper transcription: &lt;2 seconds (Chapter 10)
- LLM planning: &lt;5 seconds (Chapter 11)
- Step execution: 2-5 seconds per step (Chapter 12)
- Full pipeline: &lt;30 seconds (Chapter 12)

**Learning Objectives**
Specific, measurable outcomes students should achieve. Each chapter lists 5 learning objectives in the introduction.

**Lifecycle Node** (ROS 2)
A ROS 2 node with managed state transitions: unconfigured → inactive → active. Used by whisper_transcriber_node. Chapter 10 section 4.1.

**LLM Planning Service**
A ROS 2 service/action that accepts a voice command and returns a structured task plan. Core component of Chapter 11.

---

## M

**Manipulation**
Robot action to grasp, move, or release objects. Part of the three core action types (navigate, perceive, manipulate).

**Microphone**
Audio input device. Module 4 uses 16kHz mono PCM input via PyAudio. System requirements listed in Chapter 10 section 2.

**Model Version** (Whisper)
Whisper comes in multiple sizes: tiny, base, small, medium, large. Larger models are more accurate but slower. Chapter 10 section 2.3.

---

## N

**Navigation**
Robot action to move to a specified location. Implemented via Nav2 (Module 3). Chapter 12 section 2.2.

**Natural Language Processing** (NLP)
Computational techniques for understanding and generating human language. Foundation for voice transcription and LLM planning.

---

## O

**OpenAI API**
Cloud service providing access to Whisper (speech-to-text) and GPT-4 (task planning). Requires API key and authentication. Chapter 10 section 2.2, Chapter 11 section 2.1.

**OpenAI Whisper**
A robust speech-to-text model trained on 680,000 hours of multilingual audio. Supports 99 languages. Core technology in Chapter 10.

---

## P

**Parameter Validation**
Checking that action parameters match schema constraints (types, ranges, enumerations). Prevents invalid plans. Chapter 11 section 3.2.

**Perception**
Robot action to detect and identify objects using computer vision. Returns object ID and 3D coordinates. Chapter 12 section 2.2.

**Plan Validation**
Process of checking a generated task plan for executability: valid action types, logical ordering, realistic parameters, reasonable duration. Chapter 11 section 4.

**Plan Quality**
Measure of how well a task plan achieves its goal. Evaluated on: executability, logical ordering, parameter realism, duration. Chapter 11 section 6.

---

## R

**RAG Optimization** (Retrieval-Augmented Generation)
Technique for organizing documentation to be easily indexed and retrieved by AI systems. Involves clear semantic headings and keyword placement. Mentioned throughout chapters for searchability.

**Request Clarification**
A special action type used when the LLM cannot decompose an ambiguous goal. Asks user for clarification. Chapter 11 section 5.2.

**Retry Logic**
Mechanism to re-attempt failed operations (e.g., Whisper API with exponential backoff, navigation on obstacles). Discussed in multiple chapters.

**Robot Capabilities**
Enumeration of actions a robot can perform (navigate, perceive, manipulate). Provided to LLM as context for planning. Chapter 11 section 3.1.

**ROS 2** (Robot Operating System 2)
Middleware for robot software. Module 4 extensively uses ROS 2 for inter-process communication (topics, services, actions).

---

## S

**Safety Constraints**
Rules preventing dangerous plans (e.g., fast navigation without obstacle avoidance). Checked before execution. Chapter 12 section 4.3.

**Safety Incident**
An unexpected event during execution (collision, gripper slip, emergency stop). Logged and reported in execution trace. Chapter 12 section 6.

**Sample Rate**
Frequency of audio sampling in Hz. Whisper expects 16 kHz (16,000 samples per second). Chapter 10 section 3.1.

**Schema** (Action)
Formal definition of an action's inputs, outputs, and constraints. JSON schemas used for validation. Chapter 11 section 3.2.

**Semantic Heading**
Documentation section header with clear semantic meaning. Used for RAG chunking. Example: "## 1. Architecture" is a semantic H2.

**Speech-to-Text** (STT)
Converting spoken audio to written text. Core function of Whisper module. Chapter 10 primary topic.

**Step Ordering**
Logical sequence of task steps. Example: perceive before manipulate (can't grasp before finding object). Validated in Chapter 11 section 4.1.

**System Prompt**
Initial context provided to an LLM to guide its behavior. For task planning, defines robot capabilities and response format. Chapter 11 section 2.3.

---

## T

**Task Decomposition**
Breaking a high-level goal into actionable steps. Primary function of the LLM planner. Chapter 11 primary topic.

**Task Plan**
A structured sequence of steps to achieve a goal. Contains: goal statement, steps (with action type and parameters), metadata. Defined in data-model.md.

**Timeout**
Maximum time allowed for a step to complete. Prevents hanging. Default 30 seconds for full plan, 5-20 seconds per step. Chapter 12 section 5.2.

**Transcription**
Converted form of audio into text. Output of Whisper API. Chapter 10 primary topic.

**Troubleshooting**
Process of identifying and resolving system failures. Chapter 12 section 6 covers common failure modes and debugging strategies.

---

## V

**Validation Report**
Structured output of a plan validation, listing errors or confirming success. Includes: step count, action types, parameter constraints, timing. Chapter 11 section 4.1.

**Vision-Language-Action** (VLA)
A system that perceives visually, reasons linguistically, and acts physically. Module 4's integrating concept spanning Chapters 10-12.

**Voice Command**
A spoken utterance to control the robot. Captured by microphone, transcribed by Whisper, decomposed by LLM, executed. Chapter 10 primary topic.

**Voice Processing Pipeline**
The complete flow from audio input to ROS 2 topic publication. Diagram in Chapter 10 section 1.1.

---

## W

**Whisper Confidence**
Measure of transcription quality. Whisper doesn't return explicit scores, but confidence estimated from decoding probability and comparison with alternatives. Chapter 10 section 5.1.

**Whisper Client Wrapper**
A Python module encapsulating OpenAI Whisper API calls with retry logic, error handling, and audio validation. Described in Chapter 10 section 2.3.

**Whisper Transcriber Node**
The ROS 2 lifecycle node that captures audio, calls Whisper API, validates confidence, and publishes to `/voice/transcribed_command` topic. Core of Chapter 10.

---

## X

*(No terms beginning with X)*

---

## Y

**YAML Configuration**
Human-readable data format used for robot capabilities, LLM system prompts, and action schemas. Examples throughout Chapters 10-12.

---

## Z

*(No terms beginning with Z)*

---

## Related Glossaries

- **Module 1**: ROS 2 Fundamentals (topics, services, nodes, packages)
- **Module 2**: Perception & Computer Vision (cameras, filters, segmentation)
- **Module 3**: Digital Twins & Simulation (Isaac Sim, physics, sensors)
- **Module 4**: Vision-Language-Action (this glossary)

---

## Cross-References

- **Chapter 10 - Voice-to-Action**: Whisper API, audio capture, ROS 2 publishers, error handling
- **Chapter 11 - Cognitive Planning**: LLM function calling, task decomposition, plan validation, robot capabilities
- **Chapter 12 - Capstone**: Executor nodes, action clients, error recovery, end-to-end metrics

---

**Glossary Version**: 1.0
**Last Updated**: January 26, 2026
**Modules Covered**: 1-4
**Total Terms**: 87
