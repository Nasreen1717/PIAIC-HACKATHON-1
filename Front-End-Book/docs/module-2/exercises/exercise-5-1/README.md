# Exercise 5.1: Import Humanoid URDF & Animate from Gazebo

**Difficulty**: Guided (step-by-step instructions)
**Duration**: 3-4 hours
**Learning Outcomes**: Import URDF → ROS 2 integration → Real-time animation → Professional rendering

---

## Exercise Overview

In this exercise, you will:

1. **Create a Unity 2022.3 project** set up for robotics with ROS 2
2. **Import a humanoid URDF model** using the URDF Importer
3. **Verify link hierarchy** and adjust materials
4. **Subscribe to /joint_states** from a running Gazebo simulation
5. **Animate the robot in real-time** as Gazebo publishes joint angles
6. **Apply professional materials and lighting** to create a polished visualization
7. **Test performance** and ensure smooth animation (>30 FPS)

**Success Criteria** ✅:
- [ ] Unity project created with ROS 2 integration
- [ ] Humanoid URDF imported with correct link hierarchy
- [ ] Robot animates in real-time from Gazebo /joint_states
- [ ] Professional materials applied (metallic main body, contrasting joints)
- [ ] Proper lighting setup (sun + fill light)
- [ ] Performance >30 FPS with smooth animation
- [ ] No console errors or warnings

---

## Step 1: Create Unity Project & Install Dependencies (30 min)

### 1.1 Create Project

Follow Section 1 of Chapter 5:

1. Download **Unity Hub** from https://unity3d.com/download
2. Install **Unity 2022.3 LTS**
3. Create new project: `robotics-humanoid` (3D Core template)

### 1.2 Install ROS 2 for Unity

In a terminal, source ROS 2 and build C# bindings:

```bash
source /opt/ros/humble/setup.bash

cd ~/path-to-unity-project/Assets/Plugins/ROS2
git clone https://github.com/ros2/ros2_dotnet.git
cd ros2_dotnet
./build.sh --ros-distro humble
# (Takes 10-20 minutes)
```

### 1.3 Install URDF Importer

In Unity Editor:
1. **Window** → **Package Manager**
2. Click **+** → **Add package from git URL**
3. Paste: `https://github.com/rosjp/URDF-Importer.git`
4. Wait for import (1-2 minutes)

### 1.4 Verify Installation

Create test script: `Assets/Scripts/TestSetup.cs`

```csharp
using UnityEngine;
using ROS2;

public class TestSetup : MonoBehaviour
{
    private void Start()
    {
        Debug.Log("✓ ROS 2 for Unity installed correctly");
        Debug.Log("✓ URDF Importer ready");
        Debug.Log("✓ Ready to import robot!");
    }
}
```

Press **Play** in Editor. Check Console for success messages.

---

## Step 2: Prepare URDF File (15 min)

### 2.1 Create Humanoid URDF

Create file: `Assets/Models/humanoid.urdf`

```xml
<?xml version="1.0"?>
<robot name="humanoid">
  <!-- Torso (main body) -->
  <link name="base_link">
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.3 0.5 0.2"/>
      </geometry>
      <material name="grey"/>
    </visual>
  </link>

  <!-- Left Shoulder -->
  <link name="shoulder_left">
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.01" iyy="0.01" izz="0.01" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.4"/>
      </geometry>
      <material name="blue"/>
    </visual>
  </link>

  <!-- Right Shoulder -->
  <link name="shoulder_right">
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.01" iyy="0.01" izz="0.01" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.4"/>
      </geometry>
      <material name="blue"/>
    </visual>
  </link>

  <!-- Left Hip -->
  <link name="hip_left">
    <inertial>
      <mass value="3.0"/>
      <inertia ixx="0.02" iyy="0.02" izz="0.02" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.06" length="0.5"/>
      </geometry>
      <material name="grey"/>
    </visual>
  </link>

  <!-- Right Hip -->
  <link name="hip_right">
    <inertial>
      <mass value="3.0"/>
      <inertia ixx="0.02" iyy="0.02" izz="0.02" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.06" length="0.5"/>
      </geometry>
      <material name="grey"/>
    </visual>
  </link>

  <!-- Joints -->
  <joint name="shoulder_left" type="revolute">
    <parent link="base_link"/>
    <child link="shoulder_left"/>
    <origin xyz="0.15 0.25 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2"/>
  </joint>

  <joint name="shoulder_right" type="revolute">
    <parent link="base_link"/>
    <child link="shoulder_right"/>
    <origin xyz="-0.15 0.25 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2"/>
  </joint>

  <joint name="hip_left" type="revolute">
    <parent link="base_link"/>
    <child link="hip_left"/>
    <origin xyz="0.1 -0.25 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-0.785" upper="0.785" effort="20" velocity="2"/>
  </joint>

  <joint name="hip_right" type="revolute">
    <parent link="base_link"/>
    <child link="hip_right"/>
    <origin xyz="-0.1 -0.25 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-0.785" upper="0.785" effort="20" velocity="2"/>
  </joint>
</robot>
```

