"""Minimal aiohttp stub for local tests."""

class ClientTimeout:
    def __init__(self, total: int | None = None):
        self.total = total


class ClientError(Exception):
    pass


class _DummyResp:
    def __init__(self):
        self.status = 200

    async def text(self):
        return "[]"

    async def json(self, content_type=None):
        return {}


class _Ctx:
    def __init__(self, resp: _DummyResp):
        self._resp = resp

    async def __aenter__(self):
        return self._resp

    async def __aexit__(self, exc_type, exc, tb):
        return False


class ClientSession:
    def __init__(self):
        pass

    def request(self, *args, **kwargs):
        return _Ctx(_DummyResp())
