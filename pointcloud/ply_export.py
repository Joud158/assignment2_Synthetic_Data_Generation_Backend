""" ## Part 4 -- Point Cloud Generation

From the depth map, generate a labeled point cloud **in the camera frame**:

* Reconstruct XYZ points by back-projecting each pixel using the camera intrinsics
* The resulting 3D coordinates are expressed in the camera's coordinate frame
* Attach RGB color from the rendered color image
* Attach semantic and instance labels from the segmentation masks
* Export as `.ply` using Open3D

--- """

import numpy as np
import open3d as o3d

def build_labeled_pointcloud(xyz: np.ndarray, rgb: np.ndarray, semantic: np.ndarray, instance: np.ndarray, valid: np.ndarray) -> o3d.geometry.PointCloud:

    pts = xyz[valid].reshape(-1, 3).astype(np.float32)
    cols = (rgb[valid].reshape(-1, 3).astype(np.float32)) / 255.0

    sem = semantic[valid].reshape(-1).astype(np.int32)
    ins = instance[valid].reshape(-1).astype(np.int32)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)
    pcd.colors = o3d.utility.Vector3dVector(cols)

    # attach labels hone
    pcd.point["semantic"] = o3d.utility.IntVector(sem.tolist())
    pcd.point["instance"] = o3d.utility.IntVector(ins.tolist())

    return pcd

def save_ply(pcd: o3d.geometry.PointCloud, path: str) -> None:
    o3d.io.write_point_cloud(path, pcd, write_ascii=False)