### 2.2 Validate URDF

```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('humanoid.urdf'); print('✓ Valid URDF')"
```

---

## Step 3: Import URDF into Unity (30 min)

### 3.1 Import via URDF Importer

1. In Project, select `Assets/Models/humanoid.urdf`
2. In Inspector, click **Import**
3. Options:
   - ✅ Import meshes
   - ✅ Create colliders
   - ✅ Create ArticulationBodies
4. Click **Import URDF**

Wait for processing (30-60 seconds).

### 3.2 Verify Hierarchy

In **Hierarchy**, you should see:

```
humanoid
├─ base_link (ArticulationBody)
│  ├─ shoulder_left (ArticulationBody)
│  ├─ shoulder_right (ArticulationBody)
│  ├─ hip_left (ArticulationBody)
│  └─ hip_right (ArticulationBody)
```

**Verify**:
- ✅ All links present
- ✅ Hierarchy matches URDF
- ✅ No missing links

### 3.3 Adjust Scale (if needed)

If robot appears too large/small:
1. Select `humanoid` root
2. In Inspector, set **Transform Scale** to adjust (usually 1.0)

---

## Step 4: Setup ROS 2 Integration (45 min)

### 4.1 Create ROS 2 Manager

Create: `Assets/Scripts/ROS2Manager.cs` (copy from Chapter 5, Section 1)

### 4.2 Create Joint State Subscriber

Create: `Assets/Scripts/JointStateSubscriber.cs` (copy from Chapter 5, Section 3)

### 4.3 Create Joint Animator

Create: `Assets/Scripts/JointAnimator.cs` (copy from Chapter 5, Section 3)

### 4.4 Add to Scene

1. Create empty GameObject: `ROS2Manager`
   - Add component: `ROS2Manager`

2. Create empty GameObject: `JointStates`
   - Add component: `JointStateSubscriber`

3. Select robot `humanoid` GameObject
   - Add component: `JointAnimator`

---

## Step 5: Setup Lighting & Materials (45 min)

### 5.1 Create Materials

Using MaterialSetup.cs from Chapter 5:

1. Create new Material: `Assets/Materials/MetallicRobot`
   - Shader: `Universal Render Pipeline/Lit`
   - Base Color: RGB(0.4, 0.4, 0.4)
   - Metallic: 0.9
   - Smoothness: 0.3

2. Create new Material: `Assets/Materials/JointPlastic`
   - Base Color: RGB(0.1, 0.1, 0.1)
   - Metallic: 0.0
   - Smoothness: 0.6

### 5.2 Apply Materials

1. Select `base_link` → Assign `MetallicRobot` material
2. Select each joint (`shoulder_*`, `hip_*`) → Assign `JointPlastic` material

### 5.3 Setup Lighting

1. Delete default light (if exists)
2. Create **Directional Light** (Sun):
   - Intensity: 1.5
   - Color: Yellowish (1.0, 0.95, 0.8)
   - Rotation: X=45, Y=45
   - Shadows: Real-time

