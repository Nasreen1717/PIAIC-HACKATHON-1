# Chapter 5: High-Fidelity Rendering in Unity

**Chapter Status**: 🚀 Learning Phase
**Duration**: 8-10 hours of study
**Prerequisites**: Chapter 4 (Gazebo Physics), Module 1 (ROS 2 basics), Basic Unity knowledge (2022.3 LTS)

---

## Introduction: From Simulation to Visualization

In Chapter 4, you learned how **Gazebo** simulates physics accurately, enabling you to design and test robot control algorithms in a realistic virtual environment. But physics simulation alone tells only half the story.

Consider this scenario:

> You've implemented a complex manipulation task where your robot must:
> 1. Detect an object using simulated sensors
> 2. Plan a collision-free motion
> 3. Execute the manipulation with real-time feedback control
>
> How do you know if your algorithm is *really* working? You can:
> - Watch console logs (boring, hard to interpret)
> - Plot graphs in matplotlib (useful for analysis, not for intuition)
> - **Watch the robot move smoothly in 3D with realistic lighting** (immediate understanding!)

**This is where rendering matters.**

In this chapter, you'll learn to take your Gazebo simulation and display it in **Unity**, a professional game engine with world-class rendering capabilities. By the end, you'll have:

✅ A photorealistic 3D visualization of your robot in action
✅ Real-time joint animation from ROS 2 feedback
✅ Professional lighting, materials, and camera controls
✅ Interactive demonstrations ready to share

### Why Rendering for Robotics?

Many engineers ask: *"Why not just use Gazebo's built-in visualization (RViz2)?"*

