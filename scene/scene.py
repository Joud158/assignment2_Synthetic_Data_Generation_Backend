""" Define a **Scene** class (`scene.py`) that:

* Holds multiple `SceneObject` instances
* Supports an `add()` method to insert objects into the scene
* Supports a `reset()` method to clear all objects
* Supports a `to_dict()` method to serialize the scene state
* Preserves instance consistency """

# e5r so2al bi part 1 

from __future__ import annotations
from typing import List, Dict
from .scene_object import SceneObject

class Scene:
    def __init__(self):
        self.objects: List[SceneObject] = []
        self._next_instance_id: int = 1 

    def add(self, obj: SceneObject) -> None:
        self.objects.append(obj)
        if obj.instance_id >= self._next_instance_id:
            self._next_instance_id = obj.instance_id + 1

    def reset(self) -> None:
        self.objects.clear()
        self._next_instance_id = 1

    def to_dict(self) -> Dict:
        return {
            "num_objects": len(self.objects),
            "objects": [o.model_dump() for o in self.objects],
        }

    def new_instance_id(self) -> int:
        iid = self._next_instance_id
        self._next_instance_id += 1
        return iid

    

    