3. Create **Point Light** (Fill):
   - Intensity: 0.3
   - Color: Blueish (0.7, 0.8, 1.0)
   - Range: 20
   - Position: Left side, lower

---

## Step 6: Test Animation (45 min)

### 6.1 Prepare Gazebo

In one terminal:

```bash
source /opt/ros/humble/setup.bash
cd ~/path-to-chapter-4-examples
gzserver 4-simple-world.world
```

### 6.2 Run Joint Controller

In another terminal:

```bash
source /opt/ros/humble/setup.bash
cd ~/path-to-chapter-4-examples
python3 4-joint-controller.py
```

Robot should be moving in Gazebo now!

### 6.3 Run Unity

Make sure ROS 2 is sourced before launching Unity:

```bash
source /opt/ros/humble/setup.bash
cd ~/robotics-humanoid
/opt/unity/Unity -projectPath .
```

In Unity Editor:
1. Click **Play**
2. **Watch your robot animate in real-time!**

Expected behavior:
- Robot appears in scene with professional materials
- Robot moves smoothly following Gazebo's joint commands
- No console errors
- FPS >30

---

## Step 7: Add Camera & UI (30 min)

### 7.1 Setup Camera Controller

1. Attach `OrbitCamera.cs` to **Main Camera**
2. Drag `humanoid` to **Target** field

Test controls:
- Right-click + drag: Rotate camera
- Scroll: Zoom
- Space: Cycle view modes
- F: Frame all

### 7.2 Add Telemetry UI

1. Create Canvas: **UI → Panel**
2. Inside Canvas, add **Text (TextMeshPro)**
3. Attach `TelemetryDisplay.cs` to Canvas
4. Assign Text element in Inspector

Now you'll see real-time joint angles on screen!

---

## Acceptance Criteria Checklist

- [ ] **Project Setup**: ROS 2 and URDF Importer installed without errors
- [ ] **URDF Import**: Humanoid robot imported with correct hierarchy
- [ ] **Link Visibility**: All 5 links (base, 2 shoulders, 2 hips) visible
- [ ] **Joint Naming**: ROS 2 joint names match GameObject names
- [ ] **Animation**: Robot moves smoothly in sync with Gazebo commands
- [ ] **Materials**: Professional metallic/plastic appearance (not gray)
- [ ] **Lighting**: Proper sun + fill light with shadows
- [ ] **Performance**: Frame rate >30 FPS (target 60 FPS)
- [ ] **No Errors**: Console shows no red error messages
- [ ] **Camera Control**: Can orbit, zoom, and frame all smoothly
- [ ] **UI Display**: Telemetry HUD shows joint angles correctly

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Robot doesn't move | ROS 2 not connected | Check Gazebo is running and publishing /joint_states |
| No /joint_states | ROS 2 environment not set | Source: `source /opt/ros/humble/setup.bash` before launch |
| Jerky motion | High latency | Enable smoothing in JointAnimator |
| Robot too small/large | Scale mismatch | Adjust Transform Scale on humanoid root |
| Materials look flat | Default materials | Create and apply custom PBR materials from MaterialSetup |
| Low FPS | Too many lights/effects | Reduce shadow quality or use light baking |
| Joint names don't match | ROS 2 vs. GameObject naming | Verify names in /joint_states match Hierarchy |

---

## Next Steps

After completing this exercise:

1. **Experiment with materials**: Create glossy metal, matte rubber, or transparent materials
2. **Add UI elements**: Create buttons to record/playback animations
3. **Try different controllers**: Run different motion patterns (circle, figure-8, etc.)
4. **Optimize rendering**: Use LOD and light baking for better FPS
5. **Move to Exercise 5.2**: Design your own interactive demonstration scene

---

## Submission

For evaluation, submit:

1. **Screenshot** of running scene with robot visible and animated
2. **Console output** showing ROS 2 connected and joint messages received
3. **Performance report** (FPS, frame time)
4. **Brief reflection** (what was hardest? what would you improve?)

---

**Congratulations!** You've built a real-time robot visualization system! 🎉
