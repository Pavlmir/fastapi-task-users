from typing import List
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from pydantic import parse_obj_as
from starlette.responses import HTMLResponse
from tortoise import exceptions, Tortoise

from app.schemas.db_schemas import UserTokenPydantic, UserCreatePydantic, TokenBasePydantic, UserBasePydantic
from app.repositories.repo import UsersActions, users_repo
from app.models.app_models import UserErrorsModel, Users
from app.utils.dependecies import get_current_user


router = APIRouter()
logger = logging.getLogger("__name__")


@router.get("/get", description="Get 'Hello!'", response_description="Some text")
async def get():
    return HTMLResponse("V1: Hello!")


@router.post("/login", response_model=TokenBasePydantic)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    /api/v1/users/login
    """
    user = users_repo.find_by_name(name=form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect name")

    if not users_repo.validate_password(
        password=form_data.password, hashed_password=user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password")

    db_token = users_repo.create_user_token(user_id=user.id)

    return parse_obj_as(TokenBasePydantic, db_token)


@router.get("/me", response_model=UserBasePydantic)
def read_users_me(current_user: UserTokenPydantic = Depends(get_current_user)) -> UserTokenPydantic:
    """/api/v1/users/me"""
    return current_user


@router.get("/", response_model=List[UserBasePydantic])
def list_users(skip: int = 0,
               limit: int = 10,
               current_user: UserTokenPydantic = Depends(get_current_user)):
    db_users = users_repo.get_list(limit=limit, offset=skip)
    return parse_obj_as(List[UserBasePydantic], db_users)


@router.get("/list", response_class=FileResponse, include_in_schema=False)
def list_users():
    return FileResponse("static/index.html")


@router.get("/{user_id}", response_model=UserTokenPydantic)
def get_user_by_id(user_id: UUID, current_user: str = Depends(get_current_user)):
    db_user = users_repo.get_by_id(user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserErrorsModel.user_not_found.value
        )

    return UserTokenPydantic.from_orm(db_user)


@router.post("/manager/users/",
             summary="Создать нового пользователя",
             response_model=UserTokenPydantic,
             status_code=status.HTTP_201_CREATED,
             tags=["Пользователи"])
async def create_user(user: UserCreatePydantic, current_user: str = Depends(get_current_user)):
    """Create new User"""
    db_user = await Users.filter(email=user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UserErrorsModel.email_exist.value
        )

    try:
        new_speaker = await users_repo.create_object(data, {"created_by": current_user})
    except exceptions.BaseORMException as e:
        logger.exception(e)
        return HTMLResponse(status_code=400)
    except ValueError as e:
        return HTMLResponse(status_code=400, content=str(e))

    try:
        new_obj = await users_repo.create_object(obj, {"public_event_id": event_id})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except exceptions.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PublicEvent with id: {} not found".format(event_id)
        )
    return new_obj

    data = UserTokenPydantic.from_orm(new_speaker).dict()
    db_user = users_repo.create(user)
    db_token = users_repo.create_user_token(db_user.id)

    result_user = UserTokenPydantic.from_orm(db_user)
    result_user.token = {"token": db_token.token, "expires": db_token.expires}

    return result_user