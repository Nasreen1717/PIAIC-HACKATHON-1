# Quick Start: Module 4 - Vision-Language-Action (VLA) Capstone

**Date**: 2026-01-26 | **Feature**: 004-vla-capstone | **Branch**: 004-vla-capstone

## Prerequisites

- Completed Modules 1, 2, and 3
- Ubuntu 22.04 LTS with ROS 2 Humble installed
- Isaac Sim 2023.8+ with humanoid robot model
- Python 3.10+, colcon workspace set up
- GPU recommended (RTX 4070 Ti+ or AWS g5.2xlarge)
- OpenAI API key (for Whisper and GPT-4 access)

## Installation (15 minutes)

### 1. Clone the Module 4 Repository

```bash
cd ~/ros2_ws/src
git clone https://github.com/your-org/module-4-vla.git
cd ~/ros2_ws
```

### 2. Install Python Dependencies

```bash
pip install -r module-4-vla/requirements.txt
```

**Key packages**:
- `openai>=1.0.0` — OpenAI API client (Whisper, GPT-4)
- `python-dotenv` — Environment variable management
- `numpy`, `scipy` — Numerical computing
- `pytest` — Testing framework
- `rclpy` — ROS 2 Python client library

### 3. Create Environment File

```bash
cp module-4-vla/.env.example module-4-vla/.env
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...  # Optional
```

⚠️ **Important**: Never commit `.env` to version control. It's in `.gitignore`.

### 4. Build ROS 2 Packages

```bash
cd ~/ros2_ws
colcon build --packages-select custom_msgs
colcon build --packages-select whisper_node llm_planner executor_node
source install/setup.bash
```

### 5. Verify Installation

```bash
# Test Python imports
python -c "import openai; print(f'OpenAI version: {openai.__version__}')"

# Test ROS 2 messages
python -c "from custom_msgs.msg import VoiceCommand; print('Custom messages OK')"

# Run unit tests
cd module-4-vla
pytest tests/unit/ -v
```

**Expected output**: All tests pass, no import errors.

---

## Your First Voice-to-Action Command (10 minutes)

### Step 1: Start Isaac Sim with Module 4 Scene

```bash
# Terminal 1: Launch Isaac Sim
cd ~/isaac-sim
./isaac-sim.sh
# In Isaac Sim GUI: Load "/modules/module-4/scenes/humanoid_kitchen.usd"
```

### Step 2: Launch ROS 2 Stack

```bash
# Terminal 2: Launch all ROS 2 nodes
cd ~/ros2_ws
source install/setup.bash
ros2 launch module_4_launch all_nodes.launch.py
```

This starts:
- `whisper_node` (listens for audio)
- `llm_planner_node` (generates task plans)
- `executor_node` (executes plans)
- Nav2 stack (from Module 3)
- Perception nodes (from Module 3)

### Step 3: Test Voice Command

```bash
# Terminal 3: Publish a test command via ROS 2 (or use microphone)
cd ~/ros2_ws
source install/setup.bash

# Option A: Use microphone (real audio)
python module-4-vla/examples/example_02_ros2_publisher.py

# Option B: Test with pre-recorded audio
python module-4-vla/examples/example_03_error_handling.py --audio-file data/test_audio.wav
```

**Expected output**:
```
[INFO] Starting Whisper transcriber...
[INFO] Listening for audio...
[INFO] Transcript: "bring me the red cube from the table"
[INFO] Publishing to /voice/transcribed_command
[INFO] LLM planning...
[INFO] Generated 4-step task plan (estimated 25s)
[INFO] Executing...
[INFO] Step 1/4: Navigate to kitchen_table... SUCCESS (8.2s)
[INFO] Step 2/4: Perceive red_cube... SUCCESS (2.1s)
[INFO] Step 3/4: Grasp red_cube... SUCCESS (4.2s)
[INFO] Step 4/4: Navigate to user... SUCCESS (9.8s)
[INFO] Task completed! Success rate: 100%
```

### Step 4: View Execution Trace

```bash
# Terminal 3: Open the execution log
python module-4-vla/scripts/view_trace.py --trace-id execution-trace-001
```

---

## Module 4 Structure

### Docusaurus Documentation

```
Front-End-Book/docs/module-4/
├── chapter-10-voice-to-action.mdx          # Whisper integration
├── chapter-11-cognitive-planning.mdx       # LLM task decomposition
└── chapter-12-capstone-humanoid.mdx        # End-to-end demo
```

### Code Examples

