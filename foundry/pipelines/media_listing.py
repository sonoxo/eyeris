"""Foundry Code Repository transform for EYERIS camera-image Media Sets.

This module follows Palantir's documented transforms-media pattern. It is meant to
run inside a Foundry Python transforms repository where `transforms-media` is
installed. Media Set transforms can be built but are not previewed in Code Repos.
"""

from transforms.api import Output, transform
from transforms.mediasets import LightweightMediaSetInputParam, MediaSetInput

CAMERA_MEDIA_SET = "/Sonoxo/EYERIS/camera-images"
IMAGE_LISTING_DATASET = "/Sonoxo/EYERIS/image-listing"


@transform.using(
    images=MediaSetInput(CAMERA_MEDIA_SET),
    listing_output=Output(IMAGE_LISTING_DATASET),
)
def compute(images: LightweightMediaSetInputParam, listing_output):
    media_items = images.list_media_items_by_path_with_media_reference().pandas()
    listing_output.write_table(media_items)
