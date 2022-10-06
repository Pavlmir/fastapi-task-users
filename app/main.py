import time
import json
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger as log
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from strawberry.fastapi import GraphQLRouter

from app.core.config import settings
from app.core.db import init_db
from app.routers.base_router import api_router
from app.schemas.db_schemas import schema_graphql


def create_application() -> FastAPI:
    app_fastapi = FastAPI(
        title="FastAPI Microservice with RESTful API and Clean Architecture",
        version="0.1.0",
        root_path=settings.API_ROOT_URL,
        docs_url=None if settings.NODOC else "/docs",
        redoc_url=None if settings.NODOC else "/redoc",
    )

    app_fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=[origin for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app_fastapi.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "static"), name="static")
    app_fastapi.include_router(api_router)
    app_fastapi.include_router(GraphQLRouter(schema_graphql), prefix="/graphql")

    return app_fastapi


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_root():
    return FileResponse("static/index.html")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    token = request.cookies.get("Authorization")
    if token:
        token = f"Bearer {token.split('Bearer')[1].strip()}"
        request.scope["headers"].append(
            (b"authorization", bytes(token, encoding='utf-8')))

    response = await call_next(request)
    process_time = time.time() - start_time

    if request.url.path == "/v1/login":
        response_body = b''
        async for chunk in response.body_iterator:
            response_body += chunk

        body = json.loads(response_body)
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type)
        token = body.get("access_token", "unauthorized")
        response.set_cookie("Authorization", value=f"Bearer {token}")

    response.headers["X-Process-Time"] = str(process_time)

    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7040, log_level="debug")