import json
import pytest

from eyeris import BoundingBox, Camera, MockDetector, enrich_detection, run_inference
from eyeris.contracts import validate_non_identifying_payload


def test_camera_geopoint_and_geoshape_validation():
    camera = Camera(
        camera_id="cam-rva-001",
        label="Authorized test camera",
        latitude=37.5407,
        longitude=-77.4360,
        field_of_view_geojson=json.dumps(
            {
                "type": "Polygon",
                "coordinates": [[[-77.4361, 37.5406], [-77.4359, 37.5406], [-77.4359, 37.5408], [-77.4361, 37.5406]]],
            }
        ),
    )
    assert camera.geopoint == "37.5407000,-77.4360000"


def test_inference_filters_low_confidence_and_enriches_location():
    detector = MockDetector(
        [
            {"class": "vehicle", "confidence": 0.94, "bbox": [0.1, 0.2, 0.7, 0.8], "observed_at": "2026-08-26T20:00:00Z"},
            {"class": "person", "confidence": 0.10, "bbox": [0.2, 0.2, 0.4, 0.6], "observed_at": "2026-08-26T20:00:00Z"},
        ],
        model_version="contract-test",
    )
    detections = run_inference(
        detector=detector,
        image=b"fake-image",
        camera_id="cam-rva-001",
        media_reference="ri.media.example",
        minimum_confidence=0.25,
    )
    assert [item.detected_class for item in detections] == ["vehicle"]
    assert detections[0].bounding_box == BoundingBox(0.1, 0.2, 0.7, 0.8)

    camera = Camera("cam-rva-001", "Authorized test camera", 37.5407, -77.4360)
    enriched = enrich_detection(detections[0], camera)
    assert enriched.geopoint == "37.5407000,-77.4360000"


def test_identity_fields_are_rejected_recursively():
    with pytest.raises(ValueError, match="Identity field"):
        validate_non_identifying_payload(
            {"class": "person", "confidence": 0.9, "metadata": {"face_embedding": [0.1, 0.2]}}
        )


def test_invalid_bbox_rejected():
    with pytest.raises(ValueError):
        BoundingBox(-0.1, 0.0, 1.0, 1.0)
