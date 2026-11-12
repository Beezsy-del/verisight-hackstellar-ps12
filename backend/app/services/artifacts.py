"""Expiring private preview capabilities for one local process; not cloud storage."""
import base64
import os
import secrets
import tempfile
import time
from pathlib import Path
from threading import RLock

class ArtifactStore:
    def __init__(self, root=None, ttl=600, budget=128 * 1024 * 1024):
        self.root = Path(root or tempfile.mkdtemp(prefix='verisight-previews-'))
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.ttl, self.budget = ttl, budget
        self.entries = {}
        self.lock = RLock()

    def cleanup(self):
        with self.lock:
            for token, (_, deadline, _) in list(self.entries.items()):
                if deadline <= time.monotonic():
                    (self.root / token).unlink(missing_ok=True)
                    del self.entries[token]

    def put(self, value):
        header, encoded = value.split(',', 1)
        mime = header.removeprefix('data:').removesuffix(';base64')
        if mime not in {'image/png', 'image/jpeg', 'image/webp', 'image/bmp'}:
            raise ValueError('Unsupported preview format')
        content = base64.b64decode(encoded, validate=True)
        if len(content) > 6_500_000:
            raise ValueError('Preview exceeds supported artifact size')
        with self.lock:
            self.cleanup()
            if sum(size for _, _, size in self.entries.values()) + len(content) > self.budget:
                raise ValueError('Temporary preview capacity is full')
            token = secrets.token_urlsafe(32)
            with (self.root / token).open('xb') as stream:
                os.chmod(self.root / token, 0o600)
                stream.write(content)
            self.entries[token] = (mime, time.monotonic() + self.ttl, len(content))
        return '/api/artifacts/' + token

    def get(self, token):
        with self.lock:
            self.cleanup()
            item = self.entries.get(token)
            if item is None:
                return None
            return (self.root / token).read_bytes(), item[0]

    def clear(self):
        with self.lock:
            for token in list(self.entries):
                (self.root / token).unlink(missing_ok=True)
            self.entries.clear()

store = ArtifactStore()

def delivery_report(value):
    """Copy reports; never mutate cached reports or forensic inputs."""
    if os.getenv('VERCEL'):
        return value
    if hasattr(type(value), 'model_fields'):
        return value.model_copy(update={key: delivery_report(getattr(value, key)) for key in type(value).model_fields})
    if isinstance(value, dict):
        return {key: delivery_report(item) for key, item in value.items()}
    if isinstance(value, list):
        return [delivery_report(item) for item in value]
    if isinstance(value, str) and value.startswith('data:image/') and len(value) > 128_000:
        return store.put(value)
    return value
