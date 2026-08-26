from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .adapters import UltralyticsYoloDetector
from .inference import run_inference


def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install EYERIS with the 'server' extra to run the model service") from exc

    model_path = os.environ.get("EYERIS_MODEL_PATH")
    if not model_path:
        raise RuntimeError("EYERIS_MODEL_PATH must point to authorized object-detection weights")

    detector = UltralyticsYoloDetector(Path(model_path), model_version=os.environ.get("EYERIS_MODEL_VERSION"))
    app = FastAPI(title="EYERIS non-identifying object recognition", version="0.1.0")

    class InferenceRequest(BaseModel):
        image: str
        camera_id: str
        media_reference: str
        minimum_confidence: float = 0.25

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "ok": True,
            "mode": "NON_IDENTIFYING_OBJECT_SCENE_RECOGNITION",
            "modelVersion": detector.model_version,
        }

    @app.post("/infer")
    def infer(request: InferenceRequest) -> dict[str, Any]:
        try:
            detections = run_inference(
                detector=detector,
                image=request.image,
                camera_id=request.camera_id,
                media_reference=request.media_reference,
                minimum_confidence=request.minimum_confidence,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "mode": "NON_IDENTIFYING_OBJECT_SCENE_RECOGNITION",
            "detections": [detection.as_record() for detection in detections],
        }

    return app


app = create_app()
