from scene.scene import Scene
from render.camera import PinholeCamera
from config import IMG_W, IMG_H, FX, FY, CX, CY

class AppState:
    def __init__(self):
        self.scene = Scene()
        self.camera = PinholeCamera(width=IMG_W, height=IMG_H, fx=FX, fy=FY, cx=CX, cy=CY)

STATE = AppState()
