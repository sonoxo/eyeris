from __future__ import annotations

from dataclasses import replace

from .contracts import Camera, Detection


def enrich_detection(detection: Detection, camera: Camera) -> Detection:
    if detection.camera_id != camera.camera_id:
        raise ValueError("Detection camera_id does not match camera metadata")
    return replace(
        detection,
        geopoint=camera.geopoint,
        field_of_view_geojson=camera.field_of_view_geojson,
    )


def enrich_many(detections: list[Detection], cameras: dict[str, Camera]) -> list[Detection]:
    enriched: list[Detection] = []
    for detection in detections:
        camera = cameras.get(detection.camera_id)
        if camera is None:
            raise KeyError(f"Missing camera metadata for {detection.camera_id}")
        enriched.append(enrich_detection(detection, camera))
    return enriched
