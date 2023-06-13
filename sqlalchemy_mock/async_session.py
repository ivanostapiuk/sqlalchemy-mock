from .session import Session


class AsyncSession(Session):
    async def execute(self, expresion: object, *args, **kwargs):
        return super().execute(expresion, *args, **kwargs)