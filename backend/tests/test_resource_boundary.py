import asyncio
import pytest
from app.services.resource_boundary import AnalysisBoundary


async def receive():
    return {'type':'http.request','body':b''}


def test_large_response_is_blocked_and_slot_released():
    async def app(scope, receive, send):
        await send({'type':'http.response.start','status':200,'headers':[]})
        await send({'type':'http.response.body','body':b'x'*100})
    guard=AnalysisBoundary(app,capacity=1,response_budget=20)
    async def run():
        for _ in range(2):
            messages=[]
            async def send(m):messages.append(m)
            await guard({'type':'http','path':'/api/analyze'},receive,send)
            assert messages[0]['status']==413
            assert b'BLOCK' in messages[1]['body']
    asyncio.run(run())


def test_concurrent_overload_is_explicit_and_recovers():
    async def run():
        started=asyncio.Event();finish=asyncio.Event()
        async def app(scope,receive,send):
            started.set();await finish.wait()
            await send({'type':'http.response.start','status':200,'headers':[]})
            await send({'type':'http.response.body','body':b'{}'})
        guard=AnalysisBoundary(app,capacity=1)
        first=[];second=[]
        async def send1(m):first.append(m)
        async def send2(m):second.append(m)
        task=asyncio.create_task(guard({'type':'http','path':'/api/analyze'},receive,send1))
        await started.wait()
        await guard({'type':'http','path':'/api/analyze'},receive,send2)
        assert second[0]['status']==503
        finish.set();await task
        assert first[0]['status']==200
    asyncio.run(run())


def test_exception_releases_slot():
    async def app(scope,receive,send):raise ValueError('failure')
    guard=AnalysisBoundary(app,capacity=1)
    async def run():
        async def send(m):pass
        for _ in range(2):
            with pytest.raises(ValueError):
                await guard({'type':'http','path':'/api/analyze'},receive,send)
    asyncio.run(run())


@pytest.mark.parametrize('report', [
    {'verdict':'INCONCLUSIVE'},
    {'verdict':'INCONCLUSIVE','analysis_gate':{'allowed_actions':{'view_report':False}}},
    {'reanalysis':{'verdict':'INCONCLUSIVE'}},
    {'report':{'filename':'unvalidated.png'}},
])
def test_unvalidated_report_never_leaves_as_success(report):
    import json
    async def app(scope,receive,send):
        await send({'type':'http.response.start','status':200,'headers':[]})
        await send({'type':'http.response.body','body':json.dumps(report).encode()})
    async def run():
        messages=[]
        async def send(m):messages.append(m)
        await AnalysisBoundary(app)({'type':'http','path':'/api/analyze'},receive,send)
        assert messages[0]['status']==503
    asyncio.run(run())
