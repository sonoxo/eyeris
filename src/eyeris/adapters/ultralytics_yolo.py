from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence


class UltralyticsYoloDetector:
    """Optional adapter for user-supplied Ultralytics-compatible object-detection weights.

    The adapter emits class labels, confidence, and normalized bounding boxes only.
    It deliberately does not expose face embeddings, identity lookup, or persistent
    individual tracking.
    """

    def __init__(self, model_path: str | Path, *, model_version: str | None = None) -> None:
        try:
            from ultralytics import YOLO
        except ImportError as exc:  # pragma: no cover - exercised only with vision extra installed
            raise RuntimeError("Install EYERIS with the 'vision' extra to use Ultralytics YOLO") from exc

        self._model = YOLO(str(model_path))
        self.model_version = model_version or Path(model_path).name

    def detect(self, image: Any) -> Sequence[dict[str, Any]]:
        outputs = self._model.predict(source=image, verbose=False)
        detections: list[dict[str, Any]] = []
        for output in outputs:
            names = output.names
            boxes = output.boxes
            if boxes is None:
                continue
            image_height, image_width = output.orig_shape
            for xyxy, confidence, class_id in zip(boxes.xyxy.tolist(), boxes.conf.tolist(), boxes.cls.tolist()):
                x_min, y_min, x_max, y_max = xyxy
                detections.append(
                    {
                        "class": str(names[int(class_id)]),
                        "confidence": float(confidence),
                        "bbox": [
                            max(0.0, min(1.0, x_min / image_width)),
                            max(0.0, min(1.0, y_min / image_height)),
                            max(0.0, min(1.0, x_max / image_width)),
                            max(0.0, min(1.0, y_max / image_height)),
                        ],
                    }
                )
        return detections
