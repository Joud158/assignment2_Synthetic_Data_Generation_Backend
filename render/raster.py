import numpy as np

def clip_box(x0, y0, x1, y1, w, h):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(w - 1, x1)
    y1 = min(h - 1, y1)
    return x0, y0, x1, y1

def raster_circle(u: int, v: int, r: int, w: int, h: int): #center (u,v) radius r
    if r <= 0:
        return None
    x0, y0, x1, y1 = clip_box(u - r, v - r, u + r, v + r, w, h)
    yy, xx = np.ogrid[y0:y1+1, x0:x1+1] #kl el pixels bl bounding boxe
    mask = (xx - u) ** 2 + (yy - v) ** 2 <= r ** 2 #equation of circle
    return (slice(y0, y1+1), slice(x0, x1+1), mask) #bs mne5od el sha2fe yali fiha

def raster_rect(u: int, v: int, half: int, w: int, h: int):
    if half <= 0:
        return None
    x0, y0, x1, y1 = clip_box(u - half, v - half, u + half, v + half, w, h)
    mask = np.ones((y1 - y0 + 1, x1 - x0 + 1), dtype=bool)
    return (slice(y0, y1+1), slice(x0, x1+1), mask)

def raster_ellipse(u: int, v: int, rx: int, ry: int, w: int, h: int):
    if rx <= 0 or ry <= 0:
        return None
    x0, y0, x1, y1 = clip_box(u - rx, v - ry, u + rx, v + ry, w, h)
    yy, xx = np.ogrid[y0:y1+1, x0:x1+1]
    mask = ((xx - u) / rx) ** 2 + ((yy - v) / ry) ** 2 <= 1.0
    return (slice(y0, y1+1), slice(x0, x1+1), mask)
