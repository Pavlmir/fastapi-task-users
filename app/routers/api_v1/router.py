from typing import List
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from pydantic import parse_obj_as
from starlette.responses import HTMLResponse
from tortoise import exceptions

from app.schemas.db_schemas import (UserTokenPydantic,
                                    UserCreatePydantic,
                                    TokenBasePydantic,
                                    UserBasePydantic,
                                    Users_Pydantic)
from app.repositories.repo import UsersRepo, TokensRepo
from app.models.app_models import UserErrorsModel, Users
from app.utils.dependecies import get_current_user


router = APIRouter()
logger = logging.getLogger("__name__")


@router.get("/get", description="Get 'Hello!'", response_description="Some text")
async def get():
    return HTMLResponse("V1: Hello!")


@router.post("/login", response_model=TokenBasePydantic)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    /v1/login
    """
    user = await Users.filter(name=form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect name")

    if not UsersRepo.validate_password(
        password=form_data.password, hashed_password=user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password")

    db_token = await TokensRepo.create(user_id=user.id)

    return parse_obj_as(TokenBasePydantic, db_token)


@router.get("/users/me", response_model=UserBasePydantic)
def read_users_me(current_user: UserTokenPydantic = Depends(get_current_user)) -> UserTokenPydantic:
    """/v1/user/me"""
    return current_user


@router.get("/users/list", response_model=List[UserBasePydantic])
async def list_users(skip: int = 0,
                     limit: int = 10,
                     current_user: UserTokenPydantic = Depends(get_current_user)):
    db_users = await UsersRepo.get_list(limit=limit, offset=skip)
    return parse_obj_as(List[UserBasePydantic], db_users)


@router.get("/index", response_class=FileResponse, include_in_schema=False)
def index():
    return FileResponse("static/index.html")


@router.get("/users/{user_id}", response_model=Users_Pydantic)
async def get_user_by_id(user_id: int, current_user: UserTokenPydantic = Depends(get_current_user)):
    db_user = await UsersRepo.get_by_id(user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserErrorsModel.user_not_found.value
        )

    return Users_Pydantic.from_orm(db_user)


@router.post("/manager/users/",
             summary="Создать нового пользователя",
             response_model=UserTokenPydantic,
             status_code=status.HTTP_201_CREATED,
             tags=["Пользователи"])
async def create_user(data: UserCreatePydantic, current_user: UserTokenPydantic = Depends(get_current_user)):
    """Create new User"""
    db_user = await Users.filter(email=data.email).first()
    if db_user:
        return HTMLResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=UserErrorsModel.email_exist.value
        )

    try:
        db_user = await UsersRepo.create(data)
    except exceptions.BaseORMException as e:
        logger.exception(e)
        return HTMLResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(e))
    except ValueError as e:
        logger.exception(e)
        return HTMLResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
    except exceptions.IntegrityError as e:
        logger.exception(e)
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=str(e))

    db_token = await TokensRepo.create(db_user.id)

    row = data.dict()
    row["id"] = db_user.id
    row["token"] = {
        "id": db_token.id,
        "access_token": db_token.token,
        "expires": db_token.expires
    }

    result_user = UserTokenPydantic(**row)

    return result_user

#
# @router.get("/models/{model_name}")
# async def get_model(model_name: ModelName):
#     if model_name is ModelName.alexnet:
#         return {"model_name": model_name, "message": "Deep Learning FTW!"}
#
#     if model_name.value == "lenet":
#         return {"model_name": model_name, "message": "LeCNN all the images"}
#
#     return {"model_name": model_name, "message": "Have some residuals"}