using UnityEngine;

/// <summary>
/// Orbit Camera Controller for Robot Visualization
///
/// This script implements a professional camera controller that:
/// - Orbits around a target (robot)
/// - Supports mouse drag for rotation
/// - Supports scroll wheel for zoom
/// - Smooth damping for natural feel
/// - Multiple view modes (orbit, follow, first-person)
///
/// Controls:
/// - Right-click + drag: Rotate camera
/// - Scroll wheel: Zoom in/out
/// - Mouse wheel click: Frame all
/// - Space: Toggle view mode
///
/// Author: Module 2 - Digital Twin
/// Date: 2026-01-22
/// License: MIT
/// </summary>
public class OrbitCamera : MonoBehaviour
{
    [Header("Target Settings")]
    [SerializeField] private Transform target;          // Robot to orbit around
    [SerializeField] private Vector3 targetOffset = Vector3.zero;  // Offset from pivot

    [Header("Orbit Settings")]
    [SerializeField] private float distance = 5.0f;
    [SerializeField] private float minDistance = 0.5f;
    [SerializeField] private float maxDistance = 20.0f;

    [Header("Rotation Settings")]
    [SerializeField] private float rotationSpeed = 2.0f;
    [SerializeField] private float rotationDamping = 0.9f;  // Smoothing factor
    [SerializeField] private float minPitch = -89.0f;
    [SerializeField] private float maxPitch = 89.0f;

    [Header("Zoom Settings")]
    [SerializeField] private float scrollSpeed = 1.0f;
    [SerializeField] private float zoomDamping = 0.85f;

    [Header("View Modes")]
    [SerializeField] private bool enableFollowMode = true;
    [SerializeField] private float followSmoothing = 0.1f;

    // Internal rotation state
    private float rotationX = 0.0f;  // Pitch (up/down)
    private float rotationY = 0.0f;  // Yaw (left/right)
    private float targetRotationX = 0.0f;
    private float targetRotationY = 0.0f;

    // Zoom state
    private float targetDistance;
    private float velocityDistance = 0.0f;

    // View modes
    private enum ViewMode { Orbit, Follow, FirstPerson }
    private ViewMode currentViewMode = ViewMode.Orbit;

    // Debug
    [SerializeField] private bool debugLogging = false;

    private void Start()
    {
        if (target == null)
        {
            Debug.LogError("[OrbitCamera] No target assigned! Assign robot GameObject to 'Target' field.");
            enabled = false;
            return;
        }

        targetDistance = distance;

        if (debugLogging)
            Debug.Log("[OrbitCamera] Initialized with target: " + target.name);
    }

    private void LateUpdate()
    {
        HandleInput();
        UpdateCameraPosition();
    }

    private void HandleInput()
    {
        // Right-click to rotate
        if (Input.GetMouseButton(1))
        {
            targetRotationX += Input.GetAxis("Mouse X") * rotationSpeed;
            targetRotationY -= Input.GetAxis("Mouse Y") * rotationSpeed;
            targetRotationY = Mathf.Clamp(targetRotationY, minPitch, maxPitch);
        }

        // Scroll wheel to zoom
        float scrollInput = Input.GetAxis("Mouse ScrollWheel");
        if (Mathf.Abs(scrollInput) > 0.01f)
        {
            targetDistance -= scrollInput * scrollSpeed;
            targetDistance = Mathf.Clamp(targetDistance, minDistance, maxDistance);
        }

        // Space to cycle view modes
        if (Input.GetKeyDown(KeyCode.Space))
        {
            CycleViewMode();
        }

        // F to frame all
        if (Input.GetKeyDown(KeyCode.F))
        {
            FrameAll();
        }
    }

    private void UpdateCameraPosition()
    {
        // Apply damping to rotation
        rotationX = Mathf.Lerp(rotationX, targetRotationX, rotationDamping);
        rotationY = Mathf.Lerp(rotationY, targetRotationY, rotationDamping);

        // Apply damping to distance (zoom)
        distance = Mathf.SmoothDamp(distance, targetDistance, ref velocityDistance, 0.1f);

        // Calculate camera position
        switch (currentViewMode)
        {
            case ViewMode.Orbit:
                UpdateOrbitView();
                break;
            case ViewMode.Follow:
                UpdateFollowView();
                break;
            case ViewMode.FirstPerson:
                UpdateFirstPersonView();
                break;
        }
    }

    private void UpdateOrbitView()
    {
        Quaternion rotation = Quaternion.Euler(rotationY, rotationX, 0);
        Vector3 offset = rotation * Vector3.back * distance;

        transform.position = target.position + targetOffset + offset;
        transform.LookAt(target.position + targetOffset + Vector3.up * 0.5f);

        if (debugLogging && Time.frameCount % 60 == 0)
            Debug.Log($"[OrbitCamera] Orbit - Distance: {distance:F1}, Rotation: ({rotationX:F1}, {rotationY:F1})");
    }

    private void UpdateFollowView()
    {
        // Follow from behind but smoothly
        Vector3 targetPos = target.position - target.forward * distance + Vector3.up * (distance * 0.3f);
        transform.position = Vector3.Lerp(transform.position, targetPos, followSmoothing);
        transform.LookAt(target.position + Vector3.up * 1.0f);
    }

    private void UpdateFirstPersonView()
    {
        // First-person from robot's perspective
        Transform head = target.Find("head");  // Assumes robot has "head" link
        if (head != null)
        {
            transform.position = head.position + head.forward * 0.2f;
            transform.rotation = head.rotation;
        }
        else
        {
            // Fallback: orbit mode if no head found
            UpdateOrbitView();
        }
    }

    private void CycleViewMode()
    {
        currentViewMode = (ViewMode)(((int)currentViewMode + 1) % 3);
        Debug.Log($"[OrbitCamera] View mode changed to: {currentViewMode}");
    }

    private void FrameAll()
    {
        // Frame the entire robot in view
        var renderer = target.GetComponentInChildren<Renderer>();
        if (renderer != null)
        {
            Bounds bounds = renderer.bounds;
            float cameraDistance = bounds.extents.magnitude / Mathf.Tan(Camera.main.fieldOfView * 0.5f * Mathf.Deg2Rad);
            targetDistance = cameraDistance * 1.5f;
            targetDistance = Mathf.Clamp(targetDistance, minDistance, maxDistance);

            if (debugLogging)
                Debug.Log($"[OrbitCamera] Framed all - Distance: {targetDistance:F1}");
        }
    }

    /// <summary>
    /// Reset camera to default orbit position.
    /// </summary>
    public void ResetToDefault()
    {
        rotationX = 0.0f;
        rotationY = 45.0f;
        targetDistance = 5.0f;
        currentViewMode = ViewMode.Orbit;
        Debug.Log("[OrbitCamera] Reset to default position");
    }

    /// <summary>
    /// Set camera to look at a specific link.
    /// </summary>
    public void LookAtLink(Transform linkTransform)
    {
        if (linkTransform == null) return;

        Vector3 directionToLink = (linkTransform.position - target.position).normalized;
        rotationX = Mathf.Atan2(directionToLink.x, directionToLink.z) * Mathf.Rad2Deg;
        rotationY = Mathf.Asin(directionToLink.y) * Mathf.Rad2Deg;
        targetRotationX = rotationX;
        targetRotationY = rotationY;
    }

    /// <summary>
    /// Get current view mode.
    /// </summary>
    public string GetViewModeName()
    {
        return currentViewMode.ToString();
    }
}
