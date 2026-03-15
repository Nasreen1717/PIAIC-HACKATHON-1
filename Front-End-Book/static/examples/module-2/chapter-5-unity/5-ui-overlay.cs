using UnityEngine;
using TMPro;
using System.Collections.Generic;

/// <summary>
/// Real-Time Telemetry UI Overlay for Robot Visualization
///
/// This script creates an on-screen HUD displaying:
/// - Robot joint names and current angles (degrees and radians)
/// - ROS 2 connection status
/// - Frame rate (FPS) and latency information
/// - Message throughput (Hz)
/// - Debug information overlay
///
/// The UI is responsive and updates every frame with latest robot data.
/// Useful for presentations, demonstrations, and debugging.
///
/// Usage:
/// 1. Create a Canvas in scene (UI > Panel)
/// 2. Add TextMeshPro text elements as children
/// 3. Attach this script to Canvas
/// 4. Assign text references in Inspector
/// 5. Overlay updates automatically!
///
/// Author: Module 2 - Digital Twin
/// Date: 2026-01-22
/// License: MIT
/// </summary>
public class TelemetryDisplay : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private TextMeshProUGUI jointDisplayText;
    [SerializeField] private TextMeshProUGUI statusText;
    [SerializeField] private TextMeshProUGUI fpsText;

    [Header("Display Settings")]
    [SerializeField] private int maxJointsToDisplay = 8;    // Limit visible joints
    [SerializeField] private bool showInRadians = true;
    [SerializeField] private bool showVelocities = false;

    [Header("Colors")]
    [SerializeField] private Color connectedColor = Color.green;
    [SerializeField] private Color disconnectedColor = Color.red;
    [SerializeField] private Color warningColor = Color.yellow;

    // References
    private JointStateSubscriber jointStateSubscriber;
    private OrbitCamera orbitCamera;

    // Performance tracking
    private float fpsUpdateTimer = 0.0f;
    private float currentFps = 0.0f;
    private const float FPS_UPDATE_INTERVAL = 0.5f;  // Update FPS every 0.5s
    private Queue<float> frameTimeHistory;
    private const int FRAME_TIME_HISTORY_SIZE = 60;

    private void Start()
    {
        InitializeTelemetryDisplay();
    }

    private void InitializeTelemetryDisplay()
    {
        // Find dependencies
        jointStateSubscriber = FindObjectOfType<JointStateSubscriber>();
        orbitCamera = FindObjectOfType<OrbitCamera>();

        // Initialize frame time tracking
        frameTimeHistory = new Queue<float>(FRAME_TIME_HISTORY_SIZE);

        // Verify UI elements
        if (jointDisplayText == null || statusText == null || fpsText == null)
        {
            Debug.LogWarning("[TelemetryDisplay] Some UI text elements are not assigned!");
        }

        Debug.Log("[TelemetryDisplay] Initialized telemetry display");
    }

    private void Update()
    {
        UpdateJointDisplay();
        UpdateStatusDisplay();
        UpdatePerformanceDisplay();
    }

    private void UpdateJointDisplay()
    {
        if (jointDisplayText == null || jointStateSubscriber == null)
            return;

        var jointState = jointStateSubscriber.GetLatestJointState();
        if (jointState == null)
        {
            jointDisplayText.text = "<color=yellow>Waiting for /joint_states...</color>";
            return;
        }

        // Build display string
        string displayText = "<color=cyan><b>=== Joint Angles ===</b></color>\n";

        int jointsToShow = Mathf.Min(jointState.Name.Count, maxJointsToDisplay);
        for (int i = 0; i < jointsToShow; i++)
        {
            string jointName = jointState.Name[i];
            double position = jointState.Position[i];

            string angleStr = showInRadians
                ? $"{position:F3} rad"
                : $"{Mathf.Rad2Deg * (float)position:F1}°";

            displayText += $"<color=white>{jointName}: {angleStr}</color>\n";

            // Show velocity if enabled
            if (showVelocities && i < jointState.Velocity.Count)
            {
                double velocity = jointState.Velocity[i];
                displayText += $"  <size=80%><color=gray>v: {velocity:F3} rad/s</color></size>\n";
            }
        }

        if (jointState.Name.Count > maxJointsToDisplay)
        {
            displayText += $"<color=gray><size=80%>... and {jointState.Name.Count - maxJointsToDisplay} more joints</size></color>";
        }

        jointDisplayText.text = displayText;
    }

    private void UpdateStatusDisplay()
    {
        if (statusText == null || jointStateSubscriber == null)
            return;

        // Build status string
        string status = "";

        // ROS 2 Connection Status
        var jointState = jointStateSubscriber.GetLatestJointState();
        if (jointState != null)
        {
            status += $"<color=green>● ROS 2 Connected</color>\n";
            int messageCount = jointStateSubscriber.GetMessageCount();
            status += $"Messages: {messageCount}\n";
        }
        else
        {
            status += $"<color=red>● ROS 2 Disconnected</color>\n";
            status += "No /joint_states received\n";
        }

        // View Mode
        if (orbitCamera != null)
        {
            status += $"View: {orbitCamera.GetViewModeName()}\n";
        }

        // Time info
        status += $"\nTime: {Time.time:F1}s\n";
        status += $"Frame: {Time.frameCount}\n";

        statusText.text = status;
        statusText.color = (jointState != null) ? connectedColor : disconnectedColor;
    }

    private void UpdatePerformanceDisplay()
    {
        if (fpsText == null)
            return;

        // Update frame time history
        frameTimeHistory.Enqueue(Time.deltaTime);
        while (frameTimeHistory.Count > FRAME_TIME_HISTORY_SIZE)
            frameTimeHistory.Dequeue();

        // Calculate FPS periodically
        fpsUpdateTimer += Time.deltaTime;
        if (fpsUpdateTimer >= FPS_UPDATE_INTERVAL)
        {
            float totalTime = 0.0f;
            foreach (float frameTime in frameTimeHistory)
                totalTime += frameTime;

            float avgFrameTime = totalTime / frameTimeHistory.Count;
            currentFps = (avgFrameTime > 0) ? 1.0f / avgFrameTime : 0.0f;
            fpsUpdateTimer = 0.0f;
        }

        // Display FPS with color coding
        Color fpsColor = currentFps >= 60 ? Color.green
                       : currentFps >= 30 ? Color.yellow
                       : Color.red;

        string fpsStr = $"<color=#{ColorUtility.ToHtmlStringRGB(fpsColor)}><b>FPS: {currentFps:F1}</b></color>\n";
        fpsStr += $"Frame Time: {Time.deltaTime * 1000.0f:F2}ms\n";
        fpsStr += $"Target: 60 FPS";

        fpsText.text = fpsStr;
    }

    /// <summary>
    /// Toggle between showing angles in radians and degrees.
    /// </summary>
    public void ToggleRadiansDegrees()
    {
        showInRadians = !showInRadians;
        Debug.Log($"[TelemetryDisplay] Angle display: {(showInRadians ? "Radians" : "Degrees")}");
    }

    /// <summary>
    /// Toggle velocity display.
    /// </summary>
    public void ToggleVelocityDisplay()
    {
        showVelocities = !showVelocities;
        Debug.Log($"[TelemetryDisplay] Velocity display: {(showVelocities ? "ON" : "OFF")}");
    }

    /// <summary>
    /// Change number of joints displayed.
    /// </summary>
    public void SetMaxJointsDisplayed(int count)
    {
        maxJointsToDisplay = Mathf.Max(1, count);
        Debug.Log($"[TelemetryDisplay] Max joints to display: {maxJointsToDisplay}");
    }

    /// <summary>
    /// Get current FPS for programmatic use.
    /// </summary>
    public float GetCurrentFPS()
    {
        return currentFps;
    }

    /// <summary>
    /// Export telemetry snapshot as string.
    /// Useful for logging or debugging.
    /// </summary>
    public string ExportTelemetrySnapshot()
    {
        var jointState = jointStateSubscriber.GetLatestJointState();
        if (jointState == null)
            return "No joint state data available";

        string snapshot = $"=== Telemetry Snapshot at {System.DateTime.Now} ===\n";
        snapshot += $"FPS: {currentFps:F1}\n";
        snapshot += $"Time: {Time.time:F2}s\n";
        snapshot += "Joints:\n";

        for (int i = 0; i < jointState.Name.Count; i++)
        {
            snapshot += $"  {jointState.Name[i]}: {jointState.Position[i]:F6} rad\n";
        }

        return snapshot;
    }
}

/// <summary>
/// Helper component for keyboard shortcuts to control telemetry display.
/// </summary>
public class TelemetryShortcuts : MonoBehaviour
{
    [SerializeField] private TelemetryDisplay telemetryDisplay;

    private void Update()
    {
        if (telemetryDisplay == null)
            telemetryDisplay = FindObjectOfType<TelemetryDisplay>();

        if (telemetryDisplay == null)
            return;

        // R: Toggle radians/degrees
        if (Input.GetKeyDown(KeyCode.R))
            telemetryDisplay.ToggleRadiansDegrees();

        // V: Toggle velocity display
        if (Input.GetKeyDown(KeyCode.V))
            telemetryDisplay.ToggleVelocityDisplay();

        // 1-9: Show N joints
        for (int i = 0; i <= 8; i++)
        {
            if (Input.GetKeyDown(KeyCode.Alpha1 + i))
                telemetryDisplay.SetMaxJointsDisplayed(i == 0 ? 9 : i);
        }

        // E: Export snapshot
        if (Input.GetKeyDown(KeyCode.E))
        {
            string snapshot = telemetryDisplay.ExportTelemetrySnapshot();
            Debug.Log(snapshot);
        }
    }
}
