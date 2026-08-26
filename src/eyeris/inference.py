from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Protocol, Sequence

from .contracts import BoundingBox, Detection, make_detection, validate_non_identifying_payload


class Detector(Protocol):
    model_version: str

    def detect(self, image: Any) -> Sequence[dict[str, Any]]:
        """Return non-identifying object/scene detections for one image."""
        ...


@dataclass
class MockDetector:
    """Deterministic detector used for tests and local contract verification."""

    detections: Sequence[dict[str, Any]]
    model_version: str = "mock-1"

    def detect(self, image: Any) -> Sequence[dict[str, Any]]:
        del image
        return self.detections


def _bbox_from_result(result: dict[str, Any]) -> BoundingBox | None:
    raw = result.get("bbox")
    if raw is None:
        return None
    if not isinstance(raw, (list, tuple)) or len(raw) != 4:
        raise ValueError("bbox must be [x_min, y_min, x_max, y_max] in normalized coordinates")
    return BoundingBox(*(float(value) for value in raw))


def run_inference(
    *,
    detector: Detector,
    image: Any,
    camera_id: str,
    media_reference: str,
    minimum_confidence: float = 0.25,
) -> list[Detection]:
    if not 0.0 <= minimum_confidence <= 1.0:
        raise ValueError("minimum_confidence must be between 0 and 1")

    results: Iterable[dict[str, Any]] = detector.detect(image)
    detections: list[Detection] = []
    for result in results:
        validate_non_identifying_payload(result)
        confidence = float(result.get("confidence", 0.0))
        if confidence < minimum_confidence:
            continue
        label = str(result.get("class") or result.get("label") or "").strip()
        if not label:
            raise ValueError("Detector result is missing class/label")
        detections.append(
            make_detection(
                camera_id=camera_id,
                media_reference=media_reference,
                detected_class=label,
                confidence=confidence,
                model_version=detector.model_version,
                bounding_box=_bbox_from_result(result),
                observed_at=result.get("observed_at"),
            )
        )
    return detections
