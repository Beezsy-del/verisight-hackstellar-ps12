from app.services.forensic.provenance.ai_origin_signals import inspect_ai_origin_signals


def _png_text_chunk(keyword: bytes, value: bytes) -> bytes:
    data = keyword + b"\x00" + value
    return len(data).to_bytes(4, "big") + b"tEXt" + data + b"\x00\x00\x00\x00"


def _signal(report: dict, signal_id: str) -> dict:
    return next(item for item in report["signals"] if item["id"] == signal_id)


def test_ai_generator_name_is_reported_as_metadata_only():
    png = b"\x89PNG\r\n\x1a\n" + _png_text_chunk(b"Software", b"Stable Diffusion WebUI")
    report = inspect_ai_origin_signals(
        png,
        {"software": "Stable Diffusion WebUI", "png_chunks": []},
        c2pa_present=False,
        c2pa_status="NO_MANIFEST_FOUND",
        generic_pixel_cue_count=0,
    )

    metadata_signal = _signal(report, "generator_metadata")
    assert metadata_signal["status"] == "DETECTED"
    assert "Stable Diffusion" in metadata_signal["evidence"]
    assert "forged" in metadata_signal["limitation"]
    assert report["classifier_available"] is False


def test_absent_generator_metadata_does_not_claim_human_origin():
    report = inspect_ai_origin_signals(
        b"ordinary image bytes",
        {"software": None, "png_chunks": []},
        c2pa_present=False,
        c2pa_status="NO_MANIFEST_FOUND",
        generic_pixel_cue_count=0,
    )

    assert _signal(report, "generator_metadata")["status"] == "NOT_DETECTED"
    assert _signal(report, "c2pa_provenance")["status"] == "NOT_DETECTED"
    assert _signal(report, "visible_ai_mark")["status"] == "NOT_CHECKED"
    assert _signal(report, "source_layers")["status"] == "NOT_CHECKED"
    assert _signal(report, "ai_origin_classifier")["status"] == "NOT_AVAILABLE"


def test_marker_and_pixel_cues_keep_their_limited_meanings():
    report = inspect_ai_origin_signals(
        b"image with jumbf marker",
        {"software": None, "png_chunks": []},
        c2pa_present=True,
        c2pa_status="MANIFEST_PRESENT_UNVERIFIED",
        generic_pixel_cue_count=2,
    )

    credential = _signal(report, "c2pa_provenance")
    pixel = _signal(report, "generic_pixel_cues")
    assert credential["status"] == "UNVERIFIED"
    assert "does not validate" in credential["evidence"]
    assert pixel["status"] == "DETECTED"
    assert "not AI-specific" in pixel["limitation"]
