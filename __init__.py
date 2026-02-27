_REQUIRED_PACKAGES = {
    "cv2": "opencv-python",
    "imageio": "imageio",
    "PyOpenColorIO": "opencolorio",
}

_missing = []
for _module, _pip_name in _REQUIRED_PACKAGES.items():
    try:
        __import__(_module)
    except ImportError:
        _missing.append(_pip_name)

if _missing:
    raise ImportError(
        f"[ComfyUI-HQ-Image-Save-Plus] Missing required packages: {', '.join(_missing)}. "
        f"Install them with:  pip install {' '.join(_missing)}"
    )

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
