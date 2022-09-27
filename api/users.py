from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from pydantic import parse_obj_as

from apps.users.schemas import UserToken, UserCreate, TokenBase, UserBase
from apps.users.actions import UsersActions
from apps.users.models import UserErrorsModel
from apps.users.dependecies import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login", response_model=TokenBase)
def login(form_data: OAuth2PasswordRequestForm = Depends(), users_actoins: UsersActions = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    /api/v1/users/login
    """
    user = users_actoins.find_by_name(name=form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect name")

    if not users_actoins.validate_password(
        password=form_data.password, hashed_password=user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password")

    db_token = users_actoins.create_user_token(user_id=user.id)

    return parse_obj_as(TokenBase, db_token)


@router.get("/me", response_model=UserBase)
def read_users_me(current_user: UserToken = Depends(get_current_user)) -> UserToken:
    """/api/v1/users/me"""
    return current_user


@router.get("/", response_model=List[UserBase])
def list_users(skip: int = 0, max: int = 10, current_user: UserToken = Depends(get_current_user), users_actoins: UsersActions = Depends()):
    db_users = users_actoins.all(skip=skip, max=max)
    return parse_obj_as(List[UserBase], db_users)


@router.get("/list", response_class=FileResponse, include_in_schema=False)
def list_users():
    return FileResponse("static/index.html")


@router.post("/", response_model=UserToken, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, current_user: UserToken = Depends(get_current_user), users_actoins: UsersActions = Depends()):
    db_user = users_actoins.find_by_email(email=user.email)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UserErrorsModel.email_exist.value
        )

    db_user = users_actoins.create(user)
    db_token = users_actoins.create_user_token(db_user.id)

    result_user = UserToken.from_orm(db_user)
    result_user.token = {"token": db_token.token, "expires": db_token.expires}

    return result_user


@router.get("/{user_id}", response_model=UserToken)
def get_user_by_id(user_id: UUID, users_actoins: UsersActions = Depends(get_current_user)):
    db_user = users_actoins.find_by_id(user_id)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserErrorsModel.user_not_found.value
        )

    return UserToken.from_orm(db_user)
