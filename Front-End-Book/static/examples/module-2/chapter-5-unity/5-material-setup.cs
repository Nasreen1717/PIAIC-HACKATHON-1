using UnityEngine;

/// <summary>
/// PBR Material Setup Utility for Robotics
///
/// This script creates and applies physically-based rendering (PBR) materials
/// to robot links. It provides:
/// - Programmatic material creation
/// - Preset materials (metallic, plastic, matte)
/// - Easy assignment to multiple GameObjects
/// - Real-time material preview
///
/// Physically-Based Rendering (PBR) uses:
/// - Albedo (base color): What color is the surface?
/// - Metallic: Is it metal (1) or non-metal (0)?
/// - Roughness: Is it shiny (0) or matte (1)?
/// - Normal maps: Fine surface detail (optional)
///
/// Usage:
/// 1. Attach to empty GameObject or use via scripts
/// 2. Call CreateMaterial() to create custom PBR material
/// 3. Assign to robot links via SetMaterialToGameObject()
/// 4. Adjust parameters in Inspector or via code
///
/// Author: Module 2 - Digital Twin
/// Date: 2026-01-22
/// License: MIT
/// </summary>
public class MaterialSetup : MonoBehaviour
{
    [System.Serializable]
    public struct PBRMaterial
    {
        public string name;
        public Color albedo;
        public float metallic;
        public float roughness;
        public Texture2D normalMap;
    }

    [Header("Material Presets")]
    [SerializeField] private Material uiMetallicPreset;
    [SerializeField] private Material uiPlasticPreset;
    [SerializeField] private Material uiMattePreset;

    /// <summary>
    /// Creates a PBR material with the given parameters.
    /// </summary>
    public Material CreatePBRMaterial(string materialName, Color albedo, float metallic, float roughness)
    {
        Material mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
        mat.name = materialName;

        // Set PBR properties
        mat.SetColor("_BaseColor", albedo);
        mat.SetFloat("_Metallic", metallic);
        mat.SetFloat("_Smoothness", 1.0f - roughness);  // Note: Smoothness = 1 - Roughness

        return mat;
    }

    /// <summary>
    /// Creates a metallic robot material (aluminum-like).
    /// Used for main robot structure.
    /// </summary>
    public Material CreateMetallicMaterial()
    {
        return CreatePBRMaterial(
            "RobotMetal",
            new Color(0.4f, 0.4f, 0.4f),  // Dark gray
            metallic: 0.9f,
            roughness: 0.2f
        );
    }

    /// <summary>
    /// Creates a plastic material (non-metallic, slightly shiny).
    /// Used for joint covers, cables, etc.
    /// </summary>
    public Material CreatePlasticMaterial(Color color = default)
    {
        if (color == default)
            color = new Color(0.1f, 0.1f, 0.1f);  // Black

        return CreatePBRMaterial(
            "RobotPlastic",
            color,
            metallic: 0.0f,
            roughness: 0.4f
        );
    }

    /// <summary>
    /// Creates a matte rubber/paint material (non-metallic, very rough).
    /// Used for grippers, bumpers, etc.
    /// </summary>
    public Material CreateMatteMaterial(Color color = default)
    {
        if (color == default)
            color = new Color(0.8f, 0.8f, 0.8f);  // Light gray

        return CreatePBRMaterial(
            "RobotMatte",
            color,
            metallic: 0.0f,
            roughness: 0.8f
        );
    }

    /// <summary>
    /// Assigns a material to a GameObject's renderer.
    /// </summary>
    public void ApplyMaterialToGameObject(GameObject target, Material material)
    {
        var renderer = target.GetComponent<MeshRenderer>();
        if (renderer != null)
        {
            renderer.material = material;
            Debug.Log($"[MaterialSetup] Applied material '{material.name}' to '{target.name}'");
        }
        else
        {
            Debug.LogWarning($"[MaterialSetup] '{target.name}' has no MeshRenderer component");
        }
    }

