import logging

import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.logging import LoggingIntegration

import settings
from app.routes import app as routes

sentry_sdk.init(
    dsn=settings.SENTRY_DSN_URL,
    environment=settings.ENVIRONMENT,
    integrations=[
        LoggingIntegration(),
    ],
    traces_sample_rate=0.2,
    send_default_pii=True,
)
logging.basicConfig(level=logging.INFO)

app = FastAPI(docs_url="/api/swagger/", openapi_url="/api/openapi.json")
app.include_router(routes)


@app.get("/health/")
def health() -> str:
    return "i'm alive"
