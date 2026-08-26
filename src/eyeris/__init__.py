"""EYERIS geospatial visual-intelligence core."""

from .contracts import BoundingBox, Camera, Detection, SceneObservation, make_detection
from .geospatial import enrich_detection
from .inference import Detector, MockDetector, run_inference

__all__ = [
    "BoundingBox",
    "Camera",
    "Detection",
    "SceneObservation",
    "Detector",
    "MockDetector",
    "enrich_detection",
    "make_detection",
    "run_inference",
]

__version__ = "0.1.0"
