from pydantic import BaseModel, Field

class GenerateSceneRequest(BaseModel):
    num_objects: int = Field(default=10, ge=1, le=200)
    seed: int = Field(default=42)

class ExportDatasetRequest(BaseModel):
    num_scenes: int = Field(default=20, ge=1, le=1000)
    num_objects: int = Field(default=10, ge=1, le=200)
    seed: int = Field(default=0)
    out_dir: str = Field(default="dataset_out")
