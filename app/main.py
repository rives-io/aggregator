from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_pagination import add_pagination

from .db.session import get_engine
from .routers import profile, tape, cartridge, rule, console_achievements

app = FastAPI(
    title="RIVES External Indexer",
    summary="Third Indexer of the Solution",
    version='0.1.0',
    license_info={
        'name': 'Apache License 2.0',
        'identifier': 'Apache-2.0',
    }
)
add_pagination(app)


@app.on_event('startup')
def on_startup():
    get_engine()


app.include_router(profile.router)
app.include_router(tape.router)
app.include_router(cartridge.router)
app.include_router(rule.router)
app.include_router(console_achievements.router)


class HealthResponse(BaseModel):
    status: str = "ok"


@app.get('/health', tags=['healthcheck'])
async def healthcheck() -> HealthResponse:
    """Simple Healthcheck. Always returns ok."""
    return {'status': 'ok'}
