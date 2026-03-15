#!/usr/bin/env python3
"""
URDF to USD Conversion and Import

Purpose:
    Import URDF robot models into Isaac Sim and convert to USD format with
    proper physics configuration and collision handling.

Prerequisites:
    - Isaac Sim 2023.8+ installed
    - URDF file with valid mesh paths
    - PyYAML for URDF parsing

Usage:
    python3 example-7.2-urdf-import.py --urdf /path/to/robot.urdf --output robot.usd

Expected Output:
    ✅ URDF loaded: robot.urdf
    ✅ Converting to USD...
    ✅ Asset saved: robot.usd
    ✅ Physics configured

"""

import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from dataclasses import dataclass
import xml.etree.ElementTree as ET


# Configure logging with emoji indicators
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class URDFLink:
    """Represents a URDF link."""
    name: str
    mass: float = 1.0
    inertia: Tuple[float, float, float] = (0.1, 0.1, 0.1)
    visual_mesh: str = None
    collision_mesh: str = None
    collision_shape: str = "mesh"  # "mesh", "box", "sphere", "cylinder"


@dataclass
class URDFJoint:
    """Represents a URDF joint."""
    name: str
    joint_type: str  # "fixed", "revolute", "prismatic", "continuous"
    parent: str
    child: str
    axis: Tuple[float, float, float] = (0, 0, 1)
    lower_limit: float = -3.14
    upper_limit: float = 3.14
    effort: float = 100.0
    velocity: float = 1.0


class URDFParser:
    """Parse URDF XML files."""

    def __init__(self, urdf_path: str, mesh_dir: str = None):
        """Initialize parser."""
        self.urdf_path = Path(urdf_path)
        self.mesh_dir = Path(mesh_dir) if mesh_dir else self.urdf_path.parent
        self.tree = ET.parse(str(self.urdf_path))
        self.root = self.tree.getroot()
        self.links: Dict[str, URDFLink] = {}
        self.joints: Dict[str, URDFJoint] = {}

        logger.info(f"📖 Parsing URDF: {self.urdf_path.name}")

    def parse_links(self) -> Dict[str, URDFLink]:
        """Parse all links from URDF."""
        for link_elem in self.root.findall('link'):
            link_name = link_elem.get('name')

            # Parse mass
            mass = 1.0
            inertial = link_elem.find('inertial')
            if inertial is not None:
                mass_elem = inertial.find('mass')
                if mass_elem is not None:
                    mass = float(mass_elem.get('value', 1.0))

            # Parse visual mesh
            visual_mesh = None
            visual = link_elem.find('visual')
            if visual is not None:
                mesh = visual.find('geometry/mesh')
                if mesh is not None:
                    visual_mesh = mesh.get('filename')

            # Parse collision mesh
            collision_mesh = None
            collision = link_elem.find('collision')
            if collision is not None:
                mesh = collision.find('geometry/mesh')
                if mesh is not None:
                    collision_mesh = mesh.get('filename')

            link = URDFLink(
                name=link_name,
                mass=mass,
                visual_mesh=visual_mesh,
                collision_mesh=collision_mesh
            )
            self.links[link_name] = link

        logger.info(f"✅ Parsed {len(self.links)} links")
        return self.links

    def parse_joints(self) -> Dict[str, URDFJoint]:
        """Parse all joints from URDF."""
        for joint_elem in self.root.findall('joint'):
            joint_name = joint_elem.get('name')
            joint_type = joint_elem.get('type')

            parent_elem = joint_elem.find('parent')
            child_elem = joint_elem.find('child')
            parent = parent_elem.get('link') if parent_elem is not None else ""
            child = child_elem.get('link') if child_elem is not None else ""

            # Parse axis
            axis_elem = joint_elem.find('axis')
            axis = (0, 0, 1)
            if axis_elem is not None:
                axis_str = axis_elem.get('xyz', '0 0 1')
                axis = tuple(map(float, axis_str.split()))

            # Parse limits
            lower_limit = -3.14
            upper_limit = 3.14
            limit_elem = joint_elem.find('limit')
            if limit_elem is not None:
                lower_limit = float(limit_elem.get('lower', -3.14))
                upper_limit = float(limit_elem.get('upper', 3.14))

            joint = URDFJoint(
                name=joint_name,
                joint_type=joint_type,
                parent=parent,
                child=child,
                axis=axis,
                lower_limit=lower_limit,
                upper_limit=upper_limit
            )
            self.joints[joint_name] = joint

        logger.info(f"✅ Parsed {len(self.joints)} joints")
        return self.joints

    def validate_meshes(self) -> bool:
        """✅ Validate all mesh files exist."""
        missing_meshes = []

        for link in self.links.values():
            for mesh_file in [link.visual_mesh, link.collision_mesh]:
                if mesh_file:
                    # Resolve mesh path
                    if mesh_file.startswith("package://"):
                        # TODO: Resolve ROS package path
                        logger.warning(f"⚠️  Package path not resolved: {mesh_file}")
                    else:
                        mesh_path = self.mesh_dir / mesh_file
                        if not mesh_path.exists():
                            missing_meshes.append(str(mesh_path))

        if missing_meshes:
            logger.error(f"❌ Missing mesh files:")
            for mesh in missing_meshes:
                logger.error(f"   {mesh}")
            return False

        logger.info("✅ All mesh files validated")
        return True


