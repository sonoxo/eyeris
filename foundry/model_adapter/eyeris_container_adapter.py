"""Palantir Foundry container-backed ModelAdapter for EYERIS.

Author this file in a Foundry Model Adapter Library repository or package it as the
adapter library selected for the EYERIS container-backed model version.
"""

from __future__ import annotations

import pandas as pd
import palantir_models as pm
import requests


class EyerisContainerAdapter(pm.ContainerModelAdapter):
    """
    :display-name: EYERIS Non-Identifying GeoVision Adapter
    :description: Sends authorized image references to the EYERIS object/scene detector container.
    """

    def __init__(self, shared_volume_path: str, model_host_and_port: str):
        self.shared_volume_path = shared_volume_path
        self.model_host_and_port = model_host_and_port

    @classmethod
    def init_container(cls, container_context):
        shared_volume_path = container_context.shared_empty_dir_mount_path
        services = list(container_context.services.values())
        if not services or not services[0]:
            raise RuntimeError("EYERIS container exposes no service URI")
        return cls(shared_volume_path, services[0][0])

    @classmethod
    def api(cls):
        inputs = {
            "input_df": pm.Pandas(
                columns=[
                    ("image", str),
                    ("cameraId", str),
                    ("mediaReference", str),
                    ("minimumConfidence", float),
                ]
            )
        }
        outputs = {
            "output_df": pm.Pandas(
                columns=[
                    ("detectionId", str),
                    ("cameraId", str),
                    ("mediaReference", str),
                    ("detectedClass", str),
                    ("confidence", float),
                    ("observedAt", str),
                    ("modelVersion", str),
                    ("boundingBoxJson", str),
                ]
            )
        }
        return inputs, outputs

    def predict(self, input_df):
        records = []
        endpoint = "http://" + self.model_host_and_port + "/infer"
        for row in input_df.itertuples(index=False):
            payload = {
                "image": row.image,
                "camera_id": row.cameraId,
                "media_reference": row.mediaReference,
                "minimum_confidence": row.minimumConfidence,
            }
            response = requests.post(endpoint, json=payload, timeout=60)
            response.raise_for_status()
            body = response.json()
            for detection in body.get("detections", []):
                records.append(
                    {
                        "detectionId": detection["detection_id"],
                        "cameraId": detection["camera_id"],
                        "mediaReference": detection["media_reference"],
                        "detectedClass": detection["detected_class"],
                        "confidence": float(detection["confidence"]),
                        "observedAt": detection["observed_at"],
                        "modelVersion": detection["model_version"],
                        "boundingBoxJson": pd.io.json.dumps(detection.get("bounding_box")),
                    }
                )
        return pd.DataFrame(records)
