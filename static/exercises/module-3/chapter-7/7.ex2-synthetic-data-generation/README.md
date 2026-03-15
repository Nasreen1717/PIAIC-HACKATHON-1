# Exercise 7.2: Synthetic Data Generation for Robot Perception

## Overview

Generate synthetic training datasets for robot perception models in Isaac Sim. You'll create diverse, annotated synthetic images and export them in COCO format for training computer vision models. Learn to leverage simulation's deterministic nature to generate large-scale labeled datasets without manual annotation.

**Difficulty**: Intermediate-Advanced
**Duration**: 3-4 hours
**Learning Outcomes**:
- Generate diverse synthetic images using randomization (cameras, lighting, objects)
- Annotate images with bounding boxes, segmentation masks, and keypoints
- Export datasets in COCO format for popular ML frameworks
- Evaluate dataset quality and bias
- Handle sim-to-real gap through domain randomization
- Benchmark model training on synthetic vs. real data

**Prerequisites**:
- Completion of Chapter 7.1-7.3
- Access to Isaac Sim 2023.8+
- Python 3.10+ with numpy, PIL
- Basic understanding of COCO dataset format
- Familiarity with computer vision (bounding boxes, segmentation)

---

## Problem Statement

Your robot needs to detect and grasp objects on a table. You have:
- **Scene**: 4 static robot grasping scenarios
- **Objects**: 10 different object models (cubes, cylinders, spheres)
- **Cameras**: 3 camera viewpoints per scene
- **Goal**: Generate 5,000 training images with annotations

Current challenges:
1. ❌ Manual labeling is too slow (1 hour per 100 images)
2. ❌ Limited diversity in training data (only real-world collected)
3. ⚠️ Domain gap between simulation and real robot
4. ❌ Class imbalance (some objects underrepresented)

Your task is to:
- ✅ Generate synthetic images with automatic annotations
- ✅ Randomize lighting, camera pose, object placement
- ✅ Export in COCO format with 100% annotation coverage
- ✅ Create balanced dataset across object classes
- ✅ Measure and document sim-to-real transfer potential

---

## Step-by-Step Instructions

### Step 1: Setup and Scene Creation (30 min)

1. Create a basic scene in Isaac Sim with:
   - Ground plane
   - Table (0.8m × 0.6m)
   - Mounting points for robot gripper
   - Lighting (1-3 adjustable lights)

2. Load 5-10 different object models (from Isaac Sim assets):
   - Simple geometric shapes
   - Daily objects (cup, bottle, can)
   - Varying sizes and colors

3. **Template code**:
```python
from omni.isaac.core.utils.stage import add_reference_to_stage

# Create table
table = add_reference_to_stage(
    usd_path="omniverse://models/table.usd",
    prim_path="/World/table"
)

# Load object models
objects = []
for i in range(5):
    obj = add_reference_to_stage(
        usd_path=f"omniverse://models/cube_{i}.usd",
        prim_path=f"/World/object_{i}"
    )
    objects.append(obj)
```

### Step 2: Implement Randomization (1 hour)

Randomize these parameters for each image:
1. **Camera pose**: 3-5 viewpoints around the table
2. **Lighting**: Intensity (0.3-1.0), color temperature
3. **Object positions**: Random placement on table
4. **Object orientations**: Random rotations
5. **Distractors**: Add 1-3 extra objects

| Parameter | Range | Impact |
|-----------|-------|--------|
| **Camera X** | ±0.3m | Lateral viewpoint |
| **Camera Y** | ±0.2m | Depth variation |
| **Camera Height** | 0.5-1.0m | View angle |
| **Light Intensity** | 0.3-1.0 | Exposure variation |
| **Light Color Temp** | 3000-6500K | Realistic lighting |
| **Object Position** | ±0.2m in X,Y | Placement diversity |
| **Object Rotation** | 0-360° | Orientation variance |

**Acceptance Criteria**:
- ✅ At least 5 unique camera positions
- ✅ Randomization applies to all parameters
- ✅ Generated images show clear visual variety
- ✅ No parameter is left at default (static)

