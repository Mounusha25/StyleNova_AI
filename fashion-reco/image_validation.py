"""Validation utilities for user-uploaded fashion images."""

from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}


class ImageValidationError(ValueError):
    """An uploaded file is not a safe, supported image."""


def decode_uploaded_image(data: bytes, content_type: str | None) -> Image.Image:
    """Validate an uploaded image and return a detached RGB PIL image."""

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ImageValidationError("Upload a JPEG, PNG, or WebP image.")
    if not data:
        raise ImageValidationError("The uploaded image is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise ImageValidationError("The uploaded image must be 5 MB or smaller.")

    try:
        with Image.open(BytesIO(data)) as candidate:
            detected_format = candidate.format
            if candidate.width * candidate.height > MAX_IMAGE_PIXELS:
                raise ImageValidationError("The image exceeds the 25-megapixel safety limit.")
            candidate.verify()

        expected_format = ALLOWED_IMAGE_TYPES[content_type]
        if detected_format != expected_format:
            raise ImageValidationError(
                "The file contents do not match the declared image type."
            )

        with Image.open(BytesIO(data)) as candidate:
            candidate.load()
            if candidate.width < 32 or candidate.height < 32:
                raise ImageValidationError("The image must be at least 32×32 pixels.")
            return candidate.convert("RGB").copy()
    except ImageValidationError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ImageValidationError("The uploaded file is not a valid image.") from exc