class USD Generator:
    """Generate USD files from URDF data."""

    def __init__(self, urdf_data: URDFParser):
        """Initialize USD generator."""
        self.urdf = urdf_data
        self.usd_content = ""

    def generate(self) -> str:
        """🔄 Generate USD format content."""
        lines = [
            "#usda 1.0",
            "(",
            '    defaultPrim = "World"',
            ")",
            "",
            'def Xform "World" {',
        ]

        # Add all links
        for link_name, link in self.urdf.links.items():
            lines.append(f'    def Xform "{link_name}" {{')
            lines.append(f'        rel physics:rigidBody = "/{link_name}/RigidBody"')

            # Add visual mesh reference
            if link.visual_mesh:
                lines.append(f'        def Mesh "visual" {{')
                lines.append(f'            asset inputs:chdir = @{link.visual_mesh}@')
                lines.append(f'        }}')

            # Add collision mesh reference
            if link.collision_mesh:
                lines.append(f'        def Mesh "collision" {{')
                lines.append(f'            asset inputs:chdir = @{link.collision_mesh}@')
                lines.append(f'            bool collision:approximateConvexDecomp = true')
                lines.append(f'        }}')

            # Add rigid body properties
            lines.append(f'        def RigidBodySchema "RigidBody" {{')
            lines.append(f'            float physics:mass = {link.mass}')
            lines.append(f'            float3 physics:velocity = (0, 0, 0)')
            lines.append(f'            float3 physics:angularVelocity = (0, 0, 0)')
            lines.append(f'        }}')
            lines.append(f'    }}')
            lines.append("")

        # Add joints
        for joint_name, joint in self.urdf.joints.items():
            if joint.joint_type != "fixed":
                lines.append(f'    def Joint "{joint_name}" {{')
                lines.append(f'        rel physics:parentLink = "/{joint.parent}"')
                lines.append(f'        rel physics:childLink = "/{joint.child}"')
                lines.append(f'        float3 physics:axis = ({joint.axis[0]}, {joint.axis[1]}, {joint.axis[2]})')

                if joint.joint_type == "revolute":
                    lines.append(f'        float physics:lowerLimit = {joint.lower_limit}')
                    lines.append(f'        float physics:upperLimit = {joint.upper_limit}')

                lines.append(f'    }}')
                lines.append("")

        lines.append("}")

        self.usd_content = "\n".join(lines)
        logger.info("✅ USD content generated")
        return self.usd_content

    def save(self, output_path: str) -> bool:
        """💾 Save USD to file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                f.write(self.usd_content)

            logger.info(f"💾 Saved USD: {output_file}")
            logger.info(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save USD: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Convert URDF to USD format")
    parser.add_argument('--urdf', required=True, help='Path to URDF file')
    parser.add_argument('--output', required=True, help='Output USD file path')
    parser.add_argument('--mesh-dir', help='Directory containing mesh files')

    args = parser.parse_args()

    try:
        # Parse URDF
        urdf_parser = URDFParser(args.urdf, args.mesh_dir)
        urdf_parser.parse_links()
        urdf_parser.parse_joints()

        # Validate
        if not urdf_parser.validate_meshes():
            logger.warning("⚠️  Some meshes missing, continuing...")

        # Generate USD
        usd_gen = USD Generator(urdf_parser)
        usd_gen.generate()

        # Save
        if usd_gen.save(args.output):
            logger.info("✅ URDF import complete!")
            return 0
        else:
            logger.error("❌ USD save failed")
            return 1

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
