import numpy as np
from config import DEPTH_INF

def depth_to_xyz(depth: np.ndarray, camera) -> np.ndarray:
    
    H, W = depth.shape
    u = np.arange(W, dtype=np.float32) #hole el pixels hk - w hk |
    v = np.arange(H, dtype=np.float32)
    uu, vv = np.meshgrid(u, v)  #shapes (H,W)
    z = depth.astype(np.float32)
    valid = z < (DEPTH_INF * 0.5) #bs threshold hay true iza belongs la object
    # reverse el projection yali 3mlneha
    x = (uu - camera.cx) * (z / camera.fx)
    y = (vv - camera.cy) * (z / camera.fy)

    xyz = np.stack([x, y, z], axis=-1)  # (H,W,3)
    xyz[~valid] = np.nan #mn2im el fake

    return xyz, valid