### Step 3: Automatic Annotation (1 hour)

Capture annotations for each image:
1. **Bounding boxes**: Object location (x, y, width, height)
2. **Segmentation masks**: Per-pixel object labels
3. **Keypoints**: Important points on objects (optional)
4. **Class labels**: Object category (cube, sphere, etc.)

**Annotation strategy**:
```python
# For each rendered image:
annotations = {
    "image_id": frame_index,
    "annotations": [
        {
            "id": annotation_id,
            "image_id": frame_index,
            "category_id": class_id,
            "bbox": [x, y, width, height],
            "area": width * height,
            "iscrowd": 0,
            "segmentation": [polygon_points]  # Optional
        }
    ]
}
```

**Acceptance Criteria**:
- ✅ All objects in frame have bounding boxes
- ✅ Bounding boxes are accurate (IoU > 0.8 with GT)
- ✅ All annotations include class labels
- ✅ Annotation format is valid JSON

### Step 4: COCO Dataset Export (45 min)

Export dataset in COCO format:
```python
coco = {
    "info": {
        "description": "Synthetic robot grasping dataset",
        "version": "1.0",
        "year": 2024
    },
    "images": [
        {
            "id": image_id,
            "file_name": f"img_{image_id:06d}.png",
            "height": 480,
            "width": 640
        }
    ],
    "annotations": [...],  # From step 3
    "categories": [
        {"id": 1, "name": "cube", "supercategory": "object"},
        {"id": 2, "name": "sphere", "supercategory": "object"},
        ...
    ]
}

with open("coco_annotations.json", "w") as f:
    json.dump(coco, f)
```

**Acceptance Criteria**:
- ✅ COCO JSON file is valid (parseable)
- ✅ All referenced images exist
- ✅ All image dimensions correct
- ✅ Annotation counts match actual data
- ✅ Category IDs are sequential and unique

### Step 5: Class Balance Analysis (30 min)

Verify dataset quality:
1. Count annotations per class
2. Identify underrepresented classes
3. Generate additional samples for rare classes

**Analysis output**:
```
Class Distribution:
  cube: 1250 (25.0%) ✅
  sphere: 1100 (22.0%) ⚠️  (below 25%)
  cylinder: 980 (19.6%) ❌ (below 20%)
  bottle: 850 (17.0%) ❌ (below 20%)
  cup: 820 (16.4%) ❌ (below 20%)
```

**Acceptance Criteria**:
- ✅ All classes represented (0 samples = fail)
- ✅ Class distribution ≥ 15% each (balanced)
- ✅ Analysis saved to CSV/JSON

### Step 6: Sim-to-Real Transfer Evaluation (30 min)

Estimate domain gap:
1. Compare synthetic image statistics to real images
2. Measure lighting/color distribution
3. Document potential transfer challenges

**Evaluation metrics**:
- Color distribution (histogram comparison)
- Brightness distribution
- Texture realism (visual inspection)
- Domain randomization coverage

**Acceptance Criteria**:
- ✅ Synthetic images have diverse lighting
- ✅ Object appearances are realistic
- ✅ Transfer potential documented
- ✅ Recommendations for improvement provided

### Step 7: Validation and Benchmarking (1 hour)

1. Train a simple detector on 5,000 synthetic images
2. Test on real world data (if available)
3. Measure performance gap

**Optional benchmark**:
```python
# Train a simple CNN on synthetic data
model = train_yolo_detector(
    coco_file="coco_annotations.json",
    epochs=10,
    batch_size=32
)

# Evaluate on real test set
metrics = evaluate_on_real_data(model, real_test_set)
print(f"Synthetic → Real mAP: {metrics['mAP']:.3f}")
```

---

## Acceptance Criteria Checklist

