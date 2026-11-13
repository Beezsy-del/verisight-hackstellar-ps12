"""No server speech model is configured. Never invent a transcript."""
def process_audio_transcription(audio_bytes: bytes, content_type: str, language_code="en-IN", client_hint=None):
    if len(audio_bytes) < 64:
        raise ValueError("Audio payload is empty or corrupted.")
    raise NotImplementedError("Server transcription is unavailable. Use browser speech recognition where supported, or type and review your statement.")
