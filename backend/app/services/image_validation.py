"""Bound image decoding before expensive forensic processing."""
import struct
import cv2
import numpy as np
from app.core.config import settings

class InvalidImage(ValueError):
    pass

class ImageTooLarge(InvalidImage):
    pass

def decode_image(content: bytes):
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise ImageTooLarge("Choose an image smaller than 20 MB.")
    if not content:
        raise InvalidImage("The image is empty.")
    # Inspect dimensions before OpenCV allocates a full raster. Pillow is a
    # runtime dependency, not just a fixture-generation dependency.
    from io import BytesIO
    from PIL import Image, UnidentifiedImageError
    try:
        with Image.open(BytesIO(content)) as image:
            if image.format not in {"PNG", "JPEG", "WEBP", "BMP"}:
                raise InvalidImage("Use a PNG, JPG, WebP, or BMP screenshot.")
            w, h = image.size
            if w * h > 12_000_000 or max(w, h) > 8192:
                raise ImageTooLarge("Use an image up to 12 megapixels and 8192 pixels per side.")
            if min(w, h) < 16:
                raise InvalidImage("The image must be at least 16 pixels on each side.")
            if getattr(image, "n_frames", 1) != 1:
                raise InvalidImage("Use a single-frame screenshot.")
            image.verify()
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ImageTooLarge("Image dimensions exceed the processing limit.") from exc
    except (UnidentifiedImageError, OSError, SyntaxError, struct.error) as exc:
        raise InvalidImage("Unsupported or corrupt image.") from exc
    image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImage("Unsupported or corrupt image.")
    return image
