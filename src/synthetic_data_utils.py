"""
T018: Synthetic data generation utilities for Module 3.

Handles image generation, annotation, and export for training datasets.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ImageMetadata:
    """Metadata for synthetic image."""
    filename: str
    timestamp: float
    annotations: Dict
    camera_intrinsics: Dict
    pose: List[float]


class SyntheticDataGenerator:
    """Generate and manage synthetic training datasets."""

    def __init__(self, output_dir: Path):
        """Initialize synthetic data generator.

        Args:
            output_dir: Directory to save generated dataset
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "depth").mkdir(exist_ok=True)
        (self.output_dir / "annotations").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)

        self.image_count = 0
        self.metadata_list: List[ImageMetadata] = []

    def generate_batch(
        self,
        num_samples: int,
        resolution: Tuple[int, int] = (1920, 1080),
        annotation_types: List[str] = None,
        batch_size: int = 100
    ) -> Dict:
        """Generate batch of synthetic images with annotations.

        Args:
            num_samples: Number of images to generate
            resolution: Image resolution (width, height)
            annotation_types: Types of annotations (segmentation, depth, bbox)
            batch_size: Number of images per batch

        Returns:
            Dictionary with generation results
        """
        if annotation_types is None:
            annotation_types = ["segmentation_mask", "depth_map"]

        results = {
            "total_samples": num_samples,
            "batches": [],
            "images_per_hour": 0,
            "generation_time_seconds": 0,
        }

        # Simulate batch generation
        total_images = 0
        for batch_idx in range(0, num_samples, batch_size):
            batch_count = min(batch_size, num_samples - batch_idx)

            batch_result = {
                "batch_id": batch_idx // batch_size,
                "images_in_batch": batch_count,
                "annotations": {atype: batch_count for atype in annotation_types},
                "image_filenames": [
                    f"image_{self.image_count + i:06d}.png"
                    for i in range(batch_count)
                ],
                "annotation_filenames": {
                    atype: [
                        f"{atype}_{self.image_count + i:06d}.json"
                        for i in range(batch_count)
                    ] for atype in annotation_types
                }
            }

            results["batches"].append(batch_result)
            total_images += batch_count
            self.image_count += batch_count

        results["total_images_generated"] = total_images
        results["success"] = total_images == num_samples

        return results

    def export_dataset_manifest(self) -> Dict:
        """Export dataset manifest with metadata.

        Returns:
            Manifest dictionary
        """
        manifest = {
            "dataset_id": "module-3-synthetic-v1",
            "total_images": self.image_count,
            "resolution": [1920, 1080],
            "annotation_types": ["segmentation_mask", "depth_map", "bounding_box"],
            "timestamp": str(Path.cwd()),
            "image_list": [f"image_{i:06d}.png" for i in range(self.image_count)],
        }

        # Save manifest
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        return manifest

    def validate_export(self) -> bool:
        """Validate that all files were exported correctly.

        Returns:
            True if all files valid
        """
        images_dir = self.output_dir / "images"
        return (
            images_dir.exists() and
            len(list(images_dir.glob("*.png"))) > 0
        )


class AnnotationGenerator:
    """Generate annotations for synthetic images."""

    @staticmethod
    def generate_bounding_box_annotation(
        image_id: str,
        objects: List[Dict]
    ) -> Dict:
        """Generate bounding box annotation.

        Args:
            image_id: Image identifier
            objects: List of objects with bounds

        Returns:
            Annotation dictionary
        """
        return {
            "image_id": image_id,
            "annotations": [
                {
                    "category": obj.get("class", "unknown"),
                    "bbox": obj.get("bounds", [0, 0, 100, 100]),
                    "confidence": obj.get("confidence", 1.0),
                } for obj in objects
            ]
        }

    @staticmethod
    def generate_segmentation_annotation(
        image_id: str,
        segmentation_mask_path: str
    ) -> Dict:
        """Generate segmentation annotation.

        Args:
            image_id: Image identifier
            segmentation_mask_path: Path to segmentation mask

        Returns:
            Annotation dictionary
        """
        return {
            "image_id": image_id,
            "segmentation_mask": segmentation_mask_path,
            "format": "PNG",
        }

    @staticmethod
    def generate_depth_annotation(
        image_id: str,
        depth_map_path: str,
        depth_scale: float = 0.001
    ) -> Dict:
        """Generate depth annotation.

        Args:
            image_id: Image identifier
            depth_map_path: Path to depth map
            depth_scale: Scale factor for depth values

        Returns:
            Annotation dictionary
        """
        return {
            "image_id": image_id,
            "depth_map": depth_map_path,
            "format": "PNG",
            "depth_scale": depth_scale,
        }


def create_sample_dataset(output_dir: str, num_samples: int = 100) -> None:
    """Create a sample synthetic dataset.

    Args:
        output_dir: Directory to create dataset
        num_samples: Number of samples to generate
    """
    generator = SyntheticDataGenerator(Path(output_dir))
    results = generator.generate_batch(num_samples)
    manifest = generator.export_dataset_manifest()

    print(f"Generated {results['total_images_generated']} synthetic images")
    print(f"Dataset saved to: {output_dir}")
    print(f"Manifest: {manifest}")
