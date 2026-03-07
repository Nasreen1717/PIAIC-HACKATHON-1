# Exercise 5.2: Create Interactive Robot Demonstration Scene

**Difficulty**: Semi-open (design-focused, architectural choices required)
**Duration**: 4-5 hours
**Learning Outcomes**: Scene design → Interactive UI → Recording/playback → Professional demonstration

---

## Exercise Overview

In this exercise, you will design and build a **professional demonstration scene** for the humanoid robot. Unlike Exercise 5.1 (guided), this exercise is **semi-open**: you make design decisions about layout, interactivity, and visualization.

**Your task**: Create a scene that convincingly demonstrates the robot to stakeholders/investors.

### Design Freedom

You decide:
- ✓ Scene layout (lab, factory, outdoor environment, custom)
- ✓ Camera angles and viewpoints
- ✓ Interactive controls (what can the user control?)
- ✓ Demonstration modes (autonomous motion, user-controlled, mixed)
- ✓ Telemetry display (what metrics matter most?)
- ✓ Visual effects (particle effects, trails, etc.)
- ✓ Recording/playback functionality

### Constraints

You must:
- ✅ Build on Exercise 5.1 (use imported humanoid robot)
- ✅ Maintain real-time animation from ROS 2
- ✅ Keep performance >30 FPS
- ✅ Document your design decisions
- ✅ Make it look professional (suitable for presentation)

---

## Step 1: Plan Your Demonstration Scene (45 min)

### 1.1 Design Document

Create file: `Assets/DESIGN.md`

Document your vision:

```markdown
# Demonstration Scene Design

## Scene Concept
[Describe the environment where the robot will be shown]
- Lab environment with instruments
- Factory floor with workstations
- Custom research facility
- Other:

## Key Viewing Angles
- [Main view angle, e.g., "3/4 view showing full robot"]
- [Detail view angle for fine joints]
- [Wide view for environment context]

## Interactive Features
- [ ] User-controlled joint angles (sliders)
- [ ] Preset motion sequences
- [ ] Task demonstration (pick, place, etc.)
- [ ] Telemetry overlay (joint angles, forces, etc.)
- [ ] Camera transitions between views
- [ ] Recording/playback of demonstrations

## Telemetry Display
Show: [Choose what metrics matter]
- Joint angles (degrees/radians)
- Joint velocities
- Power/effort estimates
- Performance metrics (FPS, latency)
- Task progress

## Visual Polish
- [ ] Realistic environment (ground, walls, lighting)
- [ ] Professional color scheme
- [ ] Status indicators (running, paused, etc.)
- [ ] Smooth transitions between modes
- [ ] Particle effects or trails
```

### 1.2 Sketch Layout

Draw (or describe) your scene layout:

```
Your Scene Layout
┌─────────────────────────────────┐
│   Demonstration Environment     │
│  ┌───────────────────────────┐  │
│  │                           │  │
│  │    [ROBOT]                │  │
│  │      (Center)             │  │
│  │                           │  │
│  └───────────────────────────┘  │
│         (Ground/Platform)       │
│                                 │
│  Camera View: [Describe angle]  │
│  Lighting: [Describe setup]     │
└─────────────────────────────────┘
```

---

## Step 2: Create Environment (45 min)

### 2.1 Build Scene Elements

In Unity Editor, create the environment:

**Ground Platform**:
1. Create Plane: **3D Object → Plane**
   - Scale: X=10, Y=1, Z=10 (large platform)
   - Material: Gray concrete or polished floor
   - Position: Y=-1 (below robot)

**Background/Walls** (choose one):

Option A - Lab environment:
```
Create: Cube walls/panels in background
Materials: White/clean lab aesthetic
```

Option B - Factory floor:
```
Create: Industrial equipment (cylinders, boxes)
Materials: Dark metallic aesthetic
```

Option C - Custom:
```
Design your own environment
```

**Lighting Environment**:
Keep sun + fill lights from Exercise 5.1, or customize:
- Main light: Professional spotlight effect
- Ambient light: Subtle fill
- Optional: Stage lighting (different colors)

### 2.2 Create a Prefab

