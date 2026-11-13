from typing import Any


def inspect_c2pa_provenance(image_bytes: bytes) -> tuple[bool, str, dict[str, Any]]:
    """Detect possible C2PA markers without claiming to validate a credential.

    A real validator must parse the active manifest, check its signature, trust
    chain, assertions, and asset binding. A byte-marker search cannot do that.
    """
    has_marker = b"jumbf" in image_bytes.lower() or b"c2pa" in image_bytes.lower()
    return (
        has_marker,
        "MANIFEST_PRESENT_UNVERIFIED" if has_marker else "NO_MANIFEST_FOUND",
        {
            "marker_present": has_marker,
            "manifest_store_found": False,
            "signature_valid": None,
            "signer_identity": None,
            "trust_status": "NOT_VALIDATED" if has_marker else "NO_CREDENTIAL",
            "validation_available": False,
            "note": "Marker detection only; this build does not parse or cryptographically validate C2PA credentials.",
        },
    )
