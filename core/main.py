from copy import deepcopy
import json
import time
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.urls import api_router
from db.database import Model, engine

app = FastAPI()
app.include_router(api_router, prefix=settings.API_URL)
app.mount("/static", StaticFiles(directory="static"), name="static")


print("Connection to PostgreSQL...")
Model.metadata.create_all(bind=engine)


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

    if request.url.path == "/api/v1/users/login":
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


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_root():
    return FileResponse("static/index.html")


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=7040, log_level="debug")
