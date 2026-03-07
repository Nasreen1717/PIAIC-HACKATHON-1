#!/usr/bin/env python3
"""
Test Suite for Exercise 7.2: Synthetic Data Generation

Comprehensive pytest suite with 16+ tests covering:
- Dataset generation and randomization
- COCO format creation and validation
- Class distribution analysis
- Bounding box accuracy
- JSON structure validation

Run with: pytest test_solution.py -v

Author: Isaac Sim Educational Module
Version: 1.0.0
"""

import pytest
import json
import tempfile
from pathlib import Path
from solution import (
    BoundingBox,
    SceneRandomization,
    ObjectAnnotation,
    ImageMetadata,
    CategoryDefinition,
    SyntheticDatasetGenerator
)


class TestBoundingBox:
    """Test BoundingBox class."""

    def test_bbox_creation(self):
        """✅ Test bounding box creation."""
        bbox = BoundingBox(x=10, y=20, width=100, height=80)
        assert bbox.x == 10
        assert bbox.y == 20
        assert bbox.width == 100
        assert bbox.height == 80

    def test_bbox_to_coco(self):
        """✅ Test conversion to COCO format."""
        bbox = BoundingBox(x=10, y=20, width=100, height=80)
        coco = bbox.to_coco()
        assert coco == [10, 20, 100, 80]

    def test_bbox_area(self):
        """✅ Test area calculation."""
        bbox = BoundingBox(x=0, y=0, width=100, height=50)
        assert bbox.area() == 5000

    def test_bbox_clip_to_image(self):
        """✅ Test clipping to image bounds."""
        bbox = BoundingBox(x=600, y=400, width=100, height=100)
        clipped = bbox.clip_to_image(640, 480)
        assert clipped.x <= 640
        assert clipped.y <= 480
        assert clipped.x + clipped.width <= 640
        assert clipped.y + clipped.height <= 480

    def test_bbox_clip_negative(self):
        """✅ Test clipping negative coordinates."""
        bbox = BoundingBox(x=-50, y=-30, width=100, height=80)
        clipped = bbox.clip_to_image(640, 480)
        assert clipped.x >= 0
        assert clipped.y >= 0


class TestSceneRandomization:
    """Test SceneRandomization dataclass."""

    def test_default_randomization(self):
        """✅ Test default randomization values."""
        rand = SceneRandomization()
        assert rand.camera_x == 0.0
        assert rand.light_intensity == 0.7
        assert rand.num_objects == 3

    def test_custom_randomization(self):
        """✅ Test custom randomization."""
        rand = SceneRandomization(
            camera_x=0.5,
            light_intensity=0.9,
            num_objects=5
        )
        assert rand.camera_x == 0.5
        assert rand.light_intensity == 0.9
        assert rand.num_objects == 5


class TestObjectAnnotation:
    """Test ObjectAnnotation class."""

    def test_annotation_creation(self):
        """✅ Test annotation creation."""
        bbox = BoundingBox(10, 20, 100, 80)
        ann = ObjectAnnotation(
            annotation_id=1,
            image_id=0,
            category_id=1,
            category_name="cube",
            bbox=bbox,
            area=bbox.area()
        )
        assert ann.annotation_id == 1
        assert ann.category_id == 1

    def test_annotation_to_coco(self):
        """✅ Test conversion to COCO format."""
        bbox = BoundingBox(10, 20, 100, 80)
        ann = ObjectAnnotation(
            annotation_id=1,
            image_id=0,
            category_id=1,
            category_name="cube",
            bbox=bbox,
            area=8000
        )
        coco = ann.to_coco()
        assert "id" in coco
        assert "image_id" in coco
        assert "category_id" in coco
        assert "bbox" in coco
        assert "area" in coco


class TestImageMetadata:
    """Test ImageMetadata class."""

    def test_image_creation(self):
        """✅ Test image metadata creation."""
        img = ImageMetadata(
            image_id=0,
            file_name="image_000000.png",
            height=480,
            width=640
        )
        assert img.image_id == 0
        assert img.file_name == "image_000000.png"
        assert img.height == 480
        assert img.width == 640

    def test_image_to_coco(self):
        """✅ Test conversion to COCO format."""
        img = ImageMetadata(
            image_id=0,
            file_name="image_000000.png"
        )
        coco = img.to_coco()
        assert coco["id"] == 0
        assert coco["file_name"] == "image_000000.png"
        assert "height" in coco
        assert "width" in coco