    /// <summary>
    /// Applies a material to all children recursively.
    /// Useful for entire robot structures.
    /// </summary>
    public void ApplyMaterialRecursive(GameObject parent, Material material)
    {
        ApplyMaterialToGameObject(parent, material);

        foreach (Transform child in parent.transform)
        {
            ApplyMaterialRecursive(child.gameObject, material);
        }

        Debug.Log($"[MaterialSetup] Applied material to {parent.name} and all children");
    }

    /// <summary>
    /// Create a material with custom parameters (Editor helper).
    /// Call from Inspector buttons or other scripts.
    /// </summary>
    public void CreateAndPreviewMaterial(string name, Color color, float metallic, float roughness)
    {
        Material mat = CreatePBRMaterial(name, color, metallic, roughness);
        Debug.Log($"[MaterialSetup] Created material: {name}");
        Debug.Log($"  Albedo: {color}, Metallic: {metallic}, Roughness: {roughness}");
    }
}

/// <summary>
/// Editor window for easy material creation and assignment.
/// </summary>
#if UNITY_EDITOR
using UnityEditor;

public class MaterialSetupWindow : EditorWindow
{
    private MaterialSetup materialSetup;
    private GameObject targetRobot;
    private int selectedPreset = 0;
    private Color customColor = Color.gray;
    private float customMetallic = 0.5f;
    private float customRoughness = 0.5f;

    [MenuItem("Window/Material Setup")]
    public static void ShowWindow()
    {
        GetWindow<MaterialSetupWindow>("Material Setup");
    }

    private void OnGUI()
    {
        GUILayout.Label("PBR Material Setup for Robots", EditorStyles.boldLabel);

        GUILayout.Space(10);

        // Material Setup reference
        materialSetup = EditorGUILayout.ObjectField("Material Setup Script", materialSetup,
                                                     typeof(MaterialSetup), true) as MaterialSetup;

        // Target robot
        targetRobot = EditorGUILayout.ObjectField("Target Robot", targetRobot,
                                                   typeof(GameObject), true) as GameObject;

        GUILayout.Space(10);

        GUILayout.Label("Preset Materials", EditorStyles.boldLabel);

        // Presets
        string[] presets = { "Metallic", "Plastic", "Matte" };
        selectedPreset = EditorGUILayout.Popup("Select Preset", selectedPreset, presets);

        if (GUILayout.Button("Create & Apply Preset", GUILayout.Height(30)))
        {
            if (materialSetup != null && targetRobot != null)
            {
                ApplyPreset();
            }
            else
            {
                EditorUtility.DisplayDialog("Error", "Set Material Setup Script and Target Robot", "OK");
            }
        }

        GUILayout.Space(10);

        GUILayout.Label("Custom Material", EditorStyles.boldLabel);

        customColor = EditorGUILayout.ColorField("Color", customColor);
        customMetallic = EditorGUILayout.Slider("Metallic", customMetallic, 0.0f, 1.0f);
        customRoughness = EditorGUILayout.Slider("Roughness", customRoughness, 0.0f, 1.0f);

        if (GUILayout.Button("Create & Apply Custom", GUILayout.Height(30)))
        {
            if (materialSetup != null && targetRobot != null)
            {
                Material custom = materialSetup.CreatePBRMaterial(
                    "CustomMaterial",
                    customColor,
                    customMetallic,
                    customRoughness
                );
                materialSetup.ApplyMaterialRecursive(targetRobot, custom);
                EditorUtility.DisplayDialog("Success", "Custom material applied!", "OK");
            }
        }
    }

    private void ApplyPreset()
    {
        Material mat = null;

        switch (selectedPreset)
        {
            case 0:
                mat = materialSetup.CreateMetallicMaterial();
                break;
            case 1:
                mat = materialSetup.CreatePlasticMaterial();
                break;
            case 2:
                mat = materialSetup.CreateMatteMaterial();
                break;
        }

        if (mat != null)
        {
            materialSetup.ApplyMaterialRecursive(targetRobot, mat);
            EditorUtility.DisplayDialog("Success", $"Applied {presets[selectedPreset]} material!", "OK");
        }
    }
}
#endif
