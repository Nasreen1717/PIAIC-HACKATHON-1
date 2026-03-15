#!/usr/bin/env python3
"""
Exercise 7.2: Synthetic Data Generation - Solution

Complete implementation for generating synthetic datasets in COCO format.
Includes scene setup, randomization, annotation, export, and validation.

Author: Isaac Sim Educational Module
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
import random
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """2D bounding box in COCO format."""
    x: float
    y: float
    width: float
    height: float

    def to_coco(self) -> List[float]:
        """Convert to COCO format [x, y, w, h]."""
        return [self.x, self.y, self.width, self.height]

    def area(self) -> float:
        """Calculate area."""
        return self.width * self.height

    def clip_to_image(self, img_width: int, img_height: int) -> 'BoundingBox':
        """Clip bounding box to image bounds."""
        x = max(0, min(self.x, img_width))
        y = max(0, min(self.y, img_height))
        width = max(0, min(self.width, img_width - x))
        height = max(0, min(self.height, img_height - y))
        return BoundingBox(x, y, width, height)


@dataclass
class SceneRandomization:
    """Randomization parameters for scene."""
    camera_x: float = 0.0
    camera_y: float = 0.0
    camera_z: float = 0.75
    camera_rotation: float = 0.0
    light_intensity: float = 0.7
    light_color_temp: int = 5500
    num_objects: int = 3
    object_positions: List[Tuple[float, float]] = field(default_factory=list)
    object_rotations: List[float] = field(default_factory=list)


@dataclass
class ObjectAnnotation:
    """Annotation for a single object."""
    annotation_id: int
    image_id: int
    category_id: int
    category_name: str
    bbox: BoundingBox
    area: float
    is_crowd: int = 0
    segmentation: List = field(default_factory=list)

    def to_coco(self) -> Dict:
        """Convert to COCO annotation format."""
        return {
            "id": self.annotation_id,
            "image_id": self.image_id,
            "category_id": self.category_id,
            "bbox": self.bbox.to_coco(),
            "area": self.area,
            "iscrowd": self.is_crowd,
            "segmentation": self.segmentation
        }


@dataclass
class ImageMetadata:
    """Metadata for a single training image."""
    image_id: int
    file_name: str
    height: int = 480
    width: int = 640
    annotations: List[ObjectAnnotation] = field(default_factory=list)

    def to_coco(self) -> Dict:
        """Convert to COCO image format."""
        return {
            "id": self.image_id,
            "file_name": self.file_name,
            "height": self.height,
            "width": self.width
        }


@dataclass
class CategoryDefinition:
    """COCO category definition."""
    id: int
    name: str
    supercategory: str = "object"

    def to_coco(self) -> Dict:
        """Convert to COCO category format."""
        return {
            "id": self.id,
            "name": self.name,
            "supercategory": self.supercategory
        }


class SyntheticDatasetGenerator:
    """Generate synthetic datasets for robot perception in COCO format."""

    # Predefined object types
    OBJECT_TYPES = {
        1: ("cube", "geometric"),
        2: ("sphere", "geometric"),
        3: ("cylinder", "geometric"),
        4: ("box", "container"),
        5: ("bottle", "container"),
        6: ("cup", "container"),
        7: ("can", "container"),
        8: ("cone", "geometric"),
        9: ("torus", "geometric"),
        10: ("teapot", "organic"),
    }

    def __init__(self, output_dir: str = "./dataset"):
        """
        Initialize the dataset generator.

        Args:
            output_dir: Directory for output images and annotations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Dataset components
        self.images: List[ImageMetadata] = []
        self.annotations: List[ObjectAnnotation] = []
        self.categories: List[CategoryDefinition] = []

        # Scene configuration
        self.image_width = 640
        self.image_height = 480
        self.annotation_id_counter = 0
        self.table_bounds = {
            "x_min": -0.4, "x_max": 0.4,
            "y_min": -0.3, "y_max": 0.3,
            "z": 0.1
        }

        # Initialize categories
        self._init_categories()

        logger.info(f"📊 Dataset generator initialized")

    def _init_categories(self) -> None:
        """Initialize category definitions from OBJECT_TYPES."""
        for cat_id, (name, supercategory) in self.OBJECT_TYPES.items():
            self.categories.append(
                CategoryDefinition(id=cat_id, name=name, supercategory=supercategory)
            )
        logger.info(f"✅ Initialized {len(self.categories)} categories")

    def setup_scene(self) -> bool:
        """
        Setup scene (simulation setup).

        In real implementation, would use Isaac Sim APIs.
        For testing, we simulate a virtual scene.

        Returns:
            True if successful
        """
        logger.info("🎬 Setting up scene...")
        # In real implementation:
        # - Create ground plane
        # - Create table
        # - Setup lighting
        # - Load object models
        logger.info("✅ Scene setup complete")
        return True

    def randomize_scene(self) -> SceneRandomization:
        """
        Randomize scene parameters for this frame.

        Returns:
            SceneRandomization with randomized parameters
        """
        # Random camera position
        camera_x = random.uniform(-0.3, 0.3)
        camera_y = random.uniform(-0.2, 0.2)
        camera_z = random.uniform(0.5, 1.0)
        camera_rotation = random.uniform(0, 360)

        # Random lighting
        light_intensity = random.uniform(0.3, 1.0)
        light_color_temp = random.randint(3000, 6500)

        # Random objects on table
        num_objects = random.randint(1, 5)
        object_positions = []
        object_rotations = []

        for _ in range(num_objects):
            x = random.uniform(
                self.table_bounds["x_min"],
                self.table_bounds["x_max"]
            )
            y = random.uniform(
                self.table_bounds["y_min"],
                self.table_bounds["y_max"]
            )
            object_positions.append((x, y))
            object_rotations.append(random.uniform(0, 360))

        return SceneRandomization(
            camera_x=camera_x,
            camera_y=camera_y,
            camera_z=camera_z,
            camera_rotation=camera_rotation,
            light_intensity=light_intensity,
            light_color_temp=light_color_temp,
            num_objects=num_objects,
            object_positions=object_positions,
            object_rotations=object_rotations
        )

    def get_visible_objects(
        self,
        randomization: SceneRandomization
    ) -> List[Tuple[int, int, Tuple[float, float]]]:
        """
        Get list of visible objects in current frame.

        Args:
            randomization: Scene randomization parameters

        Returns:
            List of (object_type_id, instance_id, position) tuples
        """
        visible = []
        for i, pos in enumerate(randomization.object_positions):
            # Randomly select object type
            obj_type_id = random.randint(1, len(self.OBJECT_TYPES))
            # Add to visible list
            visible.append((obj_type_id, i, pos))
        return visible

    def get_bounding_boxes(
        self,
        visible_objects: List[Tuple[int, int, Tuple[float, float]]],
        randomization: SceneRandomization
    ) -> List[ObjectAnnotation]:
        """
        Extract 2D bounding boxes from object positions.

        Args:
            visible_objects: List of visible objects
            randomization: Scene randomization parameters

        Returns:
            List of ObjectAnnotation with bounding boxes
        """
        annotations = []

        for obj_type_id, instance_id, (obj_x, obj_y) in visible_objects:
            # Project 3D position to 2D camera image
            # Simple projection: scale world coords to image
            img_x = (obj_x + 0.4) / 0.8 * self.image_width  # Normalize to image
            img_y = (obj_y + 0.3) / 0.6 * self.image_height

            # Simulate varying object size (30-150 pixels)
            size = random.randint(30, 150)
            width = size
            height = size

            # Create bounding box
            bbox = BoundingBox(
                x=img_x - width / 2,
                y=img_y - height / 2,
                width=width,
                height=height
            )

            # Clip to image bounds
            bbox = bbox.clip_to_image(self.image_width, self.image_height)

            # Only add if bbox is visible
            if bbox.width > 5 and bbox.height > 5:
                annotation = ObjectAnnotation(
                    annotation_id=self.annotation_id_counter,
                    image_id=0,  # Will be set later
                    category_id=obj_type_id,
                    category_name=self.OBJECT_TYPES[obj_type_id][0],
                    bbox=bbox,
                    area=bbox.area()
                )
                annotations.append(annotation)
                self.annotation_id_counter += 1

        return annotations

    def render_frame(self, frame_id: int) -> Tuple[bool, str]:
        """
        Render a frame and save to disk.

        In real implementation, would render from Isaac Sim.
        For testing, we simulate saving.

        Args:
            frame_id: Frame number for naming

        Returns:
            (success, filename)
        """
        # In real implementation:
        # - Render scene using camera
        # - Save to PNG file
        filename = f"image_{frame_id:06d}.png"
        image_path = self.output_dir / filename

        # For testing, just create empty file
        # In real implementation, would be actual image data
        image_path.touch()

        return True, filename

    def generate_frame_annotations(
        self,
        frame_id: int,
        filename: str
    ) -> ImageMetadata:
        """
        Generate all annotations for a single frame.

        Args:
            frame_id: Frame number
            filename: Output image filename

        Returns:
            ImageMetadata with all annotations
        """
        # Randomize scene
        randomization = self.randomize_scene()

        # Get visible objects
        visible_objects = self.get_visible_objects(randomization)

        # Get bounding boxes
        annotations = self.get_bounding_boxes(visible_objects, randomization)

        # Update image IDs
        for ann in annotations:
            ann.image_id = frame_id

        # Create image metadata
        image = ImageMetadata(
            image_id=frame_id,
            file_name=filename,
            height=self.image_height,
            width=self.image_width,
            annotations=annotations
        )

        return image

    def generate_dataset(self, num_images: int = 5000) -> bool:
        """
        Generate full synthetic dataset.

        Args:
            num_images: Number of images to generate

        Returns:
            True if successful
        """
        logger.info(f"🎥 Generating {num_images} synthetic images...")

        if not self.setup_scene():
            logger.error("❌ Scene setup failed")
            return False

        # Generate images
        for frame_id in range(num_images):
            # Render frame
            success, filename = self.render_frame(frame_id)
            if not success:
                logger.warning(f"⚠️  Failed to render frame {frame_id}")
                continue

            # Generate annotations
            image_metadata = self.generate_frame_annotations(frame_id, filename)

            # Add to dataset
            self.images.append(image_metadata)
            self.annotations.extend(image_metadata.annotations)

            # Progress logging
            if (frame_id + 1) % 500 == 0:
                logger.info(f"  ✅ Generated {frame_id + 1}/{num_images} images")

        logger.info(f"✅ Generated {len(self.images)} images with {len(self.annotations)} annotations")
        return True

    def analyze_class_distribution(self) -> Dict[str, float]:
        """
        Analyze distribution of object classes.

        Returns:
            Dict mapping category_name -> percentage
        """
        logger.info("📊 Analyzing class distribution...")

        if not self.annotations:
            logger.warning("⚠️  No annotations to analyze")
            return {}

        # Count annotations per category
        class_counts = defaultdict(int)
        for ann in self.annotations:
            class_counts[ann.category_name] += 1

        # Calculate percentages
        total_annotations = len(self.annotations)
        distribution = {}

        for cat in self.categories:
            count = class_counts[cat.name]
            percentage = (count / total_annotations * 100) if total_annotations > 0 else 0
            distribution[cat.name] = percentage

            status = "✅" if percentage >= 15 else "⚠️ "
            logger.info(f"  {status} {cat.name:12s}: {count:5d} ({percentage:5.1f}%)")

        return distribution

    def balance_dataset(self, min_percentage: float = 0.15) -> bool:
        """
        Ensure balanced class distribution.

        For testing purposes, we just log what would be done.

        Args:
            min_percentage: Minimum class representation (0-1)

        Returns:
            True if successful
        """
        logger.info(f"⚖️  Balancing dataset (min {min_percentage*100:.0f}% per class)...")

        distribution = self.analyze_class_distribution()

        # Check for imbalanced classes
        imbalanced = [
            name for name, pct in distribution.items()
            if pct < min_percentage * 100
        ]

        if imbalanced:
            logger.warning(f"⚠️  Imbalanced classes: {imbalanced}")
            # In real implementation, would generate additional images
            return False

        logger.info("✅ Dataset is balanced")
        return True

    def export_coco(self, output_file: str = "coco_annotations.json") -> bool:
        """
        Export dataset in COCO format.

        Args:
            output_file: Output JSON filename

        Returns:
            True if successful
        """
        logger.info(f"💾 Exporting COCO annotations to {output_file}...")

        # Build COCO structure
        coco_dataset = {
            "info": {
                "description": "Synthetic robot grasping dataset",
                "version": "1.0",
                "year": datetime.now().year,
                "date_created": datetime.now().isoformat()
            },
            "images": [img.to_coco() for img in self.images],
            "annotations": [ann.to_coco() for ann in self.annotations],
            "categories": [cat.to_coco() for cat in self.categories]
        }

        # Write to JSON file
        try:
            output_path = self.output_dir / output_file
            with open(output_path, 'w') as f:
                json.dump(coco_dataset, f, indent=2)
            logger.info(f"✅ Exported to {output_path.absolute()}")
            return True
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return False

    def validate_coco(self, coco_dict: Dict) -> Tuple[bool, List[str]]:
        """
        Validate COCO dataset structure and consistency.

        Args:
            coco_dict: COCO dataset dictionary

        Returns:
            (is_valid, error_messages)
        """
        logger.info("✔️  Validating COCO dataset...")

        errors = []

        # Check required keys
        required_keys = ["images", "annotations", "categories", "info"]
        for key in required_keys:
            if key not in coco_dict:
                errors.append(f"Missing required key: {key}")

        if errors:
            return False, errors

        # Check image consistency
        image_ids = set(img["id"] for img in coco_dict.get("images", []))
        category_ids = set(cat["id"] for cat in coco_dict.get("categories", []))

        # Validate annotations
        for ann in coco_dict.get("annotations", []):
            if ann["image_id"] not in image_ids:
                errors.append(f"Annotation {ann['id']} references invalid image {ann['image_id']}")
            if ann["category_id"] not in category_ids:
                errors.append(f"Annotation {ann['id']} references invalid category {ann['category_id']}")
            if ann["bbox"][2] <= 0 or ann["bbox"][3] <= 0:
                errors.append(f"Annotation {ann['id']} has invalid bbox dimensions")

        if errors:
            logger.error(f"❌ Validation failed with {len(errors)} errors")
            return False, errors

        logger.info("✅ COCO dataset validation passed")
        return True, []

    def compute_dataset_statistics(self) -> Dict:
        """
        Compute dataset statistics.

        Returns:
            Dictionary of statistics
        """
        logger.info("📈 Computing dataset statistics...")

        stats = {
            "total_images": len(self.images),
            "total_annotations": len(self.annotations),
            "avg_annotations_per_image": (
                len(self.annotations) / len(self.images)
                if self.images else 0
            ),
            "image_width": self.image_width,
            "image_height": self.image_height,
            "num_categories": len(self.categories),
        }

        # Per-category statistics
        class_counts = defaultdict(int)
        bbox_sizes = defaultdict(list)

        for ann in self.annotations:
            class_counts[ann.category_name] += 1
            bbox_sizes[ann.category_name].append(ann.bbox.area())

        stats["class_distribution"] = dict(class_counts)

        logger.info(f"  Total images: {stats['total_images']}")
        logger.info(f"  Total annotations: {stats['total_annotations']}")
        logger.info(f"  Avg annotations/image: {stats['avg_annotations_per_image']:.2f}")

        return stats

    def save_dataset_report(self, output_file: str = "dataset_report.txt") -> bool:
        """
        Generate and save comprehensive dataset report.

        Args:
            output_file: Output report filename

        Returns:
            True if successful
        """
        logger.info(f"📝 Generating dataset report...")

        try:
            report_path = self.output_dir / output_file

            with open(report_path, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("SYNTHETIC DATASET REPORT\n")
                f.write("=" * 70 + "\n\n")

                # Dataset overview
                f.write("OVERVIEW\n")
                f.write("-" * 70 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Total Images: {len(self.images)}\n")
                f.write(f"Total Annotations: {len(self.annotations)}\n")
                f.write(f"Categories: {len(self.categories)}\n\n")

                # Class distribution
                f.write("CLASS DISTRIBUTION\n")
                f.write("-" * 70 + "\n")
                distribution = self.analyze_class_distribution()
                for cat_name, percentage in sorted(distribution.items()):
                    f.write(f"  {cat_name:15s}: {percentage:6.1f}%\n")

                f.write("\n" + "=" * 70 + "\n")

            logger.info(f"✅ Report saved to {report_path.absolute()}")
            return True
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            return False


def main():
    """Main execution."""
    print("=" * 70)
    print("Exercise 7.2: Synthetic Data Generation")
    print("=" * 70)
    print()

    # Initialize generator
    generator = SyntheticDatasetGenerator(output_dir="./synthetic_dataset")

    # Generate dataset
    if not generator.generate_dataset(num_images=100):  # Use 100 for testing
        logger.error("Dataset generation failed")
        return 1

    # Analyze class distribution
    distribution = generator.analyze_class_distribution()

    # Balance dataset
    if not generator.balance_dataset(min_percentage=0.10):
        logger.warning("Dataset balancing recommended")

    # Compute statistics
    stats = generator.compute_dataset_statistics()
    logger.info(f"Dataset statistics: {stats}")

    # Export COCO
    if not generator.export_coco("coco_annotations.json"):
        logger.error("COCO export failed")
        return 1

    # Validate COCO
    coco_dict = json.loads((generator.output_dir / "coco_annotations.json").read_text())
    is_valid, errors = generator.validate_coco(coco_dict)

    if not is_valid:
        logger.error(f"Validation failed: {errors}")
        return 1

    # Generate report
    generator.save_dataset_report()

    print()
    print("=" * 70)
    print("✅ Exercise Complete: Dataset Generated Successfully")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    exit(main())
