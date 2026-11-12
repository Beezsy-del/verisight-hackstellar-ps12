"""Per-process admission and response bounds, with explicit retryable failures."""
import json
from threading import BoundedSemaphore


class RequestLimitExceeded(Exception):
    pass


class AnalysisBoundary:
    def __init__(self, app, capacity=2, response_budget=4_000_000):
        self.app = app
        self.slots = BoundedSemaphore(capacity)
        self.response_budget = response_budget

    async def __call__(self, scope, receive, send):
        path = scope.get('path', '')
        guarded = path.startswith(('/api/analyze', '/api/simulate-whatsapp', '/api/mobile-upload', '/api/latest-mobile-upload'))
        if scope['type'] != 'http' or not guarded:
            return await self.app(scope, receive, send)
        async def reject(status, message):
            body = json.dumps({'detail': message, 'processing_status': 'FAILED', 'analysis_gate': {'state': 'BLOCK', 'automated_approval': False}}).encode()
            await send({'type':'http.response.start','status':status,'headers':[(b'content-type',b'application/json'),(b'cache-control',b'no-store'),(b'retry-after',b'2')]})
            await send({'type':'http.response.body','body':body})
        if not self.slots.acquire(blocking=False):
            return await reject(503, 'Analysis capacity is busy. Retry shortly; no assessment was completed.')
        request_size = 0
        request_exceeded = False
        async def bounded_receive():
            nonlocal request_size, request_exceeded
            message = await receive()
            request_size += len(message.get('body', b''))
            if request_size > 21 * 1024 * 1024:
                request_exceeded = True
                raise RequestLimitExceeded()
            return message
        start = None
        parts = []
        size = 0
        exceeded = False
        async def bounded_send(message):
            nonlocal start, size, exceeded
            if message['type'] == 'http.response.start':
                start = message
            elif message['type'] == 'http.response.body':
                size += len(message.get('body', b''))
                if size > self.response_budget:
                    exceeded = True
                    parts.clear()
                elif not exceeded:
                    parts.append(message.get('body', b''))
                if not message.get('more_body', False):
                    if request_exceeded:
                        await reject(413, 'Upload request exceeds the 21 MiB transport limit.')
                    elif exceeded:
                        await reject(413, 'Analysis previews exceed the response budget. Use a smaller image; no usable assessment is being returned.')
                    else:
                        body = b''.join(parts)
                        if start['status'] == 200:
                            try:
                                parsed = json.loads(body)
                            except (ValueError, UnicodeDecodeError):
                                parsed = None
                            reports = []
                            if isinstance(parsed, dict):
                                if 'verdict' in parsed:
                                    reports.append(parsed)
                                if isinstance(parsed.get('reanalysis'), dict):
                                    reports.append(parsed['reanalysis'])
                                if isinstance(parsed.get('report'), dict):
                                    reports.append(parsed['report'])
                            for report in reports:
                                gate = report.get('analysis_gate')
                                if not isinstance(gate, dict) or not gate.get('allowed_actions', {}).get('view_report', False):
                                    return await reject(503, 'Analysis evidence validation failed. No assessment is available.')
                        start['headers'] = list(start.get('headers', [])) + [(b'cache-control', b'no-store')]
                        await send(start)
                        await send({'type':'http.response.body','body':body})
        try:
            await self.app(scope, bounded_receive, bounded_send)
        except RequestLimitExceeded:
            await reject(413, "Upload request exceeds the 21 MiB transport limit.")
        finally:
            self.slots.release()
