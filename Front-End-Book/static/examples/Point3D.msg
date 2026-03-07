# Point3D.msg - A 3D point with position and frame information
#
# This is a custom ROS 2 message definition file.
# Fields:
#   - x, y, z: Position coordinates in 3D space (meters)
#   - frame_id: Reference frame for this point (e.g., "world", "base_link")
#   - label: Optional text label for the point

float64 x
float64 y
float64 z
string frame_id
string label
