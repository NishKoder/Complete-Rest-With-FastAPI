import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from storeapi.database import database
from storeapi.logging_conf import configure_logging
from storeapi.routers.post import router as post_router
from storeapi.routers.user import router as user_router

logging = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logging.info("Starting application")
    await database.connect()
    yield
    logging.info("Stopping application")
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(post_router, prefix="/api/v1/posts")
app.include_router(user_router, prefix="/api/v1/users")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    logging.error("HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