1. Drag your designed robot + environment to **Assets/Prefabs/**
2. Save as: `DemonstrationScene.prefab`
3. Now you can easily reset to this state

---

## Step 3: Add Interactive Controls (60 min)

### 3.1 Manual Joint Control

Create: `Assets/Scripts/JointController.cs`

```csharp
using UnityEngine;
using UnityEngine.UI;

public class ManualJointController : MonoBehaviour
{
    [SerializeField] private Text statusText;
    private JointAnimator jointAnimator;
    private Dictionary<string, float> jointTargets;

    private void Start()
    {
        jointAnimator = FindObjectOfType<JointAnimator>();
        jointTargets = new Dictionary<string, float>
        {
            {"shoulder_left", 0.0f},
            {"shoulder_right", 0.0f},
            {"hip_left", 0.0f},
            {"hip_right", 0.0f},
        };
    }

    private void Update()
    {
        // Keyboard control: arrow keys move shoulders
        if (Input.GetKey(KeyCode.UpArrow))
            jointTargets["shoulder_left"] += 0.01f;
        if (Input.GetKey(KeyCode.DownArrow))
            jointTargets["shoulder_left"] -= 0.01f;

        // Implement other controls as desired
        // ...
    }

    public void SetJointTarget(string jointName, float angleRadians)
    {
        if (jointTargets.ContainsKey(jointName))
        {
            jointTargets[jointName] = angleRadians;
            statusText.text = $"Set {jointName} to {angleRadians:F2} rad";
        }
    }
}
```

### 3.2 Preset Motion Sequences

Create: `Assets/Scripts/MotionSequences.cs`

```csharp
using UnityEngine;
using System.Collections;

public class MotionSequences : MonoBehaviour
{
    private JointAnimator jointAnimator;

    private void Start()
    {
        jointAnimator = FindObjectOfType<JointAnimator>();
    }

    public void PlayWavingMotion()
    {
        StartCoroutine(WaveSequence());
    }

    private IEnumerator WaveSequence()
    {
        // Implement a waving motion:
        // 1. Raise shoulder
        // 2. Rotate shoulder in circle
        // 3. Lower shoulder
        // 4. Repeat

        for (int i = 0; i < 3; i++)
        {
            // Move shoulder up
            yield return new WaitForSeconds(1.0f);

            // Rotate in circle
            yield return new WaitForSeconds(2.0f);

            // Move down
            yield return new WaitForSeconds(1.0f);
        }

        Debug.Log("Wave motion complete!");
    }

    public void PlayBalancingMotion()
    {
        // Shift weight left/right simulating balance
    }

    public void PlayDanceMotion()
    {
        // Synchronized motion pattern
    }
}
```

### 3.3 Create UI Buttons

1. Create Canvas with buttons for:
   - **Play Demo**: Start preset motion
   - **Pause**: Stop animation
   - **Reset**: Return to neutral pose
   - **Record**: Start recording demonstration
   - **Play Back**: Replay recorded animation
   - **Camera View 1/2/3**: Switch camera angles

Example button script:
```csharp
public void OnPlayButtonClicked()
{
    GetComponent<MotionSequences>().PlayWavingMotion();
}
```

---

## Step 4: Recording & Playback (60 min)

### 4.1 Create RecordingSystem

Create: `Assets/Scripts/AnimationRecorder.cs`

```csharp
using UnityEngine;
using System.Collections.Generic;

public class AnimationRecorder : MonoBehaviour
{
    [System.Serializable]
    public struct KeyFrame
    {
        public float time;
        public Dictionary<string, float> jointAngles;
    }

    private List<KeyFrame> recordedFrames = new List<KeyFrame>();
    private bool isRecording = false;
    private float recordingStartTime;
    private JointAnimator jointAnimator;

    public void StartRecording()
    {
        recordedFrames.Clear();
        isRecording = true;
        recordingStartTime = Time.time;
        Debug.Log("Recording started");
    }

    public void StopRecording()
    {
        isRecording = false;
        Debug.Log($"Recording stopped. {recordedFrames.Count} frames recorded.");
    }

    private void Update()
    {
        if (isRecording)
        {
            // Record current joint positions
            float elapsedTime = Time.time - recordingStartTime;

            var frame = new KeyFrame
            {
                time = elapsedTime,
                jointAngles = CaptureCurrentJointAngles()
            };

            recordedFrames.Add(frame);
        }
    }

    private Dictionary<string, float> CaptureCurrentJointAngles()
    {
        // Return current joint positions from jointAnimator
        var angles = new Dictionary<string, float>();
        // ... implement
        return angles;
    }

    public void PlaybackRecording()
    {
        StartCoroutine(PlaybackRoutine());
    }

    private System.Collections.IEnumerator PlaybackRoutine()
    {
        foreach (var frame in recordedFrames)
        {
            // Apply joint angles
            yield return new WaitForSeconds(Time.deltaTime);
        }
    }
}
```

### 4.2 Create Playback UI

Add buttons:
- **Record Demo**: Start recording
- **Stop Recording**: End recording
- **Play Recording**: Replay captured motion
- **Save Recording**: Export to file (optional)

---

## Step 5: Camera System (45 min)

### 5.1 Multiple Viewpoints

Create: `Assets/Scripts/CameraManager.cs`

```csharp
using UnityEngine;

public class CameraManager : MonoBehaviour
{
    [SerializeField] private Transform[] viewpoints;  // Array of camera positions
    [SerializeField] private float transitionSpeed = 2.0f;

    private int currentViewIndex = 0;
    private Camera mainCamera;

    private void Start()
    {
        mainCamera = Camera.main;
    }

    private void Update()
    {
        // Number keys to switch views
        for (int i = 0; i < viewpoints.Length; i++)
        {
            if (Input.GetKeyDown(KeyCode.Alpha1 + i))
            {
                TransitionToView(i);
            }
        }
    }

    public void TransitionToView(int viewIndex)
    {
        if (viewIndex >= 0 && viewIndex < viewpoints.Length)
        {
            currentViewIndex = viewIndex;
            // Smoothly move camera to viewpoint
            StartCoroutine(SmoothCameraTransition(viewpoints[viewIndex]));
        }
    }

    private System.Collections.IEnumerator SmoothCameraTransition(Transform targetView)
    {
        // Lerp from current position to target position
        // Maintains smooth camera movement
        yield return null;
    }
}
```

### 5.2 Create Viewpoints

In scene:
1. Create 3-4 empty GameObjects as camera target positions
2. Position them around the robot:
   - **View 1**: Full body, 3/4 angle
   - **View 2**: Close-up of joints
   - **View 3**: Side profile
   - **View 4**: Overhead view

---

## Step 6: Documentation & Polish (45 min)

### 6.1 Create Implementation Notes

Create: `Assets/IMPLEMENTATION_NOTES.md`

Document:

```markdown
# Implementation Notes

## What Worked Well
- [Describe successful design choices]
- [Describe effective interactions]
- [Describe visual improvements]

## Challenges Overcome
- [Problem 1: Solution]
- [Problem 2: Solution]

## Performance Optimization
- Frame rate achieved: [X FPS]
- Optimization techniques used:
  - [Technique 1]
  - [Technique 2]

## Future Improvements
- [Feature that would enhance demonstration]
- [Visual improvement idea]
- [Interaction enhancement]

## Testing Notes
- Tested with Gazebo running at: [Hz]
- Network latency observed: [ms]
- Smoothing settings used: [Values]
```

### 6.2 Final Polish

- [ ] Ensure no console errors
- [ ] Test all buttons and controls
- [ ] Verify 30+ FPS performance
- [ ] Check material quality
- [ ] Verify lighting looks professional
- [ ] Test camera transitions smoothly
- [ ] Record a 30-second demo video

---

## Grading Rubric (100 points)

### Scene Design & Visual Quality (25 points)

- [ ] (5 pts) Environment is thoughtfully designed and themed
- [ ] (5 pts) Professional materials and colors (not default gray)
- [ ] (5 pts) Lighting creates realistic, appealing appearance
- [ ] (5 pts) Camera positioning shows robot effectively
- [ ] (5 pts) Overall visual polish and attention to detail

### Interactivity & Functionality (25 points)

- [ ] (5 pts) Preset motion sequences work smoothly
- [ ] (5 pts) Manual joint control responsive
- [ ] (5 pts) Camera view switching smooth and effective
- [ ] (5 pts) Recording/playback system functional
- [ ] (5 pts) UI buttons intuitive and clearly labeled

### Technical Implementation (25 points)

- [ ] (5 pts) Real-time animation synced with Gazebo
- [ ] (5 pts) Code is clean, documented, and organized
- [ ] (5 pts) Performance >30 FPS maintained
- [ ] (5 pts) No console errors or warnings
- [ ] (5 pts) Effective use of scripts and prefabs

### Documentation (25 points)

- [ ] (8 pts) DESIGN.md clearly describes decisions
- [ ] (8 pts) IMPLEMENTATION_NOTES.md documents approach
- [ ] (5 pts) Code comments explain key functionality
- [ ] (4 pts) Clear explanation of design rationale

---

## Acceptance Criteria

Submission checklist:
- [ ] Scene runs without errors
- [ ] All interactive elements work
- [ ] Performance >30 FPS
- [ ] Real-time animation from Gazebo
- [ ] Professional appearance suitable for presentation
- [ ] DESIGN.md explains your vision
- [ ] IMPLEMENTATION_NOTES.md documents technical approach
- [ ] Demo video (30 seconds) showing main features
- [ ] All code is well-commented

---

## Submission

Submit:

1. **Project folder** with all scenes, scripts, assets
2. **DESIGN.md** - Your design vision and decisions
3. **IMPLEMENTATION_NOTES.md** - Technical documentation
4. **Demo video** (MP4, 30-60 seconds) showing:
   - Scene visualization
   - Interactive controls in action
   - Camera transitions
   - Real-time robot animation
5. **Screenshot** of final scene
6. **Performance report** (FPS, frame time)

---

## Inspiration: Example Demonstration Scenes

### Lab Demo
- Clean white/gray environment
- Precision instruments in background
- Spotlight on robot
- Telemetry showing exact joint angles
- Use case: Research presentation

### Factory Floor
- Industrial environment (metal, concrete)
- Workstations and task objects
- Multiple lighting angles
- Use case: Industry/automation demo

### Showroom
- Modern, minimalist design
- Ambient background music (optional)
- Smooth camera transitions
- Use case: Investor presentations

---

## Next Steps

After completing this exercise:

1. **Add physics interactions**: Robot picks up objects, moves things
2. **Implement task demonstrations**: Predefined robot tasks
3. **Add sound effects**: Motion sounds, status beeps
4. **Create presentation mode**: Automated demo sequence
5. **Begin Chapter 6**: Sensor simulation (cameras, lidar, IMU)

---

**Excellent work!** You've created a professional robot demonstration system! 🎬