| Criterion | Met? | Notes |
|-----------|------|-------|
| **Scene Setup** | ☐ | Table, objects, lighting configured |
| **Randomization** | ☐ | ≥5 parameters randomized |
| **Image Count** | ☐ | ≥ 5,000 images generated |
| **Annotations** | ☐ | All objects labeled (100% coverage) |
| **COCO Export** | ☐ | Valid JSON, all images included |
| **Class Balance** | ☐ | All classes ≥15% representation |
| **Sim-to-Real** | ☐ | Transfer potential evaluated |
| **Documentation** | ☐ | Dataset report generated |
| **Tests Pass** | ☐ | pytest achieves > 80% |

---

## Hints (5 Levels)

### Hint 1: Getting Started
Start with a simple scene:
```python
# Load table and 5 objects
scene_setup = {
    "table": load_usd("table.usd"),
    "objects": [load_usd(f"object_{i}.usd") for i in range(5)]
}
```

### Hint 2: Randomization Function
Create a randomization controller:
```python
import random
def randomize_scene():
    # Random camera position
    camera.position = [
        random.uniform(-0.3, 0.3),
        random.uniform(-0.2, 0.2),
        random.uniform(0.5, 1.0)
    ]

    # Random object positions
    for obj in objects:
        obj.position = [
            random.uniform(-0.1, 0.1),
            random.uniform(-0.1, 0.1),
            0.1  # Keep on table
        ]

    # Random lighting
    light.intensity = random.uniform(0.3, 1.0)
```

### Hint 3: Bounding Box Extraction
Get bounding boxes from object positions:
```python
def get_bounding_box(object_prim):
    # Get 3D bounds
    bounds = object_prim.get_local_transform().bounds()
    # Project to 2D camera image
    bbox_2d = project_3d_to_2d(bounds, camera_matrix)
    return {
        "x": int(bbox_2d[0]),
        "y": int(bbox_2d[1]),
        "width": int(bbox_2d[2] - bbox_2d[0]),
        "height": int(bbox_2d[3] - bbox_2d[1])
    }
```

### Hint 4: COCO Format Structure
Essential COCO keys:
```python
coco_dataset = {
    "images": [...],       # Image metadata
    "annotations": [...],  # Per-object annotations
    "categories": [...],   # Class definitions
    "info": {...}          # Dataset info
}
```

### Hint 5: Validation Check
Validate generated dataset:
```python
def validate_coco(coco_dict):
    # Check structure
    assert "images" in coco_dict
    assert "annotations" in coco_dict
    assert "categories" in coco_dict

    # Check consistency
    image_ids = set(img["id"] for img in coco_dict["images"])
    for ann in coco_dict["annotations"]:
        assert ann["image_id"] in image_ids
        assert ann["category_id"] in [cat["id"] for cat in coco_dict["categories"]]

    print("✅ COCO dataset valid")
```

---

## Template Code

```python
#!/usr/bin/env python3
"""Exercise 7.2: Synthetic Data Generation - Template"""

import json
from pathlib import Path
from typing import Dict, List
import random
import numpy as np


class SyntheticDatasetGenerator:
    """Generate synthetic training data in COCO format."""

    def __init__(self, output_dir: str = "./dataset"):
        """Initialize generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.images = []
        self.annotations = []
        self.categories = []

    def setup_scene(self) -> bool:
        """TODO: Setup Isaac Sim scene with table and objects."""
        pass

    def randomize_scene(self):
        """TODO: Randomize camera, lighting, and object positions."""
        pass

    def render_and_capture(self, frame_id: int) -> dict:
        """TODO: Render frame and get annotations."""
        pass

    def get_bounding_boxes(self) -> List[dict]:
        """TODO: Extract bounding boxes for all visible objects."""
        pass

    def generate_dataset(self, num_images: int = 5000) -> bool:
        """TODO: Generate full synthetic dataset."""
        pass

    def analyze_class_balance(self) -> Dict[str, float]:
        """TODO: Analyze class distribution in dataset."""
        pass

    def export_coco(self, output_file: str = "coco_annotations.json") -> bool:
        """TODO: Export dataset in COCO format."""
        pass

    def validate_dataset(self) -> bool:
        """TODO: Validate COCO format and consistency."""
        pass


def main():
    """Main execution."""
    generator = SyntheticDatasetGenerator()

    # TODO: Implement workflow
    # 1. Setup scene
    # 2. Generate 5000 images
    # 3. Analyze class balance
    # 4. Export COCO
    # 5. Validate

    print("TODO: Complete exercise implementation")


if __name__ == '__main__':
    main()
```

