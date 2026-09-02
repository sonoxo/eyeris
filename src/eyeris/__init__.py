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
from .runtime import (
    ActionReceipt,
    DefaultPolicyGate,
    EyerisRuntime,
    InMemoryActionAdapter,
    InteractionFrame,
    InteractionResult,
    PolicyDecision,
)

__all__ = [
    "ActionReceipt",
    "BoundingBox",
    "Camera",
    "DefaultPolicyGate",
    "Detection",
    "Detector",
    "EyerisRuntime",
    "GazeSample",
    "GazeSmoother",
    "InMemoryActionAdapter",
    "InteractionFrame",
    "InteractionResult",
    "MockDetector",
    "MultimodalIntentEngine",
    "NormalizedPoint",
    "PolicyDecision",
    "SceneObservation",
    "SemanticCommand",
    "SemanticTarget",
    "TargetBounds",
    "TargetRegistry",
    "enrich_detection",
    "make_detection",
    "run_inference",
]

__version__ = "0.3.0"
