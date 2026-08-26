"""Attach camera WGS84 coordinates and field-of-view geometry to model detections."""

from transforms.api import Input, Output, transform_df
from pyspark.sql import functions as F

RAW_DETECTIONS = "/Sonoxo/EYERIS/detections-raw"
CAMERA_METADATA = "/Sonoxo/EYERIS/cameras"
ENRICHED_DETECTIONS = "/Sonoxo/EYERIS/detections-geospatial"


@transform_df(
    Output(ENRICHED_DETECTIONS),
    detections=Input(RAW_DETECTIONS),
    cameras=Input(CAMERA_METADATA),
)
def compute(detections, cameras):
    camera_columns = cameras.select(
        F.col("cameraId").alias("cameraId"),
        F.col("latitude").alias("cameraLatitude"),
        F.col("longitude").alias("cameraLongitude"),
        F.col("fieldOfViewGeojson").alias("fieldOfViewGeojson"),
        F.col("status").alias("cameraStatus"),
    )

    return (
        detections.join(camera_columns, on="cameraId", how="left")
        .withColumn(
            "geopoint",
            F.concat_ws(",", F.col("cameraLatitude").cast("string"), F.col("cameraLongitude").cast("string")),
        )
        .withColumn("geoCrs", F.lit("WGS84"))
    )
