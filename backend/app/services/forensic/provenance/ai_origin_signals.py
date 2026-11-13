"""Collect narrow, explainable AI-origin evidence without classifying the image.

Metadata strings are self-reported and can be edited or stripped. Pixel
forensics in this app are generic manipulation cues, not an AI-origin detector.
"""

from __future__ import annotations

import re
from typing import Any


_AI_TOOL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("OpenAI / DALL-E", re.compile(r"\b(?:openai|dall[\s_-]*e)\b", re.IGNORECASE)),
    ("Midjourney", re.compile(r"\bmidjourney\b", re.IGNORECASE)),
    ("Stable Diffusion", re.compile(r"\bstable[\s_-]*diffusion\b", re.IGNORECASE)),
    ("ComfyUI", re.compile(r"\bcomfyui\b", re.IGNORECASE)),
    ("AUTOMATIC1111", re.compile(r"\bautomatic1111\b", re.IGNORECASE)),
    ("NovelAI", re.compile(r"\bnovelai\b", re.IGNORECASE)),
    ("Adobe Firefly", re.compile(r"\b(?:adobe[\s_-]*)?firefly\b", re.IGNORECASE)),
    ("Google Imagen / Gemini", re.compile(r"\b(?:imagen|gemini)\b", re.IGNORECASE)),
    ("FLUX", re.compile(r"\bflux(?:[\s._-]*1)?\b", re.IGNORECASE)),
    ("Ideogram", re.compile(r"\bideogram\b", re.IGNORECASE)),
    ("Leonardo AI", re.compile(r"\bleonardo(?:[\s._-]*ai)?\b", re.IGNORECASE)),
    ("Fooocus", re.compile(r"\bfooocus\b", re.IGNORECASE)),
    ("InvokeAI", re.compile(r"\binvokeai\b", re.IGNORECASE)),
    ("Runway", re.compile(r"\brunway(?:ml)?\b", re.IGNORECASE)),
)


