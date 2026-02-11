from dataclasses import dataclass

@dataclass
class PinholeCamera:
    width: int
    height: int #hole el image size in pixels
    fx: float
    fy: float #focal lengths
    cx: float
    cy: float #principal point

    #el input 3d point 
    #pixel coordinates w depth => output
    def project(self, xyz: tuple[float, float, float]) -> tuple[int, int, float] | None:
        x, y, z = xyz
        if z <= 0: #hay y3ne wara el camera
            return None

        u = self.fx * (x / z) + self.cx
        v = self.fy * (y / z) + self.cy

        return int(round(u)), int(round(v)), float(z) #round la2an el pixels discrete values
