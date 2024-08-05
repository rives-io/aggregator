from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from fastapi_pagination import add_pagination

from .db.session import get_engine
from .routers import profile, tape, cartridge, rule, console_achievements

app = FastAPI(
    title="RIVES Aggregator",
    summary=(
        "Aggregate information from multiple sources and make them readily "
        "available for easy querying. All information found here comes from "
        "verifiable notices of the Cartesi DApp or from the blockchain."
    ),
    version='0.3.0',
    license_info={
        'name': 'Apache License 2.0',
        'identifier': 'Apache-2.0',
    },
    openapi_url='/agg/openapi.json',
    docs_url='/agg/docs',
    redoc_url=None,
)
add_pagination(app)


@app.on_event('startup')
def on_startup():
    get_engine()


@app.get('/docs', include_in_schema=False)
def redirect_docs():
    return RedirectResponse('/agg/docs')


app.include_router(profile.router)
app.include_router(tape.router)
app.include_router(cartridge.router)
app.include_router(rule.router)
app.include_router(console_achievements.router)


class HealthResponse(BaseModel):
    status: str = "ok"


@app.get('/health', include_in_schema=False)
async def healthcheck() -> HealthResponse:
    """Simple Healthcheck. Always returns ok."""
    return {'status': 'ok'}
