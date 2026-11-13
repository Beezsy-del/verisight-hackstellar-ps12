import io
from typing import Any

import exifread
from PIL import Image
from PIL.ExifTags import TAGS


def inspect_image_metadata(
    image_bytes: bytes,
    filename: str = "screenshot.png"
) -> dict[str, Any]:
    """
    Examines container chunks, EXIF metadata, PNG chunks, and software tags.
    """
    metadata_info = {
        "format": "UNKNOWN",
        "has_exif": False,
        "exif_tags_count": 0,
        "software": None,
        "creation_time": None,
        "icc_profile": None,
        "png_chunks": [],
        "c2pa_marker_found": False
    }

    # 1. Check for C2PA marker in raw bytes
    # C2PA embeds in JPEG/PNG via JUMBF box (marker 'jumbf' or 'c2pa')
    if b'jumbf' in image_bytes or b'c2pa' in image_bytes:
        metadata_info["c2pa_marker_found"] = True

    # 2. Pillow inspection
    try:
        with Image.open(io.BytesIO(image_bytes)) as pil_img:
            metadata_info["format"] = pil_img.format or "UNKNOWN"
            
            # Check ICC profile
            icc = pil_img.info.get('icc_profile')
            if icc:
                metadata_info["icc_profile"] = "Embedded Profile Present"

            # Check PNG textual chunks
            if pil_img.format == 'PNG':
                for k, v in pil_img.info.items():
                    if k not in ('icc_profile', 'dpi'):
                        metadata_info["png_chunks"].append(f"{k}: {v}")
                        if 'software' in k.lower():
                            metadata_info["software"] = str(v)

            # Check EXIF via Pillow
            exif_data = pil_img.getexif()
            if exif_data and len(exif_data) > 0:
                metadata_info["has_exif"] = True
                metadata_info["exif_tags_count"] = len(exif_data)
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == 'Software':
                        metadata_info["software"] = str(value)
                    elif tag_name in ('DateTime', 'DateTimeOriginal'):
                        metadata_info["creation_time"] = str(value)
    except Exception:
        pass

    # 3. ExifRead secondary verification
    try:
        tags = exifread.process_file(io.BytesIO(image_bytes), details=False)
        if tags and len(tags) > 0:
            metadata_info["has_exif"] = True
            metadata_info["exif_tags_count"] = max(metadata_info["exif_tags_count"], len(tags))
            if 'Image Software' in tags:
                metadata_info["software"] = str(tags['Image Software'])
            if 'Image DateTime' in tags and not metadata_info["creation_time"]:
                metadata_info["creation_time"] = str(tags['Image DateTime'])
    except Exception:
        pass

    # 4. Detect known generator signatures
    known_generators = ['FakeGen', 'FakeReceipt', 'HTML2Canvas', 'CanvasCapture', 'Photoshop', 'Canva', 'GIMP', 'Figma']
    sw = metadata_info.get("software") or ""
    for gen in known_generators:
        if gen.lower() in sw.lower():
            metadata_info["software_signature"] = gen
            break

    return metadata_info
