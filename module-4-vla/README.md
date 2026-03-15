# Module 4: Vision-Language-Action (VLA) Capstone

A comprehensive educational curriculum for building autonomous humanoid robots using voice commands, large language models, and ROS 2.

**Status**: Early Development | **Python 3.10+** | **ROS 2 Humble**

---

## 📚 Overview

Module 4 teaches students to build a complete voice-controlled autonomous system:

1. **Chapter 10: Voice-to-Action** - OpenAI Whisper integration with ROS 2
2. **Chapter 11: Cognitive Planning** - GPT-4 task decomposition and planning
3. **Chapter 12: Capstone** - End-to-end autonomous humanoid execution

**Target Students**: Completed Modules 1-3 (ROS 2 Fundamentals, Digital Twin, NVIDIA Isaac)

**Technology Stack**:
- OpenAI Whisper API (voice transcription)
- OpenAI GPT-4 API (task planning)
- ROS 2 Humble (middleware)
- Isaac Sim 2023.8+ (simulation)
- Nav2 (navigation)
- Python 3.10+

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone & Install

```bash
git clone https://github.com/your-org/module-4-vla.git
cd module-4-vla
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
nano .env
```

### 3. Verify Setup

```bash
python -c "import openai; print(f'OpenAI {openai.__version__} ✓')"
python -m pytest tests/unit/test_imports.py -v
```

### 4. Run First Example

```bash
cd examples
python example_01_basic_whisper.py --audio-file data/test_audio.wav
```

**Expected Output**:
```
Transcript: "bring me the red cube from the table"
Confidence: 0.95
Processing time: 1.2s
```

---

## 📖 Documentation

### Chapters
- **Chapter 10**: [Voice-to-Action Integration](../Front-End-Book/docs/module-4/chapter-10-voice-to-action.mdx)
- **Chapter 11**: [Cognitive Planning with LLMs](../Front-End-Book/docs/module-4/chapter-11-cognitive-planning.mdx)
- **Chapter 12**: [Capstone - Autonomous Humanoid](../Front-End-Book/docs/module-4/chapter-12-capstone-humanoid.mdx)

### Setup Guides
- **Quickstart**: See [specs/004-vla-capstone/quickstart.md](../specs/004-vla-capstone/quickstart.md)
- **Architecture**: See [specs/004-vla-capstone/plan.md](../specs/004-vla-capstone/plan.md)
- **API Contracts**: See [specs/004-vla-capstone/contracts/](../specs/004-vla-capstone/contracts/)

---

## 🗂️ Project Structure

```
module-4-vla/
├── src/                          # ROS 2 packages
│   ├── custom_msgs/              # Message definitions
│   ├── whisper_node/             # Voice capture & transcription
│   ├── llm_planner_node/         # Task planning via GPT-4
│   ├── executor_node/            # Plan execution
│   ├── module_4_common/          # Shared utilities
│   └── module_4_launch/          # Launch files
├── examples/                      # 6 worked examples (beginner → advanced)
├── exercises/                     # 4 student exercises + solutions
├── tests/                         # Unit + integration tests
├── scripts/                       # Setup, testing, utilities
├── config/                        # YAML configs, prompts
├── requirements.txt               # Python dependencies
├── .env.example                  # Environment template
└── README.md                      # This file
```

---

## 🔧 Installation

