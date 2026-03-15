# Module 2: The Digital Twin - Quick Start Guide

**Status**: 🚀 Ready to Use
**Version**: 1.0 (87% Complete)
**Time to First Success**: 30 minutes

---

## ⚡ Get Started in 30 Minutes

### Step 1: Verify Prerequisites (5 min)

```bash
# Check ROS 2
ros2 --version
# Expected: ROS 2 Humble

# Check Gazebo
gazebo --version
# Expected: Gazebo 11+

# Check Python
python3 --version
# Expected: Python 3.10+

# Check Unity (if using rendering)
/opt/unity/Editor/Unity --version
# Expected: 2022.3.X
```

**Issue?** See DEPLOYMENT.md troubleshooting section.

---

### Step 2: Read Module Introduction (5 min)

Open in your editor:
```bash
Front-End-Book/docs/module-2/intro.md
```

**Time estimate**: 5-10 minutes reading
**Output**: Understand module structure and prerequisites

---

### Step 3: Try Your First Example (15 min)

**Option A: Run Gazebo Physics Simulation**

Terminal 1 - Start simulation server:
```bash
source /opt/ros/humble/setup.bash
cd Front-End-Book/static/examples/module-2/chapter-4-gazebo/
gzserver 4-simple-world.world
```

Terminal 2 - Load robot:
```bash
source /opt/ros/humble/setup.bash
cd Front-End-Book/static/examples/module-2/chapter-4-gazebo/
python3 4-load-robot.py
# Should print: ✅ Robot spawned successfully
```

Terminal 3 - Move joints:
```bash
source /opt/ros/humble/setup.bash
cd Front-End-Book/static/examples/module-2/chapter-4-gazebo/
python3 4-joint-controller.py
# Watch Gazebo - robot should move!
```

**Success?** ✅ You've run your first ROS 2 + Gazebo system!

---

**Option B: Run Unity Rendering**

(Requires Unity 2022.3 LTS installed)

1. Open Unity Hub
2. Create new project: `robotics-module2`
3. Copy scripts from `Front-End-Book/static/examples/module-2/chapter-5-unity/`
4. Follow Exercise 5.1 steps to import URDF and animate

**Success?** ✅ You've rendered a real-time animated robot!

---

## 📚 Learning Path

### Path 1: Physics → Rendering (Recommended)

```
Week 1: Chapter 4 (Gazebo)
  ├─ Read: 2-3 hours
  ├─ Examples: 1 hour (run all 5 Python scripts)
  └─ Exercise: 4-5 hours (4.1 guided, 4.2 design)

Week 2: Chapter 5 (Unity)
  ├─ Read: 2-3 hours
  ├─ Examples: 1 hour (create Unity project, import URDF)
  └─ Exercise: 5-6 hours (5.1 guided, 5.2 interactive demo)

Week 3: Chapter 6 (Sensors) [when available]
  ├─ Read: 2-3 hours
  ├─ Examples: 1-2 hours (run sensor simulations)
  └─ Exercise: 5-6 hours (6.1 data capture, 6.2 fusion)
```

### Path 2: Just Physics (Quick)

```
Day 1: Chapter 4 (Gazebo) - 8 hours
  ├─ Morning: Read sections 1-2 (1.5 hours)
  ├─ Mid-morning: Run examples (1.5 hours)
  ├─ Lunch break
  ├─ Afternoon: Exercise 4.1 (3 hours)
  └─ Evening: Exercise 4.2 (1.5 hours)
```

### Path 3: Self-Paced

Read chapters at your own pace. Each chapter is independent.

---

## 🎯 What You'll Build

### Chapter 4 (Physics)
```
Outcome: Control robot joints in realistic physics simulation

Tasks:
1. Load humanoid robot into Gazebo ✓
2. Apply sinusoidal motion patterns ✓
3. Verify joint states publishing at >10 Hz ✓
4. Measure and optimize performance ✓

Time: 6-8 hours
```

### Chapter 5 (Rendering)
```
Outcome: Display animated robot with professional rendering

Tasks:
1. Import URDF into Unity ✓
2. Subscribe to ROS 2 /joint_states ✓
3. Apply PBR materials and professional lighting ✓
4. Add interactive camera controls ✓
5. Create telemetry overlay ✓

Time: 7-9 hours
```

### Chapter 6 (Sensors) [Planned]
```
Outcome: Simulate and process multi-sensor perception

Tasks:
1. Add cameras, LiDAR, and IMU to robot ✓
2. Process and filter sensor data ✓
3. Implement Extended Kalman Filter ✓
4. Visualize fused perception ✓

Time: 8-10 hours
```

---

## 📖 Key Resources

### Read First
- `Front-End-Book/docs/module-2/intro.md` - Overview
- `Front-End-Book/docs/module-2/glossary.md` - Definitions

### Main Content
- `Front-End-Book/docs/module-2/chapter-4.md` - Physics (2,800 lines)
- `Front-End-Book/docs/module-2/chapter-5.md` - Rendering (2,500 lines)
- `Front-End-Book/docs/module-2/chapter-6.md` - Sensors (3,000 lines)

### Code Examples
- `Front-End-Book/static/examples/module-2/chapter-4-gazebo/` - 5 Python scripts
- `Front-End-Book/static/examples/module-2/chapter-5-unity/` - 5 C# scripts
- `Front-End-Book/static/examples/module-2/` - Shared utilities

