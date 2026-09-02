"""EYERIS geospatial visual-intelligence and multimodal interaction core."""

from .contracts import BoundingBox, Camera, Detection, SceneObservation, make_detection
from .geospatial import enrich_detection
from .inference import Detector, MockDetector, run_inference
from .multimodal import (
    GazeSample,
    GazeSmoother,
    MultimodalIntentEngine,
    NormalizedPoint,
    SemanticCommand,
    SemanticTarget,
    TargetBounds,
    TargetRegistry,
)

__all__ = [
    "BoundingBox",
    "Camera",
    "Detection",
    "SceneObservation",
    "Detector",
    "MockDetector",
    "GazeSample",
    "GazeSmoother",
    "MultimodalIntentEngine",
    "NormalizedPoint",
    "SemanticCommand",
    "SemanticTarget",
    "TargetBounds",
    "TargetRegistry",
    "enrich_detection",
    "make_detection",
    "run_inference",
]

__version__ = "0.2.0"
