using UnityEngine;
using ROS2;
using sensor_msgs = ROS2.Sensor.Msgs;
using System.Collections.Generic;

/// <summary>
/// Real-Time Joint Animation from ROS 2 /joint_states
///
/// This runtime script animates robot joints based on messages received from
/// ROS 2 /joint_states topic. It:
/// - Subscribes to /joint_states messages from Gazebo
/// - Maps joint names to ArticulationBody components
/// - Updates joint targets in real-time
/// - Handles network latency with optional smoothing
/// - Provides debug info via Console
///
/// Usage:
/// 1. Attach to root of imported robot GameObject
/// 2. Ensure JointStateSubscriber exists in scene
/// 3. Run with Gazebo publishing /joint_states
/// 4. Robot animates in real-time!
///
/// Dependencies:
/// - ROS 2 for Unity package
/// - JointStateSubscriber script
/// - Imported robot with ArticulationBody components
///
/// Author: Module 2 - Digital Twin
/// Date: 2026-01-22
/// License: MIT
/// </summary>
public class JointAnimator : MonoBehaviour
{
    [Header("Joint Animation Settings")]
    [SerializeField] private float smoothingFactor = 0.7f;      // 0-1: higher = smoother motion
    [SerializeField] private float maxVelocity = 2.0f;          // rad/s: safety limit
    [SerializeField] private bool enableSmoothing = false;      // Toggle smoothing
    [SerializeField] private bool debugLogging = true;          // Console debug messages

    // Internal state
    private Dictionary<string, ArticulationBody> jointDictionary;
    private Dictionary<string, (float position, float time)> jointHistory;
    private JointStateSubscriber jointStateSubscriber;
    private int framesSinceLastUpdate = 0;

    private void Start()
    {
        InitializeJointAnimator();
    }

    private void InitializeJointAnimator()
    {
        if (debugLogging)
            Debug.Log("[JointAnimator] Initializing joint animator...");

        // Initialize dictionaries
        jointDictionary = new Dictionary<string, ArticulationBody>();
        jointHistory = new Dictionary<string, (float, float)>();

        // Find JointStateSubscriber in scene
        jointStateSubscriber = FindObjectOfType<JointStateSubscriber>();
        if (jointStateSubscriber == null)
        {
            Debug.LogError("[JointAnimator] ✗ JointStateSubscriber not found in scene! " +
                          "Create a GameObject with JointStateSubscriber component.");
            enabled = false;
            return;
        }

        // Build joint dictionary
        BuildJointDictionary();

        if (debugLogging)
            Debug.Log($"[JointAnimator] ✓ Initialized with {jointDictionary.Count} joints");
    }

    /// <summary>
    /// Recursively find all ArticulationBody components in robot hierarchy
    /// and map them by GameObject name.
    /// </summary>
    private void BuildJointDictionary()
    {
        jointDictionary.Clear();

        ArticulationBody[] allArticulations = GetComponentsInChildren<ArticulationBody>();

        foreach (var ab in allArticulations)
        {
            jointDictionary[ab.gameObject.name] = ab;
        }

        if (debugLogging)
        {
            Debug.Log("[JointAnimator] Joint mapping:");
            foreach (var kvp in jointDictionary)
            {
                Debug.Log($"  {kvp.Key} -> ArticulationBody");
            }
        }
    }

    private void FixedUpdate()
    {
        // Get latest message from subscriber
        var jointState = jointStateSubscriber.GetLatestJointState();
        if (jointState == null)
        {
            framesSinceLastUpdate++;
            return;
        }

        framesSinceLastUpdate = 0;

        // Update each joint in the message
        for (int i = 0; i < jointState.Name.Count; i++)
        {
            string jointName = jointState.Name[i];
            double jointPosition = i < jointState.Position.Count ? jointState.Position[i] : 0.0;

            // Try to find matching ArticulationBody
            if (jointDictionary.TryGetValue(jointName, out var articulation))
            {
                UpdateJoint(articulation, jointName, (float)jointPosition);
            }
            else if (debugLogging && i == 0)  // Log mismatch once
            {
                Debug.LogWarning($"[JointAnimator] Joint '{jointName}' from ROS 2 not found in robot. " +
                               $"Check that ROS 2 joint names match GameObject names.");
            }
        }

        // Debug: Log every 100 frames
        if (debugLogging && (int)Time.frameCount % 100 == 0)
        {
            int messageCount = jointStateSubscriber.GetMessageCount();
            Debug.Log($"[JointAnimator] Frame {Time.frameCount}: {messageCount} messages received");
        }
    }