def _png_metadata_text(image_bytes: bytes) -> list[str]:
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return []

    texts: list[str] = []
    offset = 8
    while offset + 12 <= len(image_bytes):
        length = int.from_bytes(image_bytes[offset : offset + 4], "big")
        kind = image_bytes[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        if data_end + 4 > len(image_bytes):
            break
        if kind in (b"tEXt", b"iTXt", b"zTXt"):
            # Limit work on malformed or unusually large ancillary chunks.
            texts.append(image_bytes[data_start : min(data_end, data_start + 8192)].decode("latin1", "ignore"))
        offset = data_end + 4  # include the chunk CRC
        if kind == b"IEND":
            break
    return texts


def _jpeg_metadata_text(image_bytes: bytes) -> list[str]:
    if not image_bytes.startswith(b"\xff\xd8"):
        return []

    texts: list[str] = []
    offset = 2
    while offset + 4 <= len(image_bytes) and image_bytes[offset] == 0xFF:
        marker = image_bytes[offset + 1]
        length = int.from_bytes(image_bytes[offset + 2 : offset + 4], "big")
        if length < 2:
            break
        start = offset + 4
        end = offset + 2 + length
        if end > len(image_bytes):
            break
        segment = image_bytes[start:end]

        if marker == 0xE1:
            if segment.startswith(b"Exif\x00\x00"):
                texts.extend(_exif_text_values(segment[6:]))
            elif segment.startswith(b"http://ns.adobe.com/xap/1.0/\x00"):
                xmp = segment.split(b"\x00", 1)[1][:65536].decode("utf-8", "ignore")
                # Read only conventional software/creator fields, not arbitrary XMP.
                for match in re.findall(
                    r"(?:CreatorTool|Software|Generator|HistorySoftwareAgent)[^>]{0,48}>\s*([^<]{1,256})<",
                    xmp,
                    flags=re.IGNORECASE,
                ):
                    texts.append(match)

        offset = end
        if marker == 0xDA:  # start of compressed image data
            break
    return texts


def _exif_text_values(tiff: bytes) -> list[str]:
    """Read the common ASCII EXIF Software and ImageDescription fields."""
    if len(tiff) < 8:
        return []
    byte_order = tiff[:2]
    if byte_order == b"II":
        endian = "little"
    elif byte_order == b"MM":
        endian = "big"
    else:
        return []

    def u16(position: int) -> int:
        return int.from_bytes(tiff[position : position + 2], endian)

    def u32(position: int) -> int:
        return int.from_bytes(tiff[position : position + 4], endian)

    try:
        if u16(2) != 42:
            return []
        ifd_offset = u32(4)
        if ifd_offset + 2 > len(tiff):
            return []
        count = min(u16(ifd_offset), 1024)
        values: list[str] = []
        for index in range(count):
            entry = ifd_offset + 2 + index * 12
            if entry + 12 > len(tiff):
                break
            tag = u16(entry)
            field_type = u16(entry + 2)
            value_count = u32(entry + 4)
            if tag not in (0x010E, 0x0131) or field_type != 2 or value_count == 0:
                continue
            value_offset = entry + 8 if value_count <= 4 else u32(entry + 8)
            if value_offset + value_count > len(tiff):
                continue
            values.append(tiff[value_offset : value_offset + min(value_count, 8192)].split(b"\x00", 1)[0].decode("utf-8", "ignore"))
        return values
    except (IndexError, OverflowError, ValueError):
        return []


def _metadata_tool_match(image_bytes: bytes, metadata_info: dict[str, Any]) -> str | None:
    metadata_strings = _png_metadata_text(image_bytes) + _jpeg_metadata_text(image_bytes)
    software = metadata_info.get("software")
    if isinstance(software, str):
        metadata_strings.append(software)
    png_chunks = metadata_info.get("png_chunks", [])
    if isinstance(png_chunks, list):
        metadata_strings.extend(item for item in png_chunks if isinstance(item, str))

    for tool_name, pattern in _AI_TOOL_PATTERNS:
        if any(pattern.search(value) for value in metadata_strings):
            return tool_name
    return None


def inspect_ai_origin_signals(
    image_bytes: bytes,
    metadata_info: dict[str, Any],
    *,
    c2pa_present: bool,
    c2pa_status: str,
    generic_pixel_cue_count: int,
) -> dict[str, Any]:
    """Return per-signal states; deliberately never returns an AI verdict."""
    tool_match = _metadata_tool_match(image_bytes, metadata_info)
    marker_is_unverified = c2pa_present or c2pa_status == "MANIFEST_PRESENT_UNVERIFIED"

    return {
        "classifier_available": False,
        "summary": "This signal panel does not classify an image as AI-generated or human-created.",
        "signals": [
            {
                "id": "generator_metadata",
                "label": "AI generator name in metadata",
                "status": "DETECTED" if tool_match else "NOT_DETECTED",
                "evidence": (
                    f"Readable image metadata contains the name {tool_match}."
                    if tool_match
                    else "No supported AI generator name was found in readable metadata."
                ),
                "limitation": "Metadata is self-reported; it can be forged, changed, or removed.",
            },
            {
                "id": "c2pa_provenance",
                "label": "C2PA / Content Credentials",
                "status": "UNVERIFIED" if marker_is_unverified else "NOT_DETECTED",
                "evidence": (
                    "A C2PA-related marker is present, but this deployment does not validate the manifest signature or asset binding."
                    if marker_is_unverified
                    else "No C2PA-related marker was found."
                ),
                "limitation": "A marker is not a verified credential; no marker does not establish human origin.",
            },
            {
                "id": "visible_ai_mark",
                "label": "Visible AI logo or watermark",
                "status": "NOT_CHECKED",
                "evidence": "No dedicated logo, corner-watermark, or SynthID detector is configured.",
                "limitation": "Visible marks can be cropped or removed; this app does not send images to external detectors.",
            },
            {
                "id": "source_layers",
                "label": "Native editing-layer structure",
                "status": "NOT_CHECKED",
                "evidence": "The analyzer reads flattened PNG, JPEG, WebP, and BMP images; it does not inspect PSD or editing-project layers.",
                "limitation": "An exported screenshot does not preserve the source document's editable layer history.",
            },
            {
                "id": "generic_pixel_cues",
                "label": "Generic pixel / noise review cues",
                "status": "DETECTED" if generic_pixel_cue_count else "NOT_DETECTED",
                "evidence": (
                    f"{generic_pixel_cue_count} region cue(s) came from existing compression, noise, or copy-move checks."
                    if generic_pixel_cue_count
                    else "No region cues were produced by the current compression, noise, or copy-move checks."
                ),
                "limitation": "These cues are not AI-specific and cannot distinguish generated images from camera images.",
            },
            {
                "id": "ai_origin_classifier",
                "label": "Calibrated AI-origin classifier",
                "status": "NOT_AVAILABLE",
                "evidence": "No authorized, representative, independently evaluated AI-origin model is deployed.",
                "limitation": "No overall AI-generated versus human-created conclusion or confidence is available.",
            },
        ],
    }
