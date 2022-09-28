from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/healthz")
async def get_healthcheck():
    """Base url for checking the health of the docker container"""
    return HTMLResponse(status_code=status.HTTP_200_OK)
