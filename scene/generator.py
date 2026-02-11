""" Implement a generator (`generator.py`) that:

* Randomly places objects in a scene
* Assigns class IDs which determine the object shape (sphere/cube/cylinder)
* Assigns unique instance IDs to each object
* Randomizes pose, scale, and **RGB color** (fully random, NOT based on class color)
* Avoids object overlap (bonus, not mandatory)
* Supports deterministic generation via seed
* Supports configurable object counts

**Key point:** The `color_rgb` field should be a **random color per instance**, not derived from the semantic class. This ensures RGB images look visually varied while semantic masks show consistent class groupings.
"""

import numpy as np
from .scene import Scene
from .scene_object import SceneObject, Shape
from .library import CLASS_LIBRARY

def generate_scene(num_objects: int, seed: int = 42) -> Scene:
    rng = np.random.default_rng(seed)
    scene = Scene()
    class_ids = list(CLASS_LIBRARY.keys())

    for i in range(num_objects):

        class_id = int(rng.choice(class_ids)) #mnna2e id => mna3rf ayya shape
        shape_str = CLASS_LIBRARY[class_id]["shape"] #okok so ayya shape 
        shape = Shape(shape_str)  #mn2lob el string enum
        instance_id = i + 1
        x = float(rng.uniform(-2.0, 2.0))
        y = float(rng.uniform(-2.0, 2.0))
        z = float(rng.uniform(3.0, 8.0)) #haydole reasonable ranges 
        roll  = float(rng.uniform(-np.pi, np.pi))
        pitch = float(rng.uniform(-np.pi, np.pi))
        yaw   = float(rng.uniform(-np.pi, np.pi))
        s = float(rng.uniform(0.3, 1.2))
        scale = (s, s, s)  
        color = tuple(float(c) for c in rng.random(3))

        obj = SceneObject(
            name=f"obj_{instance_id}",
            shape=shape,
            class_id=class_id,
            instance_id=instance_id,
            position=(x, y, z),
            rotation_rpy=(roll, pitch, yaw),
            scale=scale,
            color_rgb=color,
        )

        scene.add(obj)

    return scene