    /// <summary>
    /// Update a single joint's target position.
    /// Optionally applies smoothing if enabled.
    /// </summary>
    private void UpdateJoint(ArticulationBody joint, string jointName, float targetPosition)
    {
        if (enableSmoothing)
        {
            UpdateJointSmoothed(joint, jointName, targetPosition);
        }
        else
        {
            UpdateJointDirect(joint, targetPosition);
        }
    }

    /// <summary>
    /// Direct update: immediately set target position (no smoothing).
    /// Best for real-time, low-latency connections.
    /// </summary>
    private void UpdateJointDirect(ArticulationBody joint, float targetPosition)
    {
        var drive = joint.xDrive;
        drive.target = targetPosition;
        joint.xDrive = drive;
    }

    /// <summary>
    /// Smoothed update: interpolate between previous and new position.
    /// Reduces jittery motion on high-latency networks.
    /// </summary>
    private void UpdateJointSmoothed(ArticulationBody joint, string jointName, float targetPosition)
    {
        float smoothedPosition = targetPosition;

        if (jointHistory.TryGetValue(jointName, out var prev))
        {
            float currentTime = Time.time;
            float dt = currentTime - prev.time;

            if (dt > 0.001f)  // Avoid division by zero
            {
                // Compute velocity
                float velocity = (targetPosition - prev.position) / dt;
                velocity = Mathf.Clamp(velocity, -maxVelocity, maxVelocity);

                // Interpolate using clamped velocity
                smoothedPosition = prev.position + velocity * Time.deltaTime;
            }
        }

        // Update joint
        var drive = joint.xDrive;
        drive.target = smoothedPosition;
        joint.xDrive = drive;

        // Record history
        jointHistory[jointName] = (targetPosition, Time.time);
    }

    /// <summary>
    /// Enable/disable joint animator at runtime.
    /// Useful for pausing animation or switching control modes.
    /// </summary>
    public void SetEnabled(bool isEnabled)
    {
        enabled = isEnabled;
        if (debugLogging)
            Debug.Log($"[JointAnimator] Animation {(isEnabled ? "enabled" : "disabled")}");
    }

    /// <summary>
    /// Reset all joints to neutral position.
    /// </summary>
    public void ResetToNeutral()
    {
        foreach (var joint in jointDictionary.Values)
        {
            var drive = joint.xDrive;
            drive.target = 0.0f;
            joint.xDrive = drive;
        }

        if (debugLogging)
            Debug.Log("[JointAnimator] Reset all joints to neutral (0 radians)");
    }

    /// <summary>
    /// Get the current target position of a specific joint.
    /// Returns null if joint not found.
    /// </summary>
    public float? GetJointTarget(string jointName)
    {
        if (jointDictionary.TryGetValue(jointName, out var joint))
        {
            return joint.xDrive.target;
        }
        return null;
    }

    /// <summary>
    /// Get statistics about animation performance.
    /// </summary>
    public void PrintStatistics()
    {
        Debug.Log("=== Joint Animator Statistics ===");
        Debug.Log($"Total joints: {jointDictionary.Count}");
        Debug.Log($"Frames since last message: {framesSinceLastUpdate}");
        Debug.Log($"Smoothing enabled: {enableSmoothing}");
        Debug.Log($"Message history size: {jointHistory.Count}");

        int messageCount = jointStateSubscriber.GetMessageCount();
        Debug.Log($"Total messages received: {messageCount}");
    }
}
