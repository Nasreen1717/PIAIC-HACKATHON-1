# Humanoid Robot Assets (USD format)

This directory contains USD (Universal Scene Description) assets for humanoid robots.

## Files

- `humanoid_base.usd`: Base humanoid template with generic structure
- `materials/`: Physics and rendering materials
- `meshes/`: 3D mesh files for visualization

## Usage

Import USD assets into Isaac Sim:

```python
from isaacsim import SimulationApp
stage = SimulationApp.instance().stage
stage.DefinePrim("/World/humanoid", "Reference")
stage.GetPrimAtPath("/World/humanoid").GetReferences().AddReference("file:///path/to/humanoid_base.usd")
```
