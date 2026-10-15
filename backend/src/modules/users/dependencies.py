import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from modules.users.utils import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")

oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="api/v1/users/login", auto_error=False
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> int:
    try:
        payload = decode_jwt(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний тип токена. Для доступу потрібен Access Token.",
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="У токені відсутній ID користувача",
            )

        return int(user_id_str)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Термін дії токена закінчився. Будь ласка, оновіть токен.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Недійсний токен."
        )


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
) -> int | None:
    if not token:
        return None

    return await get_current_user(token)
