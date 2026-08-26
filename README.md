<div align="center">

# EYERIS // VA3LM GEOVISION

**Palantir Foundry-ready geospatial object and scene recognition for authorized visual inputs.**

`IMPLEMENTED` · `NON-IDENTIFYING` · `WGS84` · `FOUNDRY MODEL + ONTOLOGY`

</div>

![EYERIS system concept](docs/assets/sonoxo-system.svg)

## What exists now

EYERIS now contains working Python contracts for camera metadata, object/scene detections, confidence filtering, normalized bounding boxes, WGS84 geospatial enrichment, an optional Ultralytics-compatible detector adapter, a container-friendly live inference service, a Docker runtime, Foundry Media Set and geospatial transforms, a Foundry container ModelAdapter, an Ontology contract, automated tests, and cross-platform CI.

The implementation is designed to plug into the wider **GPT-GLASSONION / VA3LM / GPT-DOUG-LLM / ZYRA / XUNA / SONOXO** stack.

## Beginner flow

```text
AUTHORIZED CAMERA / IMAGE
        ↓
FOUNDRY MEDIA SET
        ↓
OBJECT + SCENE MODEL
        ↓
DETECTION
        ↓
CAMERA LAT/LONG + FIELD OF VIEW
        ↓
CAMERA + DETECTION ONTOLOGY
        ↓
MAP / WORKSHOP / OSDK
        ↓
REVIEWABLE EVIDENCE
```

## Code map

| Part | What it does |
|---|---|
| `src/eyeris/contracts.py` | Camera, Detection, bounding-box, timestamps, and privacy contracts |
| `src/eyeris/inference.py` | Standard detector interface and inference normalization |
| `src/eyeris/geospatial.py` | WGS84 camera-location enrichment |
| `src/eyeris/adapters/ultralytics_yolo.py` | Optional user-supplied object-detection weights |
| `src/eyeris/model_server.py` | `/health` + `/infer` container service |
| `Dockerfile.vision` | Linux container runtime for model hosting |
| `foundry/model_adapter/eyeris_container_adapter.py` | Palantir container-backed ModelAdapter |
| `foundry/pipelines/media_listing.py` | Media Set → image listing |
| `foundry/pipelines/geospatial_enrichment.py` | Camera metadata → geospatial detections |
| `foundry/ontology/eyeris-ontology.json` | Camera / Detection / review-action Ontology contract |
| `tests/test_geovision.py` | Reproducible core and privacy-boundary verification |

## Foundry architecture

Palantir models support imported container images plus model adapters for batch or live inference. The checked-in ModelAdapter maps Foundry tabular inputs to the EYERIS `/infer` service. Camera points are represented as Ontology `geopoint` values using WGS84 `latitude,longitude`; field-of-view geometry uses GeoJSON Geometry suitable for `geoshape`.

Full implementation notes: [docs/FOUNDry_GEOVISION.md](docs/FOUNDry_GEOVISION.md)

## Local verification

```bash
python -m pip install '.[dev]'
python -m pytest -q
python -m compileall -q src
```

Optional local object detector runtime:

```bash
python -m pip install '.[vision,server]'
export EYERIS_MODEL_PATH=/path/to/authorized/object-detection-weights.pt
uvicorn eyeris.model_server:app --host 0.0.0.0 --port 8080
```

## Privacy boundary

EYERIS is intentionally **non-identifying**. Generic object and scene labels are supported, including generic `person` detections. The core rejects identity-oriented payload fields such as face embeddings, identity IDs, person names, and persistent subject identifiers.

The intended uses are authorized asset/site awareness, object counts, vehicles, equipment, hazards, occupancy, and scene state — not covert identity surveillance.

## Status language

- **Implemented:** present in source code.
- **Verified:** exercised by reproducible tests/CI.
- **Foundry-ready:** code shape and adapter contracts exist for Foundry integration.
- **Deployed:** only after the target Foundry enrollment has actually run the model, transforms, Ontology, and app.

EYERIS is **implemented and CI-verified in GitHub**. A live Foundry deployment still requires the target enrollment, model resource, Media Set RIDs/paths, Ontology API names, and runtime credentials.
