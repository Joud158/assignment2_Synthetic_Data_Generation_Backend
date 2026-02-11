""" Define a **scene object model** (`scene_object.py`) that includes:

* `name` -- a descriptive name for the object
* `shape` -- the geometric primitive (`"sphere"`, `"cube"`, or `"cylinder"`)
* `class_id` -- semantic class identifier
* `instance_id` -- unique instance identifier
* `position` -- (x, y, z) coordinates in the scene
* `rotation_rpy` -- rotation as (roll, pitch, yaw)
* `scale` -- (sx, sy, sz) scale factors
* `color_rgb` -- (r, g, b) color values in the range [0, 1] """


# hone 3m na3ml el data structure lal object => esma scene object model
# one object kif 7a ykon defined

# pydantic 5abriyet
# ----------------------
# pydantic is a library that provides us with BaseModel and Field
# Basemodel is mtl a super class that checks data
# Field hiye to set rules on properties bi2alb el class

from pydantic import BaseModel, Field, field_validator # pydantic elna is used for json conversion
from enum import Enum

class Shape(str, Enum):
    sphere = "sphere"
    cube = "cube"
    cylinder = "cylinder"

class SceneObject(BaseModel):
    # type hinting
    # lezm na3ml define la shu howe el shape 
    name: str
    shape: Shape
    class_id: int = Field(ge=1)
    instance_id: int = Field(ge=1)
    position: tuple[float, float, float] = Field(...)
    rotation_rpy: tuple[float, float, float] = Field(...)
    scale: tuple[float, float, float] = Field(...) #this field is required hk ma3neta
    color_rgb: tuple[float, float, float] = Field(...)

    @field_validator("color_rgb")
    @classmethod
    def color_in_0_1(cls, v): #on class w el validated item eno y3ne el sha8le yali 3m a3mela validation
        if any(c < 0 or c > 1 for c in v):
            raise ValueError("color_rgb must be in [0,1]")
        return v

# ba3d na2es hone eno ensure el id is unique
# w kmn eno el class id ttwaza3 3a kl class