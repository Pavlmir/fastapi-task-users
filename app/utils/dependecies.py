from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer

from app.repositories.repo import users_repo


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = users_repo.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user
