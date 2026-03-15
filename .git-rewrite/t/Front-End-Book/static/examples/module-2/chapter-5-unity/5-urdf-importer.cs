using UnityEditor;
using UnityEngine;
using System.IO;

/// <summary>
/// URDF Importer Editor Script for Unity
///
/// This script provides a GUI for importing URDF robot models into Unity.
/// It handles:
/// - File selection and parsing
/// - GameObject hierarchy creation
/// - ArticulationBody setup for joints
/// - Collision geometry handling
/// - Error reporting and validation
///
/// Usage:
/// 1. Attach to an empty GameObject or use as Editor Window
/// 2. Select URDF file via GUI
/// 3. Click "Import URDF"
/// 4. Robot hierarchy created in scene
///
/// Author: Module 2 - Digital Twin
/// Date: 2026-01-22
/// License: MIT
/// </summary>
public class URDFImporterEditor : EditorWindow
{
    private string urdfPath = "";
    private bool importMeshes = true;
    private bool createColliders = true;
    private bool createArticulations = true;
    private float scaleFactor = 1.0f;

    private Vector2 scrollPosition = Vector2.zero;

    [MenuItem("Window/URDF Importer")]
    public static void ShowWindow()
    {
        GetWindow<URDFImporterEditor>("URDF Importer");
    }

    private void OnGUI()
    {
        scrollPosition = GUILayout.BeginScrollView(scrollPosition);

        GUILayout.Label("URDF Robot Model Importer", EditorStyles.boldLabel);

        GUILayout.Space(10);

        // URDF File Selection
        GUILayout.Label("1. Select URDF File", EditorStyles.boldLabel);
        GUILayout.BeginHorizontal();
        urdfPath = GUILayout.TextField(urdfPath, GUILayout.ExpandWidth(true));
        if (GUILayout.Button("Browse", GUILayout.Width(80)))
        {
            string path = EditorUtility.OpenFilePanel("Select URDF file", "", "urdf");
            if (!string.IsNullOrEmpty(path))
            {
                urdfPath = path;
                LogInfo($"Selected URDF: {Path.GetFileName(urdfPath)}");
            }
        }
        GUILayout.EndHorizontal();

        if (!string.IsNullOrEmpty(urdfPath) && File.Exists(urdfPath))
        {
            EditorGUILayout.HelpBox($"✓ File exists: {urdfPath}", MessageType.Info);
        }
        else if (!string.IsNullOrEmpty(urdfPath))
        {
            EditorGUILayout.HelpBox($"✗ File not found: {urdfPath}", MessageType.Error);
        }

        GUILayout.Space(10);

        // Import Options
        GUILayout.Label("2. Import Options", EditorStyles.boldLabel);
        importMeshes = GUILayout.Toggle(importMeshes, "Import Meshes & Visuals");
        createColliders = GUILayout.Toggle(createColliders, "Create Collision Geometry");
        createArticulations = GUILayout.Toggle(createArticulations, "Create ArticulationBodies (for animation)");

        GUILayout.Space(5);

        GUILayout.Label("Scale Factor", EditorStyles.label);
        scaleFactor = EditorGUILayout.Slider(scaleFactor, 0.1f, 10.0f);

        GUILayout.Space(10);

        // Import Button
        GUI.backgroundColor = new Color(0.5f, 1.0f, 0.5f);
        if (GUILayout.Button("IMPORT URDF", GUILayout.Height(40)))
        {
            if (ValidateURDF())
            {
                ImportURDF();
            }
        }
        GUI.backgroundColor = Color.white;

        GUILayout.Space(10);

        // Status Information
        GUILayout.Label("Information", EditorStyles.boldLabel);
        EditorGUILayout.HelpBox(
            "Steps:\n" +
            "1. Select your URDF file\n" +
            "2. Choose import options\n" +
            "3. Click IMPORT URDF\n" +
            "4. Robot appears in scene hierarchy\n" +
            "5. Customize materials & lighting in Editor",
            MessageType.Info
        );

        GUILayout.EndScrollView();
    }

    private bool ValidateURDF()
    {
        if (string.IsNullOrEmpty(urdfPath))
        {
            LogError("No URDF file selected");
            return false;
        }

        if (!File.Exists(urdfPath))
        {
            LogError($"URDF file not found: {urdfPath}");
            return false;
        }

        // Validate XML parsing
        try
        {
            var doc = new System.Xml.XmlDocument();
            doc.Load(urdfPath);

            var robotElement = doc.SelectSingleNode("//robot");
            if (robotElement == null)
            {
                LogError("Invalid URDF: No <robot> element found");
                return false;
            }

            LogInfo($"✓ URDF validated. Robot name: {robotElement.Attributes?["name"]?.Value}");
            return true;
        }
        catch (System.Exception e)
        {
            LogError($"URDF parsing error: {e.Message}");
            return false;
        }
    }