### Prerequisites
- Ubuntu 22.04 LTS
- Python 3.10+
- ROS 2 Humble (if using actual ROS 2 integration)
- OpenAI API key (https://platform.openai.com/api-keys)

### Full Setup (30 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env with your OpenAI API key and preferences

# 3. Build ROS 2 packages (if in ROS 2 workspace)
cd ~/ros2_ws
colcon build --packages-select custom_msgs whisper_node llm_planner_node executor_node
source install/setup.bash

# 4. Run tests to verify
pytest tests/ -v

# 5. Launch Isaac Sim and ROS 2 (if full stack)
ros2 launch module_4_launch all_nodes.launch.py
```

---

## 📚 Learning Progression

### Level 1: Voice Processing (Chapter 10)
- Learn Whisper API basics
- Capture and transcribe audio
- Publish to ROS 2 topics
- Handle errors gracefully

**Time**: 2-3 hours | **Exercises**: 2

### Level 2: Task Planning (Chapter 11)
- Understand GPT-4 function calling
- Decompose goals into steps
- Validate plan structure
- Handle ambiguous commands

**Time**: 2-3 hours | **Exercises**: 2

### Level 3: Capstone Integration (Chapter 12)
- Chain all components: voice → planning → execution
- Execute nav2 navigation, perception, manipulation
- Monitor and log execution
- Measure performance metrics

**Time**: 4-5 hours | **Exercises**: 1 capstone project

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Generate coverage report
pytest tests/ --cov=module_4_common --cov-report=html

# Run specific test
pytest tests/unit/test_whisper.py -v
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"
```bash
pip install openai>=1.0.0
```

### "OPENAI_API_KEY not set"
```bash
# Check .env file exists and has valid key
cat .env | grep OPENAI_API_KEY

# If missing, add it:
echo "OPENAI_API_KEY=sk-..." >> .env
```

### "Whisper transcription timeout"
Increase timeout in config:
```yaml
# config/robot_capabilities.yaml
whisper:
  timeout_seconds: 10  # Increase from default 5
```

### "ROS 2 nodes not found"
```bash
# Verify ROS 2 packages built and sourced
cd ~/ros2_ws
colcon build --packages-select custom_msgs
source install/setup.bash

# Check topic list
ros2 topic list | grep voice
```

### "Isaac Sim connection fails"
- Verify Isaac Sim is running: `ps aux | grep isaac`
- Check network connectivity: `ping localhost:5005`
- See [Isaac Sim documentation](https://docs.nvidia.com/isaac/isaac-sim/)

---

## 🔌 API Keys & Secrets

### OpenAI API Key
1. Create account: https://platform.openai.com
2. Generate API key: https://platform.openai.com/api-keys
3. Add to `.env`: `OPENAI_API_KEY=sk-...`
4. Cost estimate: ~$0.05 per capstone demo (usage-based)

### Security Best Practices
- ✅ Keep `.env` out of git (added to `.gitignore`)
- ✅ Use unique API keys per environment (dev/test/prod)
- ✅ Rotate keys regularly
- ✅ Monitor API usage at https://platform.openai.com/account/billing/overview

---

## 📊 Architecture Overview

```
User (Voice)
    ↓
Whisper API → Transcribed Text
    ↓
/voice/transcribed_command (ROS 2 Topic)
    ↓
LLM Planner (GPT-4) → Task Plan (JSON)
    ↓
Task Executor (ROS 2 Node)
    ↓
Nav2 + Perception + Arm Control
    ↓
Humanoid Robot Action (Navigate/Grasp/Place)
    ↓
Execution Trace (Logging & Metrics)
```

---

## 🎯 Success Metrics

Module 4 is complete when students can:

- ✅ Set up Whisper with >90% accuracy, <2s latency
- ✅ Generate task plans with 95% validity rate, <5s latency
- ✅ Execute capstone task: 80%+ success rate, <30s per cycle
- ✅ Zero collisions or gripper errors
- ✅ Document and explain their system

---

## 📝 Examples & Exercises

### Examples (Learn by Doing)
1. `example_01_basic_whisper.py` - Standalone Whisper
2. `example_02_ros2_publisher.py` - Voice → ROS 2
3. `example_03_error_handling.py` - Graceful failures
4. `example_04_llm_planning.py` - Basic planning
5. `example_05_complex_planning.py` - Multi-step tasks
6. `example_06_end_to_end.py` - Full pipeline

### Exercises (Student Handoff)
1. `exercise_01_whisper_accuracy.py` - Measure accuracy (30 min)
2. `exercise_02_ros2_integration.py` - Build voice listener (45 min)
3. `exercise_03_plan_quality.py` - Evaluate plans (60 min)
4. `exercise_04_capstone_demo.py` - Full capstone (2-3 hours)

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `specs/004-vla-capstone/spec.md` | Feature specification |
| `specs/004-vla-capstone/plan.md` | Architecture & design |
| `specs/004-vla-capstone/tasks.md` | 63 implementation tasks |
| `specs/004-vla-capstone/data-model.md` | Entity definitions |
| `specs/004-vla-capstone/contracts/` | API contracts |
| `specs/004-vla-capstone/quickstart.md` | 25-minute setup guide |

---

## 🚀 Next Steps

1. **Start Chapter 10**: See [docs/module-4/chapter-10-voice-to-action.mdx](../Front-End-Book/docs/module-4/chapter-10-voice-to-action.mdx)
2. **Run Examples**: `cd examples && python example_01_basic_whisper.py`
3. **Complete Exercises**: See `exercises/README.md`
4. **Join Community**: GitHub Discussions, robotics forums

---

## 📄 License

MIT License - See LICENSE file

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

---

## 📞 Support

- **Documentation**: https://your-org.github.io/module-4-vla/
- **Issues**: https://github.com/your-org/module-4-vla/issues
- **Discussions**: https://github.com/your-org/module-4-vla/discussions

---

## 🙏 Acknowledgments

Built as part of the Physical AI & Humanoid Robotics Textbook project.

**Modules**: 1 (ROS 2) → 2 (Digital Twin) → 3 (NVIDIA Isaac) → 4 (VLA Capstone)

---

**Last Updated**: 2026-01-26 | **Version**: 0.1.0 (Early Development)