---

## Solution Code (Summary)

See `solution.py` for complete implementation including:
- Scene setup with table and multiple objects
- Randomization of camera, lighting, and objects
- Annotation capture (bounding boxes, segmentation)
- COCO format generation
- Class balance analysis
- Dataset validation and reporting

---

## Test Suite

Run with: `pytest test_solution.py -v`

**Test Coverage** (16+ tests):
- ✅ Scene loads and initializes
- ✅ Randomization produces diverse output
- ✅ Annotations are accurate
- ✅ COCO format is valid JSON
- ✅ All images are referenced
- ✅ All annotations have valid categories
- ✅ Class distribution is balanced
- ✅ Bounding boxes are within image bounds
- ✅ Dataset size matches generation config
- ✅ Export succeeds without errors
- ✅ Multiple runs produce different data
- ✅ Segmentation masks are valid

---

## Common Mistakes

| Mistake | How to Avoid |
|---------|-------------|
| **Duplicate image IDs** | Use sequential counter for image_id |
| **Missing annotations** | Check `all(img_id in ann_ids for img_id in image_ids)` |
| **Invalid COCO JSON** | Use `json.loads(json.dumps(data))` to validate |
| **Out-of-bounds boxes** | Clip bbox to image dimensions |
| **Empty categories** | Generate at least 1 annotation per category |
| **Non-deterministic results** | Seed random for reproducibility in tests |
| **Slow generation** | Use vectorized operations, batch processing |
| **No domain randomization** | Randomize ALL scene parameters, not just positions |

---

## Extension Challenges

After completing the basic exercise:

1. **Multi-scene variation**: Generate data across 3-5 different table configurations, backgrounds, and lighting setups.

2. **Occlusion handling**: Randomly place objects to create occlusion, then verify bounding boxes remain accurate.

3. **Domain randomization++**: Add material variation (glossy/matte), depth-of-field blur, motion blur, and noise.

4. **Semantic segmentation**: Export per-pixel class labels as segmentation masks in COCO format.

5. **Real-world validation**: Compare synthetic dataset statistics with real images (color histogram, contrast, etc.).

6. **Active learning**: Generate hardest examples (lowest model confidence) and add to dataset iteratively.

---

## Grading Rubric

| Aspect | Poor (0-2) | Fair (3-5) | Good (6-8) | Excellent (9-10) |
|--------|-----------|-----------|-----------|-----------------|
| **Dataset Generation** | Minimal images, no randomization | 1000+ images, basic randomization | 5000+ images, good variety | 5000+ diverse, domain randomization |
| **Annotations** | < 80% coverage, errors | ~90% coverage | > 95% coverage | 100% accurate, validated |
| **COCO Format** | Invalid JSON | Valid but incomplete | Valid, all fields | Valid, well-structured, documented |
| **Class Balance** | Severe imbalance | Some imbalance | Good balance (>20%) | Excellent balance (>25%) |
| **Code Quality** | Incomplete, errors | Working but messy | Clean, well-documented | Excellent structure, extensible |
| **Evaluation** | No analysis | Basic stats | Good analysis | Thorough, with recommendations |

**Total**: _____ / 10 points

---

## References

- COCO Dataset: https://cocodataset.org/
- Isaac Sim Documentation: https://docs.omniverse.nvidia.com/isaacsim/
- Domain Randomization: Tobin et al., "Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World" (2017)
- Synthetic Data for Vision: https://github.com/NVIDIA/Omniverse-Samples

---

*Exercise 7.2: Synthetic Data Generation* | Module 3 - Advanced Robotics
