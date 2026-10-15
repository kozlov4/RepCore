from typing import Annotated

from core.config import settings
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import ConnectionConfig, FastMail
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_helper import db_helper

from .dependencies import get_current_user
from .schemas import (
    ForgotPasswordRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenInfo,
    UserLogin,
    UserRegistration,
    UserResponse,
    VerifyEmailRequest,
)
from .service import (
    forgot_password,
    get_user,
    refresh_access_token,
    register_user,
    reset_password,
    user_login,
    verify_email_code,
)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)


router = APIRouter(tags=["Users"])

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]
OAuth2FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
@limiter.limit("5/minute")
async def user_registration(
    request: Request,
    user_data: UserRegistration,
    session: SessionDep,
    background_tasks: BackgroundTasks,
):
    return await register_user(
        session=session,
        user_in=user_data,
        background_tasks=background_tasks,
        fm=fm,
    )


@router.post("/login")
async def login_for_swagger(form_data: OAuth2FormDep, session: SessionDep):
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    return await user_login(session=session, user_in=user_data)


@router.post("/refresh", response_model=TokenInfo)
async def refresh_jwt_tokens(token_data: RefreshTokenRequest, session: SessionDep):
    return await refresh_access_token(
        session=session, refresh_token=token_data.refresh_token
    )


@router.post("/verify-email")
async def verify_email(verify_data: VerifyEmailRequest, session: SessionDep):
    return await verify_email_code(session=session, verify_data=verify_data)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password_endpoint(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await forgot_password(
        request=request, background_tasks=background_tasks, session=session, fm=fm
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password_endpoint(
    request: ResetPasswordRequest,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await reset_password(request=request, session=session)
