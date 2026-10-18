from io import BytesIO
from pathlib import Path
import sys
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fashion-reco"))

from image_validation import (  # noqa: E402
    MAX_IMAGE_BYTES,
    ImageValidationError,
    decode_uploaded_image,
)


def make_image(image_format: str = "PNG", size: tuple[int, int] = (64, 64)) -> bytes:
    output = BytesIO()
    Image.new("RGB", size, color=(90, 40, 150)).save(output, format=image_format)
    return output.getvalue()


class ImageValidationTests(unittest.TestCase):
    def test_accepts_png_and_converts_to_rgb(self) -> None:
        image = decode_uploaded_image(make_image(), "image/png")
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (64, 64))

    def test_rejects_unsupported_content_type(self) -> None:
        with self.assertRaisesRegex(ImageValidationError, "JPEG, PNG, or WebP"):
            decode_uploaded_image(make_image(), "image/gif")

    def test_rejects_mismatched_content_type(self) -> None:
        with self.assertRaisesRegex(ImageValidationError, "do not match"):
            decode_uploaded_image(make_image("JPEG"), "image/png")

    def test_rejects_invalid_and_oversized_files(self) -> None:
        with self.assertRaisesRegex(ImageValidationError, "not a valid image"):
            decode_uploaded_image(b"not an image", "image/png")
        with self.assertRaisesRegex(ImageValidationError, "5 MB or smaller"):
            decode_uploaded_image(b"x" * (MAX_IMAGE_BYTES + 1), "image/png")

    def test_rejects_tiny_images(self) -> None:
        with self.assertRaisesRegex(ImageValidationError, "at least 32"):
            decode_uploaded_image(make_image(size=(16, 16)), "image/png")


if __name__ == "__main__":
    unittest.main()