**Good question.** RViz2 is excellent for debugging (it's fast and shows sensor data), but Unity offers advantages:

| Aspect | RViz2 | Unity |
|--------|-------|-------|
| **Visual Quality** | Functional | Photorealistic (PBR materials, advanced lighting) |
| **Rendering Speed** | Moderate (50-100 FPS) | Fast (120+ FPS on modern GPU) |
| **Interactivity** | Basic (orbit camera) | Full (custom UI, interactive objects) |
| **Deployment** | Linux/ROS 2 only | Cross-platform (Windows, Mac, Linux, Web, Mobile) |
| **Use Case** | Development debugging | Demonstrations, presentations, field deployment |
| **Learning Curve** | Shallow | Moderate (but worthwhile) |

**Real-world applications:**

- **Robot demonstrations**: Show stakeholders/investors polished videos of your robot working flawlessly
- **Field deployment**: Run a rendering client on a tablet while the robot operates autonomously
- **Training**: Use the same visualization for operator training as the actual robot deployment
- **Capstone projects**: Impress audiences with professional-quality demonstrations
- **Digital twins**: Create convincing virtual replicas for remote operation and monitoring

### Learning Objectives (SMART)

By the end of Chapter 5, you will be able to:

1. **Understand** the Unity robotics workflow:
   - Install Unity 2022.3 LTS with robotics-specific packages
   - Structure a robotics project (Scenes, Prefabs, Scripts)
   - Manage ROS 2 dependencies within Unity

2. **Import** URDF robot models into Unity:
   - Parse URDF files using the URDF Importer package
   - Convert links to GameObjects preserving hierarchy
   - Handle collision geometry and inertia properties
   - Debug import issues (scale, coordinate frames)

3. **Implement** real-time joint animation from ROS 2:
   - Subscribe to `/joint_states` topic in C#
   - Map joint states to Unity ArticulationBody components
   - Synchronize animation with physics updates
   - Handle latency and missing data gracefully

4. **Apply** professional rendering techniques:
   - Create physically-based rendering (PBR) materials
   - Set up realistic lighting (directional, point, spot lights)
   - Implement shadows and post-processing effects
   - Optimize rendering performance (LOD, light baking)

5. **Design** interactive visualization scenes:
   - Build UI overlays showing joint telemetry
   - Implement camera controls (orbit, first-person, follow)
   - Create demonstration mode with recording/playback
   - Handle real-time parameter adjustment

6. **Evaluate** rendering quality:
   - Compare visual realism against reference photos
   - Measure frame rate and latency
   - Identify performance bottlenecks
   - Apply optimization techniques

---

## Why This Chapter Matters

Imagine you're building an autonomous robot for a task. You spend weeks developing:
- Motion planning algorithms
- Perception pipelines
- Feedback control loops

All of it works perfectly in Gazebo. But then, when you show your supervisor/client a video, you see:

- A dark, minimally-textured robot moving jerkily in a gray box (Gazebo's basic rendering)
- Versus: A beautifully-lit, photorealistic robot moving smoothly through a detailed environment (Unity)

**Which one inspires confidence?** Which one looks like it could actually work in the real world?

Beyond visual appeal, **rendering enables debugging and communication**:

- **Visual debugging**: Watching the robot move is faster than reading sensor logs
- **Stakeholder communication**: Non-technical people understand video better than plots
- **Field operations**: A rendering client on a tablet lets remote operators see exactly what the robot sees
- **Continuous operation**: Use the same rendering pipeline for simulation, testing, and deployment

### Chapter Roadmap

This chapter flows through these sections:

1. **Section 1: Unity & Robotics Workflow**
   - Setting up Unity 2022.3 LTS for robotics
   - Installing ROS 2 for Unity package
   - Project structure best practices
   - Troubleshooting common setup issues

2. **Section 2: Importing URDF into Unity**
   - How URDF files define robot structure
   - Using the URDF Importer package
   - Converting URDF links → Unity GameObjects
   - Handling collision, inertia, and materials

3. **Section 3: Real-Time Joint Animation from ROS 2**
   - Subscribing to `/joint_states` in C#
   - ArticulationBody component deep dive
   - Synchronization strategy (FixedUpdate vs. Update)
   - Handling latency and data loss

4. **Section 4: Materials, Lighting & Rendering Quality**
   - Physically-based rendering (PBR) principles
   - Creating convincing robot materials
   - Lighting setup for professional appearance
   - Performance optimization techniques

5. **Section 5: Interactive Visualization & Demonstrations**
   - Building UI overlays for telemetry
   - Camera controllers (orbit, follow, first-person)
   - Interactive scene exploration
   - Recording demonstrations for presentations

---

## Prerequisites & Knowledge Requirements

**You should already know:**

- ✅ ROS 2 basics from Module 1 (topics, services, messages)
- ✅ Python for robotics (Chapter 4 code examples)
- ✅ Basic Linux command line (Ubuntu 22.04 or WSL2)

**You should have some familiarity with:**

- ⚠️ **Basic Unity knowledge** (creating scenes, prefabs, adding components) — We'll review briefly, but extensive Unity fundamentals are beyond scope. If you've never used Unity, we recommend the [Unity Beginner's Guide](https://docs.unity3d.com/Manual/GettingStarted.html) first.
- ⚠️ **C# programming** (classes, properties, public/private) — Chapter 5 code is beginner-friendly C#, but knowing basic syntax helps

**You will need installed:**

- ✅ Ubuntu 22.04 LTS (or WSL2 on Windows)
- ✅ ROS 2 Humble (sourced and functional)
- ✅ Python 3.10+ with pip
- ✅ **Unity 2022.3 LTS** (free download from [unity.com](https://unity.com/download))
- ✅ **ROS 2 for Unity** package (we'll install via Package Manager in Section 1)
- ✅ **URDF Importer** package (we'll install in Section 2)

**Estimated time investment:**

- Sections 1-2 (Setup + URDF Import): 2-3 hours
- Sections 3-4 (Animation + Rendering): 3-4 hours
- Section 5 (Interactive UI): 2-3 hours
- Exercises 5.1 & 5.2: 4-5 hours
- **Total: 11-15 hours** (we estimate 8-10 hours if you're already familiar with Unity)

---

## Key Technologies & Concepts

### Unity 2022.3 LTS

**LTS** = Long-Term Support. In short:

- Stability over cutting-edge features
- Bug fixes for 2 years
- No major breaking changes
- Perfect for production projects

Why 2022.3 specifically?
- Good ROS 2 package compatibility
- Mature ArticulationBody system (for joint animation)
- Excellent rendering pipeline (URP = Universal Render Pipeline)
- Active community support

### ROS 2 for Unity

Official package from Open Robotics that enables:

- Publish/subscribe to ROS 2 topics in C#
- Call ROS 2 services
- Access ROS 2 parameters
- Compatible with Humble (our version)

### URDF Importer

Tool that automates importing robot models:

- Parses URDF XML
- Creates GameObject hierarchy matching robot structure
- Generates colliders and rigid bodies
- Handles coordinate frame conversion

### ArticulationBody Component

Unity's system for multi-link mechanical systems:

- Each link is a GameObject with ArticulationBody
- Joints represented as ArticulationDrive (position, velocity, effort)
- Physics-based (uses PhysX engine)
- Supports limits, damping, friction

### Physically-Based Rendering (PBR)

Modern rendering approach that creates photorealistic materials:

- Based on real-world physics (how light interacts with surfaces)
- Metallic parameter (0=non-metal like plastic, 1=metal)
- Roughness parameter (0=mirror-like, 1=matte)
- Normal maps for surface detail
- More convincing than older texturing approaches

---

## Key Terms Preview

Below are terms you'll encounter frequently in this chapter. (A full glossary is in the Module 2 Glossary.)

- **GameObject**: Basic object in Unity scene (equivalent to a node/entity)
- **Prefab**: Reusable template (like a blueprint); instances inherit properties
- **Script**: C# code attached to GameObjects for behavior
- **Component**: Modular system; GameObjects have multiple components (Transform, Renderer, Collider, etc.)
- **Scene**: Unity level/environment (like a Gazebo world)
- **FixedUpdate**: Physics-based update loop (runs at fixed timestep, usually 0.02s)
- **Update**: Graphics-based update loop (runs once per frame, variable timestep)
- **Quaternion**: 4D representation of rotation (avoids gimbal lock)
- **Materials**: Properties that define how surfaces appear (color, roughness, etc.)
- **Shaders**: Programs that compute final pixel color (PBR shaders are recommended)

---

## Chapter Structure at a Glance

```
Chapter 5: High-Fidelity Rendering in Unity
│
├─ Section 1: Unity & Robotics Workflow
│  ├─ Install Unity 2022.3 LTS
│  ├─ Install ROS 2 for Unity + URDF Importer packages
│  ├─ Create project structure
│  └─ Verify ROS 2 connection
│
├─ Section 2: Importing URDF into Unity
│  ├─ URDF file format overview
│  ├─ URDF Importer workflow
│  ├─ Verify GameObject hierarchy
│  └─ Fix common import issues
│
├─ Section 3: Real-Time Joint Animation from ROS 2
│  ├─ Subscribe to /joint_states in C#
│  ├─ ArticulationBody mapping
│  ├─ Update loop synchronization
│  └─ Handle latency gracefully
│
├─ Section 4: Materials, Lighting & Rendering Quality
│  ├─ PBR materials overview
│  ├─ Create convincing robot materials
│  ├─ Professional lighting setup
│  └─ Performance optimization
│
├─ Section 5: Interactive Visualization & Demonstrations
│  ├─ UI overlays (joint names, angles)
│  ├─ Camera controllers
│  ├─ Interactive element selection
│  └─ Recording demonstrations
│
└─ Exercises 5.1 & 5.2
   ├─ Exercise 5.1: Import & animate humanoid (guided)
   └─ Exercise 5.2: Interactive demonstration scene (semi-open)
```

---

## Quick Start: What You'll Build

By the end of Section 3, you'll have:

```
Unity Scene:
├─ Humanoid Robot (imported from URDF)
│  ├─ Base Link (ArticulationBody)
│  ├─ Shoulder Left (ArticulationBody + Joint)
│  ├─ Shoulder Right (ArticulationBody + Joint)
│  └─ ... (all joints animated)
├─ Lighting Setup (sun + fill lights)
├─ Ground Plane
└─ C# Scripts
   ├─ JointAnimator.cs (subscribes to /joint_states)
   └─ Main camera
```

When you run this in Unity with Gazebo publishing `/joint_states`, the robot will move in real-time!

---

## How to Use This Chapter

**Read Sequentially**: Each section builds on the previous. Don't skip ahead.

**Hands-On**: Type out code examples rather than copy-pasting. This builds muscle memory.

**Pause & Experiment**: After each major section, try modifying example code:
- Change material colors
- Adjust light intensity
- Test different camera angles

**Check Your Understanding**: Each section includes practice problems. Use them!

**Do the Exercises**: Exercises 5.1 & 5.2 are where you integrate everything. Don't rush through them.

---

## Support Resources

Throughout this chapter, you'll see links to:

- **Official Unity Docs**: https://docs.unity3d.com/
- **ROS 2 for Unity**: https://github.com/ros2/ros2_dotnet/wiki/
- **URDF Importer**: https://github.com/rosjp/URDF-Importer
- **Gazebo Documentation**: https://classic.gazebosim.org/

When stuck:
1. Check the Troubleshooting section at end of each section
2. Search [Google Scholar](https://scholar.google.com/) or [Stack Overflow](https://stackoverflow.com/)
3. Ask in official forums:
   - [ROS 2 Discourse](https://discourse.ros.org/)
   - [Unity Forums](https://forum.unity.com/)

---

## Next Steps

Ready? Let's start with **Section 1: Unity & Robotics Workflow**. We'll get your development environment set up so you can import and animate your first robot in ~2 hours.

---

## Chapter Learning Path

```
You (with Module 1 + Chapter 4 knowledge)
      ↓
   Learn Unity Workflow (Section 1)
      ↓
   Import Robot URDF (Section 2)
      ↓
   Animate from ROS 2 (Section 3) ← KEY INTEGRATION POINT
      ↓
   Professional Rendering (Section 4)
      ↓
   Interactive Visualization (Section 5)
      ↓
   Exercise 5.1: Guided Animation (Hands-On)
      ↓
   Exercise 5.2: Interactive Demo Scene (Design-Focused)
      ↓
   Ready for Chapter 6 (Sensor Simulation)
```

---

**Let's begin!** Continue to [Section 1: Unity & Robotics Workflow](#section-1-unity--robotics-workflow).

---

## Section 1: Unity & Robotics Workflow

**Estimated Duration**: 2-3 hours
**Learning Outcomes**:
- Install and configure Unity 2022.3 LTS for robotics development
- Understand Unity project structure (Scenes, Prefabs, Scripts)
- Install ROS 2 for Unity and URDF Importer packages
- Create a minimal robotics project
- Verify ROS 2 connectivity from Unity

### 1.1 Understanding Unity's Architecture

Before diving into installation, let's understand what Unity is and how it differs from what you know from Gazebo.

**Gazebo** is a **physics simulator first**:
- Primary goal: Accurate physics simulation
- Rendering: Secondary (visualizes the physics)
- Built for: Roboticists and control engineers
- Languages: C++ (core), Python (scripting)

**Unity** is a **game engine first**:
- Primary goal: Real-time rendering and interactive experiences
- Physics: Built-in but secondary to graphics
- Built for: Game developers (also increasingly robotics!)
- Languages: C# (primary scripting language)

**Key architectural differences:**

| Aspect | Gazebo | Unity |
|--------|--------|-------|
| **Update Loop** | Physics-first (step simulation, then render) | Rendering-first (render as fast as possible) |
| **Time** | Fixed physics timestep (0.001s) | Variable frame rate (~16.7ms@60FPS) |
| **Physics Engine** | ODE/Bullet (deterministic) | PhysX (less deterministic) |
| **Rendering** | OpenGL, minimal post-processing | GPU-optimized, advanced effects |
| **Scripting** | Python + C++ plugins | C# only (no Python directly) |
| **Project Format** | Loose files (world, URDF) | Project folder with .csproj |

**What this means for you:**

When working in Unity for robotics, you'll do:
1. **Less pure physics tuning** (that's still Gazebo's job)
2. **More rendering and interaction** (making it look great!)
3. **Focus on ROS 2 integration** (connecting to the real simulation)

Think of it this way:
```
Gazebo: "Does physics accurately"
Unity:  "Makes it look beautiful and interactive"
ROS 2:  "Makes them talk to each other"
```

### 1.2 Installing Unity 2022.3 LTS

**Step 1: Download Unity Hub**

Unity Hub is the launcher/package manager for Unity. Download from:
https://unity3d.com/download

Select: **Unity Hub** (not Unity Editor directly)

Installation (all platforms):
```bash
# After downloading the installer, follow the GUI
# This typically takes 10-15 minutes
```

**Step 2: Install Unity 2022.3 LTS**

Once Hub is open:

1. Click **Installs** (left sidebar)
2. Click **Install Editor** (button)
3. Select version: **2022.3.X LTS** (X = latest patch, e.g., 2022.3.15)
4. Check boxes for:
   - ✅ **Linux Build Support** (or Windows/Mac if not on Linux)
   - ✅ **Linux Development Tools** (C# support)
   - ❌ WebGL (not needed for this course)
   - ❌ iOS/Android (not needed for this course)
5. Click **Install** (takes 20-30 minutes)

**Verify Installation:**

After installation, the Hub should show:

```
Installs
├─ 2022.3.X (green checkmark)
```

### 1.3 Creating Your First Robotics Project

**Step 1: Create Project**

In Unity Hub:

1. Click **Projects** (left sidebar)
2. Click **New project**
3. Select:
   - **Template**: 3D (Core)
   - **Project name**: `robotics-module2` (or your choice)
   - **Location**: `~/module2_robotics/` (or preferred location)
   - **Unity version**: 2022.3.X LTS
4. Click **Create project**

**Estimated wait**: 5-10 minutes (Unity opens and initializes the project)

**Step 2: Understanding Project Structure**

Once Unity Editor opens, you'll see:

```
robotics-module2/
├─ Assets/                    # All game content (scripts, scenes, prefabs, materials)
│  ├─ Scenes/                 # Unity scenes (.unity files)
│  │  └─ SampleScene.unity    # Default empty scene
│  ├─ Scripts/                # C# code files
│  ├─ Prefabs/                # Reusable templates
│  ├─ Materials/              # Material definitions
│  ├─ Models/                 # URDF imports go here
│  └─ Plugins/                # ROS 2 packages (will be installed here)
├─ Packages/                  # Package manifest (auto-managed)
├─ ProjectSettings/           # Engine configuration
└─ Library/                   # Cache (don't edit)
```

**Key folders for robotics:**

- **Assets/Scripts/**: Where you'll write C# code
- **Assets/Models/**: Where imported URDF robots go
- **Assets/Plugins/**: Where ROS 2 package will be installed

### 1.4 Installing ROS 2 for Unity

**Prerequisites:**

- ✅ ROS 2 Humble installed on your Ubuntu machine (or WSL2)
- ✅ Unity 2022.3 LTS project open
- ✅ `python3` and `pip` available

**Step 1: Install Package Dependencies**

From a terminal (Ubuntu or WSL2):

```bash
# Install required build tools
sudo apt update
sudo apt install build-essential python3-dev python3-venv

# Create virtual environment for ROS 2 Unity
python3 -m venv ~/.ros2_unity_env
source ~/.ros2_unity_env/bin/activate

# Install ROS 2 for Unity dependencies
pip install setuptools wheel
```

**Step 2: Download ROS 2 for Unity Package**

The package is available on GitHub. Clone it:

```bash
cd ~/robotics-module2  # Navigate to your Unity project
mkdir -p Assets/Plugins/ROS2
cd Assets/Plugins/ROS2

# Clone the package (this may take a minute)
git clone https://github.com/ros2/ros2_dotnet.git
cd ros2_dotnet
```

**Step 3: Build for C# in Unity**

```bash
# Build the C# bindings
./build.sh --ros-distro humble
# (This takes 10-20 minutes; lots of compilation output)
```

After completion, you should see:

```bash
[INFO] ROS 2 C# bindings built successfully
```

**Step 4: Verify Installation in Unity Editor**

Back in Unity Editor:

1. Click **Window** → **Package Manager**
2. You should see (after refresh) the ROS 2 package listed
3. Verify no error messages in the **Console** panel

**Troubleshooting:**

| Issue | Solution |
|-------|----------|
| "Could not find ROS 2" | Make sure ROS 2 Humble is sourced: `source /opt/ros/humble/setup.bash` |
| Build fails with "CMake not found" | Install: `sudo apt install cmake` |
| Permission denied on build.sh | Run: `chmod +x build.sh` |
| Package doesn't show in Unity | Restart Unity Editor and wait 1 minute for refresh |

### 1.5 Installing URDF Importer

The **URDF Importer** is a separate package that automates importing robot models from URDF files.

**Step 1: Install via Unity Package Manager**

In Unity Editor:

1. Click **Window** → **Package Manager**
2. Click **+** button (add package)
3. Select **Add package from git URL**
4. Enter: `https://github.com/rosjp/URDF-Importer.git`
5. Click **Add**

Wait for compilation (1-2 minutes).

**Step 2: Verify Installation**

In Assets folder, you should now see:
```
Assets/
├─ URDFImporter/    # New folder with importer scripts
└─ (other folders)
```

**Step 3: Download Sample URDF**

For testing, we'll use a simple humanoid URDF. Create it:

```bash
cd ~/robotics-module2/Assets/Models
mkdir -p urdf_files

# Create a simple URDF file (copy the humanoid model from Chapter 4)
# Or download from: https://github.com/ros2/gazebo_models/
```

### 1.6 Project Configuration for ROS 2

**Step 1: Create ROS 2 Manager Script**

This script initializes ROS 2 communication in your Unity project.

In Unity Editor:

1. Right-click in **Assets/Scripts/**
2. Create → C# Script
3. Name it: `ROS2Manager.cs`
4. Double-click to edit in your code editor

Paste this template:

```csharp
using UnityEngine;
using ROS2;

public class ROS2Manager : MonoBehaviour
{
    // ROS 2 environment
    private ROS2Node ros2Node;

    // Singleton pattern (only one ROS 2 Manager)
    public static ROS2Manager Instance { get; private set; }

    private void Awake()
    {
        // Ensure only one instance
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);

        // Initialize ROS 2
        InitializeROS2();
    }

    private void InitializeROS2()
    {
        Debug.Log("[ROS2Manager] Initializing ROS 2...");

        try
        {
            // Create ROS 2 node
            ros2Node = RCLdotnet.CreatePublisherNode("unity_robot_visualizer");
            Debug.Log("[ROS2Manager] ✅ ROS 2 initialized successfully!");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[ROS2Manager] ❌ Failed to initialize ROS 2: {e.Message}");
        }
    }

    public ROS2Node GetNode()
    {
        if (ros2Node == null)
        {
            Debug.LogWarning("[ROS2Manager] ROS 2 node not initialized!");
        }
        return ros2Node;
    }

    private void OnDestroy()
    {
        if (ros2Node != null)
        {
            ros2Node.Dispose();
            Debug.Log("[ROS2Manager] ROS 2 node disposed");
        }
    }
}
```

**Step 2: Add to Scene**

1. In Hierarchy (left panel), right-click on empty space
2. Create Empty → GameObject
3. Name it: `ROS2Manager`
4. In Inspector (right panel), click **Add Component**
5. Select `ROS2Manager` script
6. Now ROS 2 will initialize when you play the scene!

### 1.7 Testing the Setup

**Step 1: Create Test Script**

Create a new script: `Assets/Scripts/TestROS2Connection.cs`

```csharp
using UnityEngine;
using ROS2;

public class TestROS2Connection : MonoBehaviour
{
    private void Start()
    {
        Debug.Log("=== ROS 2 Connection Test ===");

        var node = ROS2Manager.Instance.GetNode();
        if (node != null)
        {
            Debug.Log("✅ Successfully connected to ROS 2!");
            Debug.Log($"Node name: {node.Name}");
        }
        else
        {
            Debug.LogError("❌ Failed to connect to ROS 2");
        }
    }
}
```

**Step 2: Run in Editor**

1. In Hierarchy, select the GameObject with `ROS2Manager`
2. In Inspector, add component: `TestROS2Connection`
3. Click **Play** button (top center of Editor)
4. Check Console for output:
   - ✅ Should see: "✅ Successfully connected to ROS 2!"
   - ❌ If error: "ROS 2 environment variables not set"

**If you see the error:**

Make sure ROS 2 is sourced in the terminal where you launched Unity:

```bash
source /opt/ros/humble/setup.bash
cd ~/robotics-module2
/opt/unity/Unity -projectPath .
```

### 1.8 Project Best Practices

As you develop your robotics project in Unity, follow these practices:

**1. Organize by Feature**

```
Assets/
├─ Scripts/
│  ├─ ROS2/              # ROS 2 integration
│  │  ├─ ROS2Manager.cs
│  │  └─ JointStateSubscriber.cs
│  ├─ Robot/             # Robot-specific
│  │  ├─ RobotController.cs
│  │  └─ JointAnimator.cs
│  ├─ UI/                # User interface
│  └─ Utils/             # Utilities
├─ Prefabs/
│  ├─ Robot.prefab
│  └─ UI_Panel.prefab
├─ Materials/
│  ├─ RobotMaterial.mat
│  └─ GroundMaterial.mat
└─ Scenes/
   └─ RobotSimulation.unity
```

**2. Use Prefabs for Reusability**

Instead of creating complex GameObjects in scenes, save them as Prefabs:
- Easy to duplicate (create multiple robots)
- Change once, update everywhere
- Version control friendly

**3. Separate Concerns**

- **Scripts**: C# behavior (ROS 2 integration, animation)
- **Scenes**: Level layout (where objects are placed)
- **Prefabs**: Object templates

**4. Document Your Code**

```csharp
/// <summary>
/// Animates robot joints based on ROS 2 /joint_states messages.
/// </summary>
public class JointAnimator : MonoBehaviour
{
    // ... code
}
```

### 1.9 Troubleshooting Common Issues

| Problem | Symptoms | Solution |
|---------|----------|----------|
| **ROS 2 not found** | Error: "ROS 2 environment variables not set" | Source ROS 2 before launching Unity: `source /opt/ros/humble/setup.bash` |
| **ROS 2 build failed** | "build.sh" failed during installation | Ensure cmake installed: `sudo apt install cmake` |
| **URDF Importer missing** | Can't add package from git | Check internet connection; verify GitHub URL is correct |
| **Scripts won't compile** | Red error icons in Inspector | Check for C# syntax errors (mismatched braces, missing semicolons) |
| **Play mode fails to initialize ROS 2** | Works in Editor, fails when built | Ensure ROS 2 DLLs are in Plugins folder and copied to build output |

---

### Summary of Section 1

✅ **Installed** Unity 2022.3 LTS
✅ **Created** a robotics-ready project structure
✅ **Installed** ROS 2 for Unity and URDF Importer packages
✅ **Initialized** ROS 2 communication in a test scene
✅ **Verified** connectivity with a simple test script

**Next**: You're ready to import URDF robot models! Proceed to Section 2.

---

## Section 2: Importing URDF into Unity

**Estimated Duration**: 2-3 hours
**Learning Outcomes**:
- Understand URDF file structure and its limitations in game engines
- Use URDF Importer to convert robot models to Unity GameObjects
- Handle coordinate frame conversions and scaling issues
- Set up collision geometry and physics properties
- Debug import problems systematically

### 2.1 Understanding URDF Format

You've seen URDF (Unified Robot Description Format) in Chapter 4 for physics simulation. Let's review its structure briefly:

**URDF Key Elements**:

```xml
<robot name="humanoid">
  <!-- Links: rigid bodies -->
  <link name="base_link">
    <inertial>...</inertial>      <!-- Mass/inertia for physics -->
    <visual>...</visual>           <!-- What it looks like -->
    <collision>...</collision>     <!-- For collision detection -->
  </link>

  <!-- Joints: connections between links -->
  <joint name="shoulder_left" type="revolute">
    <parent link="torso"/>
    <child link="arm_left"/>
    <origin xyz="0 0.1 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2"/>
  </joint>
</robot>
```

**Why URDF Alone Isn't Enough for Rendering**:

URDF was designed for physics and ROS, not game engines. Issues:

| Issue | Example | Solution |
|-------|---------|----------|
| **No materials** | "This cylinder is gray, no texture" | URDF Importer creates basic materials; you customize in Unity |
| **Simple geometry** | Only boxes, cylinders, spheres, meshes | Unity converts to 3D models, you add PBR materials |
| **No lighting info** | URDF has no light definitions | You set up lights in Unity scene |
| **Coordinate frames** | URDF uses Z-up, some engines use Y-up | URDF Importer auto-converts |
| **Scale ambiguity** | URDF says "1.0 meter" but no info on rendering scale | You explicitly set in Unity (1 unit = 1 meter) |

### 2.2 The URDF Importer Workflow

**High-Level Process**:

```
Your URDF file
       ↓
URDF Parser (reads XML)
       ↓
Link→GameObject conversion
       ↓
Joint creation (ArticulationBody)
       ↓
Material generation (default gray)
       ↓
Result: Full robot hierarchy in Unity
       ↓
You: Polish with better materials & lighting
```

### 2.3 Preparing Your URDF

Before importing, ensure your URDF is clean:

**Checklist**:

- ✅ **Valid XML**: Test with: `python3 -c "import xml.etree.ElementTree as ET; ET.parse('robot.urdf')"`
- ✅ **Mesh paths are absolute**: Change `package://humanoid/meshes/base.stl` to full path `/home/user/humanoid/meshes/base.stl`
- ✅ **All links have names**: `<link name="base_link">` (no empty names)
- ✅ **All joints have limits**: Revolute joints need `<limit>` (even if wide)
- ✅ **Inertia is reasonable**: Check mass > 0 and inertia positive

**Example URDF for Import** (simplified humanoid):

```xml
<?xml version="1.0"?>
<robot name="humanoid">
  <link name="base_link">
    <inertial>
      <mass value="10"/>
      <inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.2 0.4 0.5"/>
      </geometry>
      <material name="grey">
        <color rgba="0.5 0.5 0.5 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.2 0.4 0.5"/>
      </geometry>
    </collision>
  </link>

  <link name="arm_left">
    <inertial>
      <mass value="2"/>
      <inertia ixx="0.05" iyy="0.05" izz="0.05" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.4"/>
      </geometry>
      <material name="blue"/>
    </visual>
  </link>

  <joint name="shoulder_left" type="revolute">
    <parent link="base_link"/>
    <child link="arm_left"/>
    <origin xyz="0 0.2 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2"/>
  </joint>
</robot>
```

### 2.4 Importing into Unity

**Step 1: Copy URDF to Project**

```bash
cp humanoid.urdf ~/robotics-module2/Assets/Models/
```

**Step 2: Import in Unity Editor**

1. In Inspector, select the URDF file
2. You should see an "Import" button in the Inspector panel
3. Click **Import**
4. Select options:
   - ✅ **Import mesh** (use geometry)
   - ✅ **Create collider** (add collision geometry)
   - ✅ **Animate robot** (create ArticulationBody for joints)

**Step 3: Review Imported Structure**

In Hierarchy, you should see:

```
humanoid (root GameObject)
├─ base_link (ArticulationBody + Collider + MeshRenderer)
│  ├─ arm_left (ArticulationBody + Joint drive)
│  └─ arm_right (ArticulationBody + Joint drive)
└─ (all other links similarly nested)
```

### 2.5 Handling Common Import Issues

**Issue 1: Model appears too large or too small**

**Cause**: URDF scale vs. Unity scale mismatch

**Fix**:
1. Select the root robot GameObject in Hierarchy
2. In Inspector, find **Transform** component
3. Set **Scale** to correct value (usually 1.0 for 1 meter = 1 Unity unit)
4. Or scale individual meshes in their materials

**Issue 2: Joints are locked (can't rotate)**

**Cause**: Joint limits may be missing or ArticulationBody not configured

**Fix**:
1. Select a joint GameObject (e.g., `shoulder_left`)
2. In Inspector, find **ArticulationBody** component
3. Verify **Joint Type** = "Revolute" (or appropriate type)
4. Check **Constrain** settings (should NOT be locked)
5. Set **Drive** values:
   - Target: 0 (neutral position)
   - Stiffness: 10000 (resists motion)
   - Damping: 1000 (smooths movement)

**Issue 3: Collision doesn't work**

**Cause**: Missing collider or collision geometry empty

**Fix**:
1. Select link GameObject
2. Ensure **Collider** component exists (e.g., BoxCollider)
3. If mesh imported, use **MeshCollider** instead:
   - Add Component → Physics → Mesh Collider
   - **Convex**: Checked (for dynamic objects)
   - **Use Gravity**: Checked (if you want physics)

**Issue 4: Model rotates strangely**

**Cause**: Coordinate frame mismatch (ROS uses Z-up, some game engines use Y-up)

**Fix**: The URDF Importer should auto-convert, but if not:
1. Select root robot GameObject
2. Rotate to correct orientation:
   - Rotation X: 0, Y: 0, Z: 0 (Z-up, standard for ROS)
   - Or Rotation X: 90 (if Y-up after import)

### 2.6 Customize Materials After Import

After import, all materials are likely plain gray. Let's make them professional:

**Step 1: Create Custom Material**

1. Right-click in **Assets/Materials/** folder
2. Create → Material
3. Name it: `RobotMetallic`
4. In Inspector, set:
   - **Shader**: `Universal Render Pipeline/Lit` (or `Standard`)
   - **Base Color**: Select a color (e.g., dark gray)
   - **Metallic**: 0.8 (robot is metallic)
   - **Smoothness**: 0.3 (not perfectly shiny)

**Step 2: Assign to Robot**

1. Select a link GameObject (e.g., `base_link`)
2. In Inspector, find **Mesh Renderer** component
3. In **Materials**, assign your custom material
4. Repeat for all visible links

**Result**: Your robot now looks metallic and professional!

### 2.7 Verify Import Quality

**Checklist**:

- ✅ **Hierarchy is correct**: All links nested properly as in URDF
- ✅ **All links visible**: No hidden or transparent parts
- ✅ **Joints can rotate**: Select a joint, check ArticulationBody can move
- ✅ **Colliders present**: Visualize colliders (Physics Debug View in Scene window)
- ✅ **Materials applied**: No bright neon colors (unless intentional)
- ✅ **No errors in Console**: Red X means problems (investigate!)

---

## Section 3: Real-Time Joint Animation from ROS 2

**Estimated Duration**: 2-3 hours
**Learning Outcomes**:
- Subscribe to `/joint_states` topic in C#
- Map ROS 2 joint messages to Unity ArticulationBody
- Implement smooth animation despite network latency
- Handle missing or delayed messages gracefully
- Synchronize animation with physics updates

### 3.1 The Animation Problem

Once your robot is imported into Unity, you want it to move based on ROS 2 joint state messages.

**Data flow**:

```
Gazebo Simulation
    ↓ (publishes every 10 ms)
ROS 2 Topic /joint_states
    ↓ (sent over network)
Unity Subscriber
    ↓ (receives message)
C# Script reads joint angles
    ↓
Sets ArticulationBody.xDrive.targetPosition
    ↓
UnityPhysX engine updates
    ↓
GameObject rotates smoothly
    ↓
Camera renders beautiful result
```

**Challenges**:

1. **Latency**: Message might arrive 50-200 ms after Gazebo generated it
2. **Variable rate**: Network drops frames or receives burst
3. **Time sync**: Robot's clock ≠ rendering clock
4. **Missing data**: If a joint message is lost, what do you show?

### 3.2 Creating a Joint State Subscriber

**Step 1: Create C# Script**

In **Assets/Scripts/ROS2/**, create: `JointStateSubscriber.cs`

```csharp
using UnityEngine;
using ROS2;
using sensor_msgs = ROS2.Sensor.Msgs;

public class JointStateSubscriber : MonoBehaviour
{
    // ROS 2 subscription
    private ISubscription<sensor_msgs.JointState> jointStateSubscriber;

    // Latest message
    private sensor_msgs.JointState latestJointState;

    // Synchronization
    private object lockObject = new object();

    // Debug
    private int messageCount = 0;

    private void Start()
    {
        Debug.Log("[JointStateSubscriber] Initializing joint state subscriber...");

        try
        {
            // Get ROS 2 node from manager
            var node = ROS2Manager.Instance.GetNode();
            if (node == null)
            {
                Debug.LogError("[JointStateSubscriber] ROS 2 node is not available");
                return;
            }

            // Create subscriber to /joint_states
            jointStateSubscriber = node.CreateSubscription<sensor_msgs.JointState>(
                "/joint_states",
                JointStateCallback
            );

            Debug.Log("[JointStateSubscriber] ✅ Joint state subscriber created");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[JointStateSubscriber] ❌ Failed to create subscriber: {e.Message}");
        }
    }

    private void JointStateCallback(sensor_msgs.JointState message)
    {
        // Store message safely (thread-safe)
        lock (lockObject)
        {
            latestJointState = message;
            messageCount++;

            if (messageCount % 10 == 0)  // Log every 10 messages to avoid spam
            {
                Debug.Log($"[JointStateSubscriber] Received {messageCount} messages. " +
                         $"Joints: {message.Name.Count}");
            }
        }
    }

    public sensor_msgs.JointState GetLatestJointState()
    {
        lock (lockObject)
        {
            return latestJointState;
        }
    }

    public int GetMessageCount()
    {
        lock (lockObject)
        {
            return messageCount;
        }
    }

    private void OnDestroy()
    {
        if (jointStateSubscriber != null)
        {
            jointStateSubscriber.Dispose();
            Debug.Log("[JointStateSubscriber] Disposed");
        }
    }
}
```

### 3.3 Creating a Joint Animator

Now create the script that actually moves the robot:

In **Assets/Scripts/Robot/**, create: `JointAnimator.cs`

```csharp
using UnityEngine;
using System.Collections.Generic;

public class JointAnimator : MonoBehaviour
{
    // Reference to each joint's ArticulationBody
    private Dictionary<string, ArticulationBody> jointDictionary =
        new Dictionary<string, ArticulationBody>();

    // Joint state subscriber
    private JointStateSubscriber jointStateSubscriber;

    // Animation settings
    [Header("Animation")]
    [SerializeField] private float smoothingFactor = 0.7f;  // 0-1, higher = smoother
    [SerializeField] private float maxVelocity = 2.0f;      // rad/s

    private void Start()
    {
        Debug.Log("[JointAnimator] Initializing joint animator...");

        // Find subscriber on this GameObject or parent
        jointStateSubscriber = GetComponent<JointStateSubscriber>();
        if (jointStateSubscriber == null)
        {
            jointStateSubscriber = FindObjectOfType<JointStateSubscriber>();
        }

        if (jointStateSubscriber == null)
        {
            Debug.LogError("[JointAnimator] JointStateSubscriber not found!");
            return;
        }

        // Build dictionary of all joints in robot hierarchy
        BuildJointDictionary();
    }

    private void BuildJointDictionary()
    {
        jointDictionary.Clear();

        // Find all ArticulationBody components in children
        ArticulationBody[] allArticulations = GetComponentsInChildren<ArticulationBody>();

        foreach (var ab in allArticulations)
        {
            jointDictionary[ab.gameObject.name] = ab;
        }

        Debug.Log($"[JointAnimator] Built joint dictionary with {jointDictionary.Count} joints");
    }

    private void FixedUpdate()
    {
        // Get latest joint state from subscriber
        var jointState = jointStateSubscriber.GetLatestJointState();
        if (jointState == null)
        {
            return;  // No message received yet
        }

        // Update each joint
        for (int i = 0; i < jointState.Name.Count; i++)
        {
            string jointName = jointState.Name[i];
            double jointPosition = jointState.Position[i];

            if (jointDictionary.TryGetValue(jointName, out var articulation))
            {
                UpdateJoint(articulation, (float)jointPosition);
            }
            else
            {
                // Joint name in ROS message doesn't match GameObject name
                // Log once per joint to avoid spam
            }
        }
    }

    private void UpdateJoint(ArticulationBody joint, float targetPosition)
    {
        // Set target position for ArticulationBody
        var drive = joint.xDrive;
        drive.target = targetPosition;  // In radians
        joint.xDrive = drive;

        // Alternative: Apply with smoothing (for slow networks)
        // var currentPos = joint.xDrive.target;
        // var smoothedPos = Mathf.Lerp(currentPos, targetPosition, smoothingFactor);
        // drive.target = smoothedPos;
        // joint.xDrive = drive;
    }
}
```

### 3.4 Adding to Your Scene

**Step 1: Add JointStateSubscriber**

1. Create empty GameObject: `JointStates`
2. Add component: `JointStateSubscriber`

**Step 2: Add JointAnimator**

1. Select your imported robot root GameObject
2. Add component: `JointAnimator`
3. In Inspector, adjust:
   - **Smoothing Factor**: 0.7 (adjust for latency)
   - **Max Velocity**: 2.0 (safety limit)

**Step 3: Run in Play Mode**

1. Start Gazebo with your robot: `gzserver 4-simple-world.world`
2. In another terminal, run a controller to publish joint states:
   ```bash
   python3 4-joint-controller.py
   ```
3. In Unity Editor, click **Play**
4. **Watch your robot move in sync with Gazebo!**

### 3.5 Handling Latency and Smoothing

If your animation looks jittery due to network latency:

**Option 1: Increase Smoothing**

```csharp
// In JointAnimator.cs
var currentPos = joint.xDrive.target;
var smoothedPos = Mathf.Lerp(currentPos, targetPosition, 0.5f);  // More smoothing
drive.target = smoothedPos;
joint.xDrive = drive;
```

**Option 2: Implement Linear Interpolation**

Store previous position and time, interpolate between them:

```csharp
private Dictionary<string, (float position, float time)> jointHistory =
    new Dictionary<string, (float, float)>();

private void UpdateJoint(ArticulationBody joint, float targetPosition)
{
    string name = joint.name;
    float currentTime = Time.time;

    if (jointHistory.TryGetValue(name, out var prev))
    {
        float dt = currentTime - prev.time;
        float velocity = (targetPosition - prev.position) / dt;
        velocity = Mathf.Clamp(velocity, -maxVelocity, maxVelocity);

        float smoothPos = prev.position + velocity * Time.deltaTime;

        var drive = joint.xDrive;
        drive.target = smoothPos;
        joint.xDrive = drive;
    }

    jointHistory[name] = (targetPosition, currentTime);
}
```

### 3.6 Debugging Animation Issues

**Problem: Robot doesn't move**

Debug checklist:
1. Check Console for errors (red X)
2. Verify `/joint_states` is publishing:
   ```bash
   ros2 topic hz /joint_states
   ```
3. Verify joint names match:
   ```bash
   ros2 topic echo /joint_states --once
   # Compare "name" field with GameObject names in Unity Hierarchy
   ```
4. Check JointAnimator.cs BuildJointDictionary() output in Console

**Problem: Motion is jerky or stuttering**

Solutions:
1. Increase Smoothing Factor (0.5 → 0.8)
2. Check network latency: `ping <gazebo-machine>`
3. Reduce Gazebo publish rate if it's too fast (modify controller script)
4. Use FixedUpdate instead of Update

---

## Section 4: Materials, Lighting & Rendering Quality

**Estimated Duration**: 2-3 hours
**Learning Outcomes**:
- Understand physically-based rendering (PBR) principles
- Create convincing robot materials (metallic, plastic, matte)
- Set up professional lighting (directional, point, spot lights)
- Implement real-time shadows and post-processing effects
- Optimize rendering for performance (LOD, light baking)

### 4.1 PBR (Physically-Based Rendering) Basics

Modern rendering uses **PBR**, which simulates real-world physics:

- **Albedo (base color)**: What color is it?
- **Metallic**: Is it metal (1.0) or non-metal (0.0)?
- **Roughness**: Is it shiny (0.0) or matte (1.0)?
- **Normal map**: Fine surface detail (optional)

**Why PBR?**

Traditional materials (diffuse + specular) looked plastic-y. PBR creates photorealistic materials because it's based on physics.

### 4.2 Creating Robot Materials

**Example: Metallic Robot Material**

1. In **Assets/Materials/**, create new Material: `RobotMetal`
2. Set shader: `Universal Render Pipeline/Lit`
3. Properties:
   - **Base Color**: RGB (0.4, 0.4, 0.4) - dark gray
   - **Metallic**: 0.9 (it's metallic!)
   - **Smoothness**: 0.2 (industrial finish, not shiny)

**Result**: Robot looks like brushed aluminum

**Example: Plastic Joint Cover**

1. Create Material: `PlasticBlack`
2. Shader: `Universal Render Pipeline/Lit`
3. Properties:
   - **Base Color**: RGB (0.1, 0.1, 0.1) - black
   - **Metallic**: 0.0 (not metal)
   - **Smoothness**: 0.6 (plastic is somewhat smooth)

### 4.3 Professional Lighting Setup

Lighting makes or breaks photorealism.

**Step 1: Remove default light**

In Hierarchy, delete the default "Directional Light" (if present)

**Step 2: Add Sun Light**

1. Right-click in Hierarchy → Light → Directional
2. Name it: `SunLight`
3. In Inspector:
   - **Intensity**: 1.5
   - **Color**: Slight yellow (RGB: 1.0, 0.95, 0.8)
   - **Rotation**: X=45, Y=45 (sun from upper-right)
   - **Render Shadows**: Enabled (real-time soft shadows)

**Step 3: Add Fill Light**

1. Right-click in Hierarchy → Light → Point
2. Name it: `FillLight`
3. In Inspector:
   - **Intensity**: 0.3
   - **Color**: Slight blue (RGB: 0.7, 0.8, 1.0)
   - **Range**: 20
   - **Position**: Left side of robot, lower

**Result**: Robot has natural shadows + subtle fill light (professional look!)

### 4.4 Post-Processing Effects

Unity's post-processing adds final polish:

1. Install Post-Processing package (if not already):
   - Window → Package Manager
   - Search "post-processing"
   - Install

2. Create Post-Process Volume:
   - Right-click in Hierarchy → Volume → Global Volume
   - Name it: `PostProcessing`

3. Add effects:
   - **Bloom**: Bright edges glow slightly (intensity 0.5)
   - **Tone Mapping**: Better color accuracy
   - **Ambient Occlusion**: Shadows in corners (subtle)

**Result**: Robot looks cinematic!

### 4.5 Optimizing Rendering Performance

If FPS drops below 60:

**Technique 1: LOD (Level of Detail)**

- Complex models at close range
- Simpler models at distance

In your robot prefab:
1. Select a complex link
2. Add component → Rendering → LOD Group
3. Set different mesh resolutions at different distances

**Technique 2: Light Baking**

For static objects (ground, walls):
1. Set objects as "Static" (checkbox in Inspector)
2. Window → Rendering → Lighting
3. Click "Generate Lighting"
4. Baked lightmaps replace real-time lights

**Technique 3: Reduce Shadow Quality**

In Lighting window:
- **Shadow Resolution**: Lower (e.g., 1024 instead of 4096)
- **Shadow Cascades**: 1 instead of 4

---

## Section 5: Interactive Visualization & Demonstrations

**Estimated Duration**: 2-3 hours
**Learning Outcomes**:
- Build UI overlays showing robot telemetry (joint angles, velocities)
- Implement camera controllers (orbit, follow, first-person)
- Create interactive scene exploration tools
- Record demonstrations for presentations

### 5.1 UI Overlay for Joint Telemetry

**Step 1: Create Canvas**

1. Right-click in Hierarchy → UI → Panel
2. A Canvas automatically appears
3. Rename to: `TelemetryUI`

**Step 2: Create Text Elements**

Inside Canvas, add:
1. Text (TextMeshPro): `JointDisplay`
   - Font Size: 36
   - Position: Top-left corner
   - Content: "Joints: Loading..."

**Step 3: Script to Update Telemetry**

Create: **Assets/Scripts/UI/TelemetryDisplay.cs**

```csharp
using UnityEngine;
using TMPro;

public class TelemetryDisplay : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI jointDisplayText;
    private JointStateSubscriber jointStateSubscriber;

    private void Start()
    {
        jointStateSubscriber = FindObjectOfType<JointStateSubscriber>();
    }

    private void Update()
    {
        var jointState = jointStateSubscriber.GetLatestJointState();
        if (jointState == null)
        {
            jointDisplayText.text = "Waiting for joint states...";
            return;
        }

        string displayText = "=== Joint Angles ===\n";
        for (int i = 0; i < jointState.Name.Count && i < 4; i++)
        {
            float angle = Mathf.Rad2Deg * (float)jointState.Position[i];
            displayText += $"{jointState.Name[i]}: {angle:F1}°\n";
        }

        jointDisplayText.text = displayText;
    }
}
```

### 5.2 Camera Controller

**Step 1: Create Orbit Camera**

Create: **Assets/Scripts/Camera/OrbitCamera.cs**

```csharp
using UnityEngine;

public class OrbitCamera : MonoBehaviour
{
    [SerializeField] private Transform target;  // Robot to orbit around
    [SerializeField] private float distance = 5.0f;
    [SerializeField] private float rotationSpeed = 2.0f;
    [SerializeField] private float scrollSpeed = 1.0f;

    private float rotationX = 0;
    private float rotationY = 0;

    private void Update()
    {
        // Mouse look (right-click to rotate)
        if (Input.GetMouseButton(1))
        {
            rotationX += Input.GetAxis("Mouse X") * rotationSpeed;
            rotationY -= Input.GetAxis("Mouse Y") * rotationSpeed;
            rotationY = Mathf.Clamp(rotationY, -90, 90);
        }

        // Zoom (scroll wheel)
        distance -= Input.GetAxis("Mouse ScrollWheel") * scrollSpeed;
        distance = Mathf.Clamp(distance, 0.5f, 20.0f);

        // Update camera position
        Quaternion rotation = Quaternion.Euler(rotationY, rotationX, 0);
        Vector3 offset = rotation * Vector3.back * distance;

        transform.position = target.position + offset;
        transform.LookAt(target.position + Vector3.up * 0.5f);  // Look at center, slightly up
    }
}
```

**Step 2: Add to Camera**

1. Select **Main Camera** in Hierarchy
2. Add component: **OrbitCamera**
3. Drag robot GameObject to **Target** field

### 5.3 Recording Demonstrations

To create a demo video:

1. Use **Window → Recorder → Recorder Window**
2. Set:
   - **Output Path**: `~/Videos/robot_demo.mp4`
   - **Resolution**: 1920x1080
   - **Frame Rate**: 30 FPS
3. Click **Start Recording**
4. Let robot animate for 10-15 seconds
5. Click **Stop**
6. Video saved! Share with team/stakeholders

---

### Summary of Chapter 5

✅ **Set up** Unity 2022.3 LTS with ROS 2 integration
✅ **Imported** URDF robot models
✅ **Animated** robot joints from ROS 2 messages
✅ **Applied** professional materials and lighting
✅ **Created** interactive visualization tools

**Next**: Exercise 5.1 (guided) and Exercise 5.2 (design-focused) let you integrate everything!

---