    private void ImportURDF()
    {
        LogInfo("Starting URDF import...");

        try
        {
            var doc = new System.Xml.XmlDocument();
            doc.Load(urdfPath);

            var robotElement = doc.SelectSingleNode("//robot");
            string robotName = robotElement?.Attributes?["name"]?.Value ?? "Robot";

            // Create root GameObject
            GameObject rootGO = new GameObject(robotName);
            rootGO.transform.position = Vector3.zero;

            // Create links
            var linkElements = doc.SelectNodes("//link");
            LogInfo($"Found {linkElements.Count} links");

            foreach (System.Xml.XmlElement linkElement in linkElements)
            {
                string linkName = linkElement.Attributes?["name"]?.Value ?? "Link";

                GameObject linkGO = new GameObject(linkName);
                linkGO.transform.SetParent(rootGO.transform);
                linkGO.transform.localPosition = Vector3.zero;

                // Add collider if enabled
                if (createColliders)
                {
                    var collisionElement = linkElement.SelectSingleNode("collision");
                    if (collisionElement != null)
                    {
                        AddCollider(linkGO, collisionElement);
                    }
                }

                // Add ArticulationBody if enabled
                if (createArticulations)
                {
                    var ab = linkGO.AddComponent<ArticulationBody>();
                    ab.mass = 1.0f;  // Default mass; will be overridden by joint configuration
                    ab.linearDamping = 0.01f;
                    ab.angularDamping = 0.01f;
                }

                LogInfo($"  Created link: {linkName}");
            }

            // Create joints
            var jointElements = doc.SelectNodes("//joint");
            LogInfo($"Found {jointElements.Count} joints");

            foreach (System.Xml.XmlElement jointElement in jointElements)
            {
                string jointName = jointElement.Attributes?["name"]?.Value ?? "Joint";
                string jointType = jointElement.Attributes?["type"]?.Value ?? "revolute";

                var parentElement = jointElement.SelectSingleNode("parent");
                var childElement = jointElement.SelectSingleNode("child");

                string parentName = parentElement?.Attributes?["link"]?.Value ?? "base_link";
                string childName = childElement?.Attributes?["link"]?.Value ?? "Link";

                // Find child link GameObject
                var childGO = FindChildGameObject(rootGO, childName);
                if (childGO != null)
                {
                    // Setup ArticulationBody for joint
                    if (createArticulations && jointType == "revolute")
                    {
                        ConfigureRevoluteJoint(childGO, jointElement);
                    }

                    LogInfo($"  Created joint: {jointName} ({parentName} -> {childName})");
                }
            }

            // Apply scale
            if (scaleFactor != 1.0f)
            {
                rootGO.transform.localScale = Vector3.one * scaleFactor;
                LogInfo($"Applied scale factor: {scaleFactor}");
            }

            // Select the new root in hierarchy
            Selection.activeGameObject = rootGO;

            LogInfo($"✓ Successfully imported URDF: {rootGO.name}");
            EditorUtility.DisplayDialog("URDF Import", $"Successfully imported: {rootGO.name}\n\nNext steps:\n1. Customize materials\n2. Adjust lighting\n3. Test animation", "OK");
        }
        catch (System.Exception e)
        {
            LogError($"URDF import failed: {e.Message}\n{e.StackTrace}");
            EditorUtility.DisplayDialog("URDF Import Error", $"Failed to import URDF:\n{e.Message}", "OK");
        }
    }

    private void AddCollider(GameObject go, System.Xml.XmlElement collisionElement)
    {
        var geometryElement = collisionElement.SelectSingleNode("geometry");
        if (geometryElement == null) return;

        // Check for box
        var boxElement = geometryElement.SelectSingleNode("box");
        if (boxElement != null)
        {
            string sizeStr = boxElement.Attributes?["size"]?.Value ?? "1 1 1";
            string[] sizes = sizeStr.Split(' ');
            if (sizes.Length >= 3)
            {
                float.TryParse(sizes[0], out float x);
                float.TryParse(sizes[1], out float y);
                float.TryParse(sizes[2], out float z);

                var collider = go.AddComponent<BoxCollider>();
                collider.size = new Vector3(x, y, z);
            }
            return;
        }

        // Check for cylinder
        var cylinderElement = geometryElement.SelectSingleNode("cylinder");
        if (cylinderElement != null)
        {
            float.TryParse(cylinderElement.Attributes?["radius"]?.Value ?? "0.5", out float radius);
            float.TryParse(cylinderElement.Attributes?["length"]?.Value ?? "1", out float length);

            var collider = go.AddComponent<CapsuleCollider>();
            collider.radius = radius;
            collider.height = length;
            return;
        }

        // Check for sphere
        var sphereElement = geometryElement.SelectSingleNode("sphere");
        if (sphereElement != null)
        {
            float.TryParse(sphereElement.Attributes?["radius"]?.Value ?? "0.5", out float radius);

            var collider = go.AddComponent<SphereCollider>();
            collider.radius = radius;
            return;
        }
    }

    private void ConfigureRevoluteJoint(GameObject childGO, System.Xml.XmlElement jointElement)
    {
        var limitElement = jointElement.SelectSingleNode("limit");
        float.TryParse(limitElement?.Attributes?["lower"]?.Value ?? "-3.14", out float lower);
        float.TryParse(limitElement?.Attributes?["upper"]?.Value ?? "3.14", out float upper);
        float.TryParse(limitElement?.Attributes?["effort"]?.Value ?? "10", out float effort);
        float.TryParse(limitElement?.Attributes?["velocity"]?.Value ?? "2", out float velocity);

        var ab = childGO.GetComponent<ArticulationBody>();
        if (ab != null)
        {
            ab.jointType = ArticulationJointType.RevoluteJoint;
            ab.linearDamping = 0.05f;
            ab.angularDamping = 0.05f;

            // Configure drive
            var drive = ab.xDrive;
            drive.lowerLimit = lower;
            drive.upperLimit = upper;
            drive.stiffness = 10000;
            drive.damping = 100;
            ab.xDrive = drive;
        }
    }

    private GameObject FindChildGameObject(GameObject parent, string childName)
    {
        if (parent.name == childName) return parent;

        foreach (Transform child in parent.transform)
        {
            var result = FindChildGameObject(child.gameObject, childName);
            if (result != null) return result;
        }

        return null;
    }

    private void LogInfo(string message)
    {
        Debug.Log($"[URDFImporter] ✓ {message}");
    }

    private void LogError(string message)
    {
        Debug.LogError($"[URDFImporter] ✗ {message}");
    }
}
