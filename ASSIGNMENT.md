# Assignment: Synthetic Data Generation Backend (No Simulator)

**Course:** Synthetic Data Generation
**Submission Type:** Code + Report
**Allowed Libraries:** Python, NumPy, OpenCV, Open3D, FastAPI, Pydantic
**Not Needed:** Isaac Sim, Omniverse, Unity, Blender

---

## Objective

In this assignment, you will design and implement a **synthetic data generation backend** inspired by **Isaac Sim Replicator pipelines**, but without using any simulator.

You will:
- Procedurally generate synthetic scenes
- Render RGB, depth, semantic, and instance outputs
- Generate labeled point clouds
- Expose everything through a FastAPI service
- Export structured datasets

This assignment evaluates your **understanding of synthetic data pipelines**, not your ability to use Isaac Sim.

---

## Conceptual Mapping

| Isaac Sim Concept | This Assignment |
|------------------|----------------|
| USD Scene Graph | Python Scene Graph |
| Replicator | Procedural Scene Generator |
| Semantic Labels | Class IDs |
| Instance Labels | Instance IDs |
| RGB / Depth | OpenCV Rendering |
| Point Clouds | Depth to XYZ |
| Omniverse Backend | FastAPI Server |

---

## Expected Project Structure

```text
synthetic_backend/
├── scene/
│   ├── scene_object.py
│   ├── scene.py
│   ├── generator.py
│   └── library.py
├── render/
│   ├── camera.py
│   ├── renderer.py
│   └── raster.py
├── pointcloud/
│   ├── projection.py
│   └── ply_export.py
├── api/
│   ├── server.py
│   ├── models.py
│   └── state.py
├── config.py
└── README.md
```

---

## Part 1 -- Scene Representation

Define a **scene object model** (`scene_object.py`) that includes:

* `name` -- a descriptive name for the object
* `shape` -- the geometric primitive (`"sphere"`, `"cube"`, or `"cylinder"`)
* `class_id` -- semantic class identifier
* `instance_id` -- unique instance identifier
* `position` -- (x, y, z) coordinates in the scene
* `rotation_rpy` -- rotation as (roll, pitch, yaw)
* `scale` -- (sx, sy, sz) scale factors
* `color_rgb` -- (r, g, b) color values in the range [0, 1]

Define a **class library** (`library.py`) that maps class IDs to shape names and semantic visualization colors. For example:
- Class ID 1 → `"sphere"` with red semantic color
- Class ID 2 → `"cube"` with green semantic color
- Class ID 3 → `"cylinder"` with blue semantic color

**Important:** The shape determines the class (not independent). When generating objects, pick a class_id which determines the shape. The semantic visualization uses these colors, but the RGB rendering should use random colors per instance to create visual variety.

Define a **Scene** class (`scene.py`) that:

* Holds multiple `SceneObject` instances
* Supports an `add()` method to insert objects into the scene
* Supports a `reset()` method to clear all objects
* Supports a `to_dict()` method to serialize the scene state
* Preserves instance consistency

---

## Part 2 -- Procedural Scene Generator

Implement a generator (`generator.py`) that:

* Randomly places objects in a scene
* Assigns class IDs which determine the object shape (sphere/cube/cylinder)
* Assigns unique instance IDs to each object
* Randomizes pose, scale, and **RGB color** (fully random, NOT based on class color)
* Avoids object overlap (bonus, not mandatory)
* Supports deterministic generation via seed
* Supports configurable object counts

**Key point:** The `color_rgb` field should be a **random color per instance**, not derived from the semantic class. This ensures RGB images look visually varied while semantic masks show consistent class groupings.

```python
def generate_scene(num_objects: int, seed: int) -> Scene
```

**Starter snippet -- `scene/generator.py`:**

```python
import numpy as np
from .scene import Scene
from .scene_object import SceneObject
from .library import CLASS_LIBRARY

def generate_scene(num_objects: int, seed: int = 42) -> Scene:
    rng = np.random.default_rng(seed)
    scene = Scene()

    # TODO: for each object:
    #   - pick a class from CLASS_LIBRARY
    #   - create a SceneObject with randomized pose, scale, and color
    #   - add it to the scene

    return scene
```

---