class TestCategoryDefinition:
    """Test CategoryDefinition class."""

    def test_category_creation(self):
        """✅ Test category creation."""
        cat = CategoryDefinition(id=1, name="cube")
        assert cat.id == 1
        assert cat.name == "cube"

    def test_category_to_coco(self):
        """✅ Test conversion to COCO format."""
        cat = CategoryDefinition(id=1, name="cube", supercategory="geometric")
        coco = cat.to_coco()
        assert coco["id"] == 1
        assert coco["name"] == "cube"
        assert coco["supercategory"] == "geometric"


class TestSyntheticDatasetGenerator:
    """Test SyntheticDatasetGenerator class."""

    def test_generator_initialization(self):
        """✅ Test generator initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            assert gen.image_width == 640
            assert gen.image_height == 480
            assert len(gen.categories) == 10  # 10 object types

    def test_setup_scene(self):
        """✅ Test scene setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            result = gen.setup_scene()
            assert result == True

    def test_randomize_scene(self):
        """✅ Test scene randomization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            rand = gen.randomize_scene()

            # Check ranges
            assert -0.3 <= rand.camera_x <= 0.3
            assert -0.2 <= rand.camera_y <= 0.2
            assert 0.5 <= rand.camera_z <= 1.0
            assert 0.3 <= rand.light_intensity <= 1.0
            assert 3000 <= rand.light_color_temp <= 6500
            assert 1 <= rand.num_objects <= 5

    def test_randomization_diversity(self):
        """✅ Test that randomization produces diverse output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)

            # Generate multiple randomizations
            rands = [gen.randomize_scene() for _ in range(10)]

            # Check that they're different
            camera_xs = [r.camera_x for r in rands]
            assert len(set(camera_xs)) > 1  # Not all the same

    def test_get_visible_objects(self):
        """✅ Test getting visible objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            rand = gen.randomize_scene()

            visible = gen.get_visible_objects(rand)
            assert len(visible) == rand.num_objects

            # Check structure
            for obj_type_id, instance_id, position in visible:
                assert 1 <= obj_type_id <= 10
                assert isinstance(position, tuple)
                assert len(position) == 2

    def test_get_bounding_boxes(self):
        """✅ Test bounding box extraction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            rand = gen.randomize_scene()
            visible = gen.get_visible_objects(rand)

            annotations = gen.get_bounding_boxes(visible, rand)
            assert len(annotations) > 0
            assert all(isinstance(a, ObjectAnnotation) for a in annotations)

    def test_bbox_within_bounds(self):
        """✅ Test that bboxes are within image bounds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            rand = gen.randomize_scene()
            visible = gen.get_visible_objects(rand)
            annotations = gen.get_bounding_boxes(visible, rand)

            for ann in annotations:
                assert ann.bbox.x >= 0
                assert ann.bbox.y >= 0
                assert ann.bbox.x + ann.bbox.width <= gen.image_width
                assert ann.bbox.y + ann.bbox.height <= gen.image_height

    def test_render_frame(self):
        """✅ Test frame rendering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            success, filename = gen.render_frame(0)

            assert success == True
            assert filename == "image_000000.png"
            # Check that file was created
            assert (Path(tmpdir) / filename).exists()

    def test_generate_frame_annotations(self):
        """✅ Test frame annotation generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            image = gen.generate_frame_annotations(0, "image_000000.png")

            assert isinstance(image, ImageMetadata)
            assert image.image_id == 0
            assert image.file_name == "image_000000.png"

    def test_generate_dataset_small(self):
        """✅ Test small dataset generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            result = gen.generate_dataset(num_images=10)

            assert result == True
            assert len(gen.images) == 10
            assert len(gen.annotations) > 0

    def test_analyze_class_distribution(self):
        """✅ Test class distribution analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            gen.generate_dataset(num_images=50)

            distribution = gen.analyze_class_distribution()
            assert isinstance(distribution, dict)
            assert len(distribution) > 0

            # All percentages should sum to ~100
            total_pct = sum(distribution.values())
            assert 95 < total_pct <= 100

    def test_export_coco(self):
        """✅ Test COCO export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            gen.generate_dataset(num_images=10)

            result = gen.export_coco("test_coco.json")
            assert result == True

            # Verify file was created and is valid JSON
            coco_file = Path(tmpdir) / "test_coco.json"
            assert coco_file.exists()

            coco = json.loads(coco_file.read_text())
            assert "images" in coco
            assert "annotations" in coco
            assert "categories" in coco

    def test_validate_coco_valid(self):
        """✅ Test COCO validation with valid dataset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            gen.generate_dataset(num_images=10)
            gen.export_coco("test_coco.json")

            coco_file = Path(tmpdir) / "test_coco.json"
            coco = json.loads(coco_file.read_text())

            is_valid, errors = gen.validate_coco(coco)
            assert is_valid == True
            assert len(errors) == 0

    def test_validate_coco_missing_key(self):
        """❌ Test COCO validation with missing key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)

            coco = {"images": [], "annotations": []}  # Missing 'categories'
            is_valid, errors = gen.validate_coco(coco)
            assert is_valid == False
            assert len(errors) > 0

    def test_validate_coco_invalid_reference(self):
        """❌ Test COCO validation with invalid references."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)

            coco = {
                "images": [{"id": 1, "file_name": "img.png"}],
                "annotations": [
                    {
                        "id": 1,
                        "image_id": 999,  # Invalid reference
                        "category_id": 1,
                        "bbox": [0, 0, 10, 10],
                        "area": 100,
                        "iscrowd": 0
                    }
                ],
                "categories": [{"id": 1, "name": "cube"}]
            }

            is_valid, errors = gen.validate_coco(coco)
            assert is_valid == False

    def test_compute_statistics(self):
        """✅ Test statistics computation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            gen.generate_dataset(num_images=20)

            stats = gen.compute_dataset_statistics()
            assert "total_images" in stats
            assert "total_annotations" in stats
            assert "avg_annotations_per_image" in stats
            assert stats["total_images"] == 20

    def test_save_report(self):
        """✅ Test report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            gen.generate_dataset(num_images=10)

            result = gen.save_dataset_report("test_report.txt")
            assert result == True

            # Check file was created
            report_file = Path(tmpdir) / "test_report.txt"
            assert report_file.exists()
            assert "SYNTHETIC DATASET REPORT" in report_file.read_text()


class TestIntegration:
    """Integration tests."""

    def test_end_to_end_workflow(self):
        """✅ Test complete workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)

            # Setup
            assert gen.setup_scene() == True

            # Generate
            assert gen.generate_dataset(num_images=50) == True
            assert len(gen.images) == 50

            # Analyze
            distribution = gen.analyze_class_distribution()
            assert len(distribution) > 0

            # Export
            assert gen.export_coco("coco.json") == True

            # Validate
            coco_file = Path(tmpdir) / "coco.json"
            coco = json.loads(coco_file.read_text())
            is_valid, errors = gen.validate_coco(coco)
            assert is_valid == True

    def test_dataset_consistency(self):
        """✅ Test dataset consistency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            gen.generate_dataset(num_images=30)

            # All annotations should reference valid images
            image_ids = set(img.image_id for img in gen.images)
            for ann in gen.annotations:
                assert ann.image_id in image_ids

    def test_coco_structure_completeness(self):
        """✅ Test that COCO export has all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SyntheticDatasetGenerator(output_dir=tmpdir)
            gen.generate_dataset(num_images=20)
            gen.export_coco("test.json")

            coco = json.loads((Path(tmpdir) / "test.json").read_text())

            # Check structure
            assert "info" in coco
            assert "images" in coco
            assert "annotations" in coco
            assert "categories" in coco

            # Check that arrays have data
            assert len(coco["images"]) > 0
            assert len(coco["annotations"]) > 0
            assert len(coco["categories"]) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
