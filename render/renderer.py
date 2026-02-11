""" ## Part 3 -- Synthetic Rendering

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

"""

import numpy as np
from .raster import raster_circle, raster_rect, raster_ellipse
from config import DEPTH_INF, SIZE_K

def to_u8(rgb01):
    return np.clip(np.array(rgb01) * 255.0, 0, 255).astype(np.uint8)

def render_scene(scene, camera):

    H, W = camera.height, camera.width
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    depth = np.full((H, W), DEPTH_INF, dtype=np.float32)
    semantic = np.zeros((H, W), dtype=np.int32)
    instance = np.zeros((H, W), dtype=np.int32)

    for obj in scene.objects:

        proj = camera.project(obj.position)
        if proj is None: #wara el camera
            continue
        u, v, z = proj
        if u < 0 or u >= W or v < 0 or v >= H: #barat el image
            continue

        #pixel size conversion
        s_avg = float(sum(obj.scale) / 3.0)
        base = int(round(SIZE_K * (s_avg / z)))
        base = max(1, base)

        if obj.shape.value == "sphere":
            ras = raster_circle(u, v, base, W, H)
        elif obj.shape.value == "cube":
            ras = raster_rect(u, v, base, W, H)
        else:
            ras = raster_ellipse(u, v, rx=base, ry=max(1, base // 2), w=W, h=H)

        if ras is None:
            continue

        ys, xs, local_mask = ras
        current_depth = depth[ys, xs] 
        obj_depth = np.full_like(current_depth, z, dtype=np.float32)
        closer = (obj_depth < current_depth) & local_mask

        if not np.any(closer):
            continue

        depth_patch = depth[ys, xs]
        depth_patch[closer] = z
        depth[ys, xs] = depth_patch

        semantic_patch = semantic[ys, xs]
        semantic_patch[closer] = obj.class_id
        semantic[ys, xs] = semantic_patch

        instance_patch = instance[ys, xs]
        instance_patch[closer] = obj.instance_id
        instance[ys, xs] = instance_patch

        rgb_patch = rgb[ys, xs]
        color_u8 = to_u8(obj.color_rgb)
        rgb_patch[closer] = color_u8
        rgb[ys, xs] = rgb_patch

    return {
        "rgb": rgb,
        "depth": depth,
        "semantic": semantic,
        "instance": instance,
    }
