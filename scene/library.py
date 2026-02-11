""" Define a **class library** (`library.py`) that maps class IDs to shape names and semantic visualization colors. For example:
- Class ID 1 → `"sphere"` with red semantic color
- Class ID 2 → `"cube"` with green semantic color
- Class ID 3 → `"cylinder"` with blue semantic color

**Important:** The shape determines the class (not independent). When generating objects, pick a class_id which determines the shape. The semantic visualization uses these colors, but the RGB rendering should use random colors per instance to create visual variety. """

# okok so hone 3m na3ml el assignment lal class id la shape names 
# ok so basically hole el colors hine lamma mna3ml el semantic segmentation

CLASS_LIBRARY = {
    1: {"shape": "sphere",   "semantic_color": (1.0, 0.0, 0.0)},  # red as in RGB
    2: {"shape": "cube",     "semantic_color": (0.0, 1.0, 0.0)},  # green as in RGB
    3: {"shape": "cylinder", "semantic_color": (0.0, 0.0, 1.0)},  # blue kmn as in RGB
}

VALID_CLASS_IDS = set(CLASS_LIBRARY.keys())
