"""Single-reviewer boundary; not a multi-tenant account system."""
import base64
import hmac
import ipaddress
import os
from starlette.responses import JSONResponse

class PrivateAccess:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        host = (scope.get('client') or ('', 0))[0]
        try:
            local = ipaddress.ip_address(host).is_loopback
        except ValueError:
            local = host == 'testclient'
        headers = dict(scope.get('headers', []))
        origin = headers.get(b'origin', b'').decode(errors='replace')
        if origin and scope.get('method', 'GET') not in {'GET', 'HEAD', 'OPTIONS'}:
            same_origin = origin == scope.get('scheme', 'http') + '://' + headers.get(b'host', b'').decode(errors='replace')
            local_dev = origin in {'http://localhost:5174', 'http://127.0.0.1:5174', 'http://localhost:5173', 'http://127.0.0.1:5173'} and local
            if not (same_origin or local_dev):
                return await JSONResponse({'detail': 'Cross-origin submissions are not allowed.'}, status_code=403)(scope, receive, send)
        password = os.getenv('VERISIGHT_ACCESS_PASSWORD', '')
        authorized = False
        if password:
            try:
                scheme, token = dict(scope.get('headers', [])).get(b'authorization', b'').decode().split(' ', 1)
                credentials = base64.b64decode(token, validate=True).decode()
                authorized = scheme.lower() == 'basic' and hmac.compare_digest(credentials.encode(), ('verisight:' + password).encode())
            except (ValueError, UnicodeError):
                pass
        elif local and not os.getenv('VERCEL'):
            authorized = True
        if not local and scope.get('scheme') != 'https':
            response = JSONResponse({'detail': 'Remote private access requires HTTPS.'}, status_code=403)
        elif not authorized:
            response = JSONResponse({'detail': 'Private prototype. Authorized access is required.'}, status_code=401,
                headers={'WWW-Authenticate': 'Basic realm="VeriSight private prototype", charset="UTF-8"'})
        else:
            async def private_send(message):
                if message['type'] == 'http.response.start':
                    message['headers'] = list(message.get('headers', [])) + [(b'cache-control', b'no-store'), (b'referrer-policy', b'no-referrer'), (b'x-content-type-options', b'nosniff')]
                await send(message)
            return await self.app(scope, receive, private_send)
        response.headers['Cache-Control'] = 'no-store'
        return await response(scope, receive, send)