## Part 3 -- Synthetic Rendering

Implement a simple **pinhole camera model** and generate all output modalities. Your renderer should use a **billboard / projected-shape approach** (not ray tracing): project each object's center into the image plane, then draw the object's shape at the projected location with a size proportional to its scale and distance.

**Architecture:**

* `camera.py` -- Defines the pinhole camera model and handles 3D-to-2D projection. Camera intrinsics (focal length, principal point, resolution) and scene bounds should be defined in `config.py`.
* `renderer.py` -- Main rendering entry point. Orchestrates the rendering pipeline and produces all output images (RGB, depth, semantic mask, instance mask). Implements a **Z-buffer** to handle depth ordering so that closer objects correctly occlude farther ones.
* `raster.py` -- Handles the actual drawing of projected shapes (circles for spheres, rectangles for cubes, ellipses for cylinders, etc.) onto the image buffers.

### RGB Image

* Render objects as colored shapes based on their `color_rgb`
* Apply projection from 3D to 2D using the pinhole camera model
* Handle occlusion via Z-buffer (depth ordering)

### Depth Image

* Generate a depth map from the Z-buffer
* Normalize values for visualization
* Background pixels should have a defined maximum or infinite depth

### Segmentation Masks

* Semantic mask (`class_id` per pixel)
* Instance mask (`instance_id` per pixel)
* These are naturally produced alongside the Z-buffer rendering

**Starter snippet -- `render/renderer.py`:**

```python
import numpy as np

def render_scene(scene, camera):
    """
    Renders the scene and returns a dict with keys:
      'rgb'      -> HxWx3 uint8
      'depth'    -> HxW float32
      'semantic' -> HxW int32
      'instance' -> HxW int32
    """
    raise NotImplementedError
```

---

## Part 4 -- Point Cloud Generation

From the depth map, generate a labeled point cloud **in the camera frame**:

* Reconstruct XYZ points by back-projecting each pixel using the camera intrinsics
* The resulting 3D coordinates are expressed in the camera's coordinate frame
* Attach RGB color from the rendered color image
* Attach semantic and instance labels from the segmentation masks
* Export as `.ply` using Open3D

---

## Part 5 -- FastAPI Backend

Expose the pipeline via API endpoints. Use Pydantic models (`models.py`) for request/response validation and a shared state module (`state.py`) to hold the current scene.

### Scene Control

```http
POST /scene/generate    -- Generate a new random scene
GET  /scene/state       -- Return the current scene as JSON
POST /scene/reset       -- Clear the current scene
```

### Rendering

```http
GET /render/rgb         -- Return the RGB image (PNG)
GET /render/depth       -- Return the depth image (PNG)
GET /render/semantic    -- Return the semantic mask (PNG)
GET /render/instance    -- Return the instance mask (PNG)
```

### Point Cloud

```http
GET /pointcloud         -- Return the point cloud (PLY file)
```

### Dataset Export

```http
POST /dataset/export    -- Export a batch of scenes with all modalities
```

**Starter snippet -- `api/server.py`:**

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(title="Synthetic Data Backend")

@app.post("/scene/generate")
def generate_scene_api():
    # TODO: generate a scene and store it in shared state
    return {"status": "TODO"}

@app.get("/scene/state")
def get_scene_state():
    # TODO: return the current scene as JSON
    return {"status": "TODO"}

@app.post("/scene/reset")
def reset_scene():
    # TODO: reset the current scene
    return {"status": "TODO"}

@app.get("/render/rgb")
def render_rgb():
    # TODO: render and return RGB image as PNG
    raise NotImplementedError

@app.get("/render/depth")
def render_depth():
    # TODO: render and return depth image as PNG
    raise NotImplementedError
```

---

## Part 6 -- Report (Mandatory)

In `README.md`, answer:

1. Why synthetic data is useful
2. Advantages vs real data
3. Limitations of your renderer
4. How Isaac Sim improves this pipeline

---

## Rules

* Clean, modular code
* No monolithic scripts
* No simulator usage
* Academic honesty applies

---

## Learning Outcomes

By completing this assignment, you will understand:

* How synthetic data pipelines work
* How simulation backends are designed
* How synthetic datasets are generated at scale
