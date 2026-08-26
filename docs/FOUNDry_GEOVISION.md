# EYERIS / VA3LM Geospatial Vision on Foundry

EYERIS implements the Sonoxo ecosystem's **non-identifying object and scene recognition** contract for authorized camera/image inputs.

## Runtime flow

```text
AUTHORIZED CAMERA IMAGES
        |
        v
Foundry Media Set
        |
        v
transforms-media listing
        |
        v
Object / scene detector
(container-backed live deployment or batch model inference)
        |
        v
Detection dataset
        |
        v
Camera metadata join
(latitude + longitude + field-of-view)
        |
        v
Camera + Detection Ontology objects
        |
        v
Map / Workshop / OSDK operational app
        |
        v
VA3LM evidence
```

## Checked-in implementation

- `src/eyeris/contracts.py` — Camera, Detection, bounding-box, evidence, and privacy contracts.
- `src/eyeris/inference.py` — detector interface and inference normalization.
- `src/eyeris/adapters/ultralytics_yolo.py` — optional object-detection adapter for user-supplied weights.
- `src/eyeris/model_server.py` — container-friendly `/health` and `/infer` API.
- `foundry/pipelines/media_listing.py` — Media Set → tabular listing transform.
- `foundry/pipelines/geospatial_enrichment.py` — camera metadata → WGS84 `geopoint` enrichment.
- `foundry/ontology/eyeris-ontology.json` — Camera / Detection Ontology contract.

## Palantir product split

Palantir's August 2026 SuperRepo beta can colocate Ontology definitions, TypeScript functions, and React apps. Its announcement also states that **external sources and data pipelines are not yet available inside SuperRepo**. Therefore EYERIS keeps camera ingestion and media/model pipelines in a Foundry Code Repository / model deployment, while the operational Ontology and application can be represented by a SuperRepo.

This separation is deliberate; it avoids pretending that current SuperRepo beta supports external camera ingestion directly.

## Geospatial types

- Camera point: Ontology `geopoint` formatted `latitude,longitude` in WGS84.
- Camera field of view: Ontology `geoshape` containing GeoJSON Geometry.
- Detection location: inherited from the originating camera unless a more precise sensor-derived point exists.

## Model deployment choices

1. **Batch:** run large-scale inference in Python transforms or Pipeline Builder using a Foundry model.
2. **Live:** package object-detection weights in a container-backed model and expose inference through a Foundry live deployment.

`Dockerfile.vision` supplies a concrete container runtime contract. Palantir does not mandate a standard container HTTP API; the target enrollment's model adapter must map Foundry requests to EYERIS `/infer`.

## Privacy boundary hard-coded in code

EYERIS accepts generic object and scene labels, including generic `person` detections. It rejects payload fields used for biometric or named-person identification, including face embeddings, identity IDs, person names, and persistent subject identifiers.

The system is designed for authorized operational imagery, asset/site awareness, occupancy/object counts, vehicles, hazards, equipment, and scene state — not covert identity surveillance.
