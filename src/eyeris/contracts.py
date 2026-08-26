from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Mapping

# EYERIS is intentionally non-identifying. Generic object/scene detection is allowed;
# biometric recognition, named-person lookup, and persistent individual tracking are not.
FORBIDDEN_IDENTITY_KEYS = {
    "biometric",
    "biometric_embedding",
    "face_embedding",
    "face_id",
    "identity",
    "identity_id",
    "person_id",
    "person_name",
    "subject_id",
    "subject_name",
}


@dataclass(frozen=True)
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def __post_init__(self) -> None:
        values = (self.x_min, self.y_min, self.x_max, self.y_max)
        if any(value < 0.0 or value > 1.0 for value in values):
            raise ValueError("Bounding-box coordinates must be normalized between 0 and 1")
        if self.x_min > self.x_max or self.y_min > self.y_max:
            raise ValueError("Bounding-box minimums must be <= maximums")


@dataclass(frozen=True)
class Camera:
    camera_id: str
    label: str
    latitude: float
    longitude: float
    status: str = "ACTIVE"
    field_of_view_geojson: str | None = None

    def __post_init__(self) -> None:
        if not self.camera_id.strip():
            raise ValueError("camera_id is required")
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")
        if self.field_of_view_geojson:
            geometry = json.loads(self.field_of_view_geojson)
            if geometry.get("type") in {"Feature", "FeatureCollection", "GeometryCollection"}:
                raise ValueError("field_of_view_geojson must be a GeoJSON Geometry, not a Feature wrapper")

    @property
    def geopoint(self) -> str:
        return f"{self.latitude:.7f},{self.longitude:.7f}"


@dataclass(frozen=True)
class Detection:
    detection_id: str
    camera_id: str
    media_reference: str
    detected_class: str
    confidence: float
    observed_at: str
    model_version: str
    bounding_box: BoundingBox | None = None
    geopoint: str | None = None
    field_of_view_geojson: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.detected_class.strip():
            raise ValueError("detected_class is required")

    def as_record(self) -> dict[str, Any]:
        record = asdict(self)
        return {key: value for key, value in record.items() if value is not None}


@dataclass(frozen=True)
class SceneObservation:
    camera_id: str
    media_reference: str
    scene_tags: tuple[str, ...]
    observed_at: str
    model_version: str
    geopoint: str | None = None


def _scan_for_identity_fields(value: Any, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_IDENTITY_KEYS:
                raise ValueError(f"Identity field is not permitted in EYERIS non-identifying mode: {path}.{key}")
            _scan_for_identity_fields(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_for_identity_fields(nested, f"{path}[{index}]")


def validate_non_identifying_payload(payload: Mapping[str, Any]) -> None:
    _scan_for_identity_fields(payload)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_detection(
    *,
    camera_id: str,
    media_reference: str,
    detected_class: str,
    confidence: float,
    model_version: str,
    bounding_box: BoundingBox | None = None,
    observed_at: str | None = None,
) -> Detection:
    timestamp = observed_at or utc_now_iso()
    identity_source = "|".join(
        [
            camera_id,
            media_reference,
            detected_class,
            timestamp,
            repr(bounding_box),
        ]
    )
    detection_id = sha256(identity_source.encode("utf-8")).hexdigest()[:24]
    return Detection(
        detection_id=detection_id,
        camera_id=camera_id,
        media_reference=media_reference,
        detected_class=detected_class,
        confidence=float(confidence),
        observed_at=timestamp,
        model_version=model_version,
        bounding_box=bounding_box,
    )