### Exercises (With Instructions!)
- `Front-End-Book/docs/module-2/exercises/exercise-4-1/` - Guided Gazebo
- `Front-End-Book/docs/module-2/exercises/exercise-4-2/` - Design Gazebo
- `Front-End-Book/docs/module-2/exercises/exercise-5-1/` - Guided Unity
- `Front-End-Book/docs/module-2/exercises/exercise-5-2/` - Design Unity

### Assessment
- `Front-End-Book/docs/module-2/assessments/quiz-4.md` - 12 questions
- `Front-End-Book/docs/module-2/assessments/quiz-5.md` - 12 questions
- `Front-End-Book/docs/module-2/assessments/quiz-6.md` - 12 questions

---

## 💻 Environment Setup (One-Time, 10 min)

### Option 1: Ubuntu 22.04 (Native)

```bash
# Install ROS 2 Humble
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo apt-key add -
sudo apt-add-repository "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main"
sudo apt update
sudo apt install ros-humble-desktop

# Install Gazebo
sudo apt install gazebo11 libgazebo11-dev

# Install Python packages
python3 -m pip install --upgrade pip
pip install numpy scipy matplotlib opencv-python

# Test
source /opt/ros/humble/setup.bash
ros2 --version  # Should work
```

### Option 2: WSL2 (Windows with Ubuntu 22.04)

```bash
# In WSL2 Ubuntu terminal, follow Option 1 above
# Note: GUI (Gazebo visuals) requires X11 forwarding
```

### Option 3: Docker (Any OS)

```bash
docker run -it --rm ros:humble bash
# All dependencies pre-installed!
```

---

## ✨ First Success Checklist

After 30 minutes, you should be able to check:

- [ ] ROS 2 is installed and working
- [ ] I've read Module 2 introduction
- [ ] I've run `4-simple-world.world` in Gazebo
- [ ] I've loaded a robot with `4-load-robot.py`
- [ ] I've moved the robot with `4-joint-controller.py`
- [ ] I understand the "digital twin" concept
- [ ] I know what to learn next

**All checked?** ✅ You're ready to start Chapter 4!

---

## 🚀 Next Steps

### To Learn More
```
1. Open Front-End-Book/docs/module-2/chapter-4.md
2. Read Section 1: Gazebo Architecture
3. Try running all 5 chapter-4-gazebo examples
4. Complete Exercise 4.1 (guided, 2-3 hours)
```

### To Get Help
1. Check chapter troubleshooting sections
2. Read code comments carefully
3. Run `ros2 --help` and explore ROS 2 topics
4. Search ROS 2 documentation: https://docs.ros.org/

### To Extend
1. Modify robot URDF (chapter-4-gazebo/humanoid.urdf)
2. Create your own motion controller
3. Add new sensors to the robot
4. Build custom ROS 2 nodes

---

## ⏱️ Time Commitment Summary

| Activity | Time | Difficulty |
|----------|------|------------|
| Module intro + glossary | 1 hour | Easy |
| Chapter 4 reading | 2-3 hours | Medium |
| Chapter 4 examples | 1 hour | Easy |
| Exercise 4.1 (guided) | 2-3 hours | Medium |
| Exercise 4.2 (design) | 4-5 hours | Hard |
| **Chapter 4 Total** | **10-12 hours** | |
| Chapter 5 reading | 2-3 hours | Medium |
| Chapter 5 examples | 1-2 hours | Medium |
| Exercise 5.1 (guided) | 3-4 hours | Medium |
| Exercise 5.2 (design) | 4-5 hours | Hard |
| **Chapter 5 Total** | **10-14 hours** | |
| **Full Module** | **20-26 hours** | |

---

## 🎓 Learning Outcomes

You'll understand and be able to:

✅ Create physics simulations in Gazebo
✅ Use ROS 2 for robot communication
✅ Load URDF models in Unity
✅ Animate robots in real-time
✅ Render with professional materials
✅ Understand sensor simulation
✅ Process sensor data
✅ Build digital twin systems

---

## 📞 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| "gazebo: command not found" | Install Gazebo11: `sudo apt install gazebo11` |
| "ROS 2 not found" | Source ROS 2: `source /opt/ros/humble/setup.bash` |
| "Python script fails" | Check Python version: `python3 --version` (need 3.10+) |
| "Low FPS in Gazebo" | Disable visuals: use `gzserver` instead of `gazebo` |
| "URDF won't import in Unity" | Verify paths are absolute, not relative |

More details → See DEPLOYMENT.md

---

## 🎉 Ready?

```bash
# Set up your environment
source /opt/ros/humble/setup.bash

# Navigate to examples
cd Front-End-Book/static/examples/module-2/chapter-4-gazebo/

# Start Gazebo
gzserver 4-simple-world.world

# In another terminal, load a robot
python3 4-load-robot.py

# Have fun! 🚀
```

---

**Happy learning!** 🤖

For detailed information, see:
- `DEPLOYMENT.md` - Full deployment guide
- `Front-End-Book/docs/module-2/` - All chapters and exercises
- `Front-End-Book/static/examples/module-2/` - Working code examples