```
module-4-vla/examples/
├── example_01_basic_whisper.py             # Standalone Whisper
├── example_02_ros2_publisher.py            # Whisper + ROS 2 topic
├── example_03_error_handling.py            # Confidence thresholding
├── example_04_llm_planning.py              # LLM task generation
├── example_05_execution.py                 # Plan execution
├── example_06_end_to_end.py                # Full pipeline
└── data/
    └── test_audio.wav
```

### Exercises

```
module-4-vla/exercises/
├── exercise_01_whisper_accuracy.py         # Measure transcription accuracy
├── exercise_02_ros2_integration.py         # Build voice listener
├── exercise_03_plan_quality.py             # Evaluate plan decomposition
├── exercise_04_capstone_demo.py            # Full capstone task
└── solutions/
    ├── exercise_01_solution.py
    └── ...
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"

```bash
pip install openai
```

### "OPENAI_API_KEY not set"

Check `.env`:
```bash
cat module-4-vla/.env | grep OPENAI_API_KEY
```

If empty, add your key and restart the node.

### "Whisper transcription timeout"

Increase timeout in config:
```yaml
# ~/.ros/module_4_config.yaml
whisper:
  timeout_seconds: 10  # Default 5, try 10
```

### "LLM plan generation fails"

Check OpenAI API status and rate limits:
```bash
python -c "from openai import OpenAI; c = OpenAI(); print(c.models.list())" 2>&1 | head
```

### "Robot navigation blocked"

Check Isaac Sim scene for obstacles. Verify Nav2 is running:
```bash
ros2 topic list | grep nav
```

### "Object detection fails"

Verify Isaac Sim perception nodes are publishing:
```bash
ros2 topic list | grep perception
ros2 topic echo /perception/detections
```

---

## Next Steps

### Learn the Fundamentals (Chapter 10)

- Read: `Front-End-Book/docs/module-4/chapter-10-voice-to-action.mdx`
- Run examples: `example_01_basic_whisper.py` → `example_03_error_handling.py`
- Complete: `exercise_01_whisper_accuracy.py` (30 min)

### Understand LLM Planning (Chapter 11)

- Read: `Front-End-Book/docs/module-4/chapter-11-cognitive-planning.mdx`
- Run examples: `example_04_llm_planning.py`
- Complete: `exercise_03_plan_quality.py` (1 hour)

### Build the Capstone (Chapter 12)

- Read: `Front-End-Book/docs/module-4/chapter-12-capstone-humanoid.mdx`
- Run example: `example_06_end_to_end.py`
- Complete: `exercise_04_capstone_demo.py` (2-3 hours)

---

## Key Commands

```bash
# View ROS 2 topics
ros2 topic list
ros2 topic echo /voice/transcribed_command

# Check node status
ros2 node list
ros2 node info /whisper_node

# View execution traces
python module-4-vla/scripts/view_trace.py --all

# Run all examples
bash module-4-vla/scripts/run_examples.sh

# Run tests
pytest module-4-vla/tests/ -v

# View documentation
open Front-End-Book/docs/module-4/chapter-10-voice-to-action.mdx
```

---

## Getting Help

- **Documentation**: See `Front-End-Book/docs/module-4/`
- **Examples**: Check `module-4-vla/examples/` for reference code
- **Issues**: Report on GitHub issues with `[module-4]` tag
- **Discussion**: See GitHub Discussions or robotics forums

---

## Success Metrics

After completing the quickstart, you should:

✅ Install Module 4 without errors
✅ Start Isaac Sim with humanoid robot
✅ Launch ROS 2 stack with all nodes
✅ Execute a voice command end-to-end
✅ View execution trace and logs

**Estimated time**: 25 minutes

**Ready to move on**: Start Chapter 10 exercises once quickstart is complete.

---

## Architecture Diagram

```
User (Voice) → Whisper API
                   ↓
            Transcribed Text
                   ↓
         /voice/transcribed_command (ROS 2 Topic)
                   ↓
            LLM Planner (GPT-4)
                   ↓
            Task Plan (JSON)
                   ↓
         Task Executor (ROS 2 Node)
                   ↓
         Nav2 + Perception + Arm Control
                   ↓
         Robot Action (Navigate/Grasp/Place)
                   ↓
         Execution Trace (Logging)
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_ORG_ID` | OpenAI organization (optional) | `org-...` |
| `ROS_DOMAIN_ID` | ROS 2 domain ID (prevent conflicts) | `1` |
| `ISAAC_SIM_PATH` | Path to Isaac Sim installation | `/opt/nvidia/isaac-sim` |

---

**Next**: [Read Chapter 10 Documentation](../Front-End-Book/docs/module-4/chapter-10-voice-to-action.mdx)
