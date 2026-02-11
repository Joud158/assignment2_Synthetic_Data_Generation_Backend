""" ## Part 5 -- FastAPI Backend

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
``` """

import io
import os
import json

import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse

from api.state import STATE
from api.models import GenerateSceneRequest, ExportDatasetRequest

from scene.generator import generate_scene
from render.renderer import render_scene
from pointcloud.projection import depth_to_xyz
from pointcloud.ply_export import build_labeled_pointcloud, save_ply

from config import DEPTH_INF

app = FastAPI(title="Synthetic Data Backend")

def _png_bytes_uint8(img: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise RuntimeError("PNG encoding failed")
    return buf.tobytes()

def _png_bytes_mask16(mask: np.ndarray) -> bytes:
    mask16 = mask.astype(np.uint16)
    ok, buf = cv2.imencode(".png", mask16)
    if not ok:
        raise RuntimeError("PNG encoding failed")
    return buf.tobytes()

def _png_bytes_depth_vis(depth: np.ndarray) -> bytes:
    d = depth.copy()
    d[d >= DEPTH_INF * 0.5] = np.nan  # background
    mn = np.nanmin(d)
    mx = np.nanmax(d)
    vis = 255 * (d - mn) / (mx - mn + 1e-6)
    vis = np.nan_to_num(vis, nan=255).astype(np.uint8)
    ok, buf = cv2.imencode(".png", vis)
    if not ok:
        raise RuntimeError("PNG encoding failed")
    return buf.tobytes()

def _render():
    return render_scene(STATE.scene, STATE.camera)

@app.post("/scene/generate")
def generate_scene_api(req: GenerateSceneRequest):
    STATE.scene = generate_scene(num_objects=req.num_objects, seed=req.seed)
    return {"status": "ok", "num_objects": req.num_objects, "seed": req.seed}

@app.get("/scene/state")
def get_scene_state():
    return JSONResponse(STATE.scene.to_dict())

@app.post("/scene/reset")
def reset_scene():
    STATE.scene.reset()
    return {"status": "ok"}

@app.get("/render/rgb")
def render_rgb():
    out = _render()
    png = _png_bytes_uint8(out["rgb"])
    return StreamingResponse(io.BytesIO(png), media_type="image/png")

@app.get("/render/depth")
def render_depth():
    out = _render()
    png = _png_bytes_depth_vis(out["depth"])
    return StreamingResponse(io.BytesIO(png), media_type="image/png")

@app.get("/render/semantic")
def render_semantic():
    out = _render()
    png = _png_bytes_mask16(out["semantic"])
    return StreamingResponse(io.BytesIO(png), media_type="image/png")

@app.get("/render/instance")
def render_instance():
    out = _render()
    png = _png_bytes_mask16(out["instance"])
    return StreamingResponse(io.BytesIO(png), media_type="image/png")

@app.get("/pointcloud")
def pointcloud():
    out = _render()
    xyz, valid = depth_to_xyz(out["depth"], STATE.camera)
    pcd = build_labeled_pointcloud(xyz, out["rgb"], out["semantic"], out["instance"], valid)

    tmp_path = "tmp_cloud.ply"
    save_ply(pcd, tmp_path)
    with open(tmp_path, "rb") as f:
        data = f.read()

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": 'attachment; filename="cloud.ply"'},
    )

@app.post("/dataset/export")
def dataset_export(req: ExportDatasetRequest):
    os.makedirs(req.out_dir, exist_ok=True)
    index = []

    for i in range(req.num_scenes):
        seed_i = req.seed + i
        scene = generate_scene(req.num_objects, seed=seed_i)
        out = render_scene(scene, STATE.camera)

        base = f"scene_{i:05d}"
        rgb_path = os.path.join(req.out_dir, base + "_rgb.png")
        depth_path = os.path.join(req.out_dir, base + "_depth.png")
        sem_path = os.path.join(req.out_dir, base + "_semantic.png")
        ins_path = os.path.join(req.out_dir, base + "_instance.png")
        ply_path = os.path.join(req.out_dir, base + ".ply")
        json_path = os.path.join(req.out_dir, base + ".json")

        with open(rgb_path, "wb") as f: f.write(_png_bytes_uint8(out["rgb"]))
        with open(depth_path, "wb") as f: f.write(_png_bytes_depth_vis(out["depth"]))
        with open(sem_path, "wb") as f: f.write(_png_bytes_mask16(out["semantic"]))
        with open(ins_path, "wb") as f: f.write(_png_bytes_mask16(out["instance"]))

        xyz, valid = depth_to_xyz(out["depth"], STATE.camera)
        pcd = build_labeled_pointcloud(xyz, out["rgb"], out["semantic"], out["instance"], valid)
        save_ply(pcd, ply_path)

        record = {
            "id": base,
            "seed": seed_i,
            "scene": scene.to_dict(),
            "camera": {
                "width": STATE.camera.width,
                "height": STATE.camera.height,
                "fx": STATE.camera.fx,
                "fy": STATE.camera.fy,
                "cx": STATE.camera.cx,
                "cy": STATE.camera.cy,
            },
            "files": {
                "rgb": os.path.basename(rgb_path),
                "depth": os.path.basename(depth_path),
                "semantic": os.path.basename(sem_path),
                "instance": os.path.basename(ins_path),
                "pointcloud": os.path.basename(ply_path),
            }
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

        index.append(record)

    with open(os.path.join(req.out_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    return {"status": "ok", "out_dir": req.out_dir, "num_scenes": req.num_scenes}
