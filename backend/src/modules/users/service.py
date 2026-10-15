import logging
import random
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from core.config import settings
from fastapi import BackgroundTasks, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.users.models import EmailVerification, User

from .schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenInfo,
    UserLogin,
    UserRegistration,
    VerifyEmailRequest,
)
from .utils import decode_jwt, encode_jwt, hash_password, validate_password

logger = logging.getLogger(__name__)
DUMMY_HASH = hash_password("fake_password_for_security")


async def get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)

    user = await session.scalar(query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have permission to access this resource",
        )
    return user


async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession,
    fm: FastMail,
):
    generic_response = {
        "message": "Якщо користувач з таким email існує, на нього відправлено інструкцію з відновлення."
    }

    query = select(User).where(User.email == request.email)
    user = await session.scalar(query)

    if not user:
        return generic_response

    await session.execute(
        delete(EmailVerification).where(EmailVerification.user_id == user.user_id)
    )

    reset_token = str(uuid.uuid4())
    expire_time = (datetime.now(UTC) + timedelta(minutes=15)).replace(tzinfo=None)

    new_verification = EmailVerification(
        user_id=user.user_id,
        token=reset_token,
        expires_at=expire_time,
    )
    session.add(new_verification)
    await session.commit()

    html_content = f"""
    <h2>Відновлення пароля</h2>
    <p>Для відновлення пароля перейдіть за посиланням нижче:</p>
    <p><a href="{settings.frontend_url}/reset-password?token={reset_token}">Відновити пароль</a></p>
    <p>Посилання дійсне протягом 15 хвилин.</p>
    """

    message = MessageSchema(
        subject="Відновлення пароля",
        recipients=[user.email],
        body=html_content,
        subtype=MessageType.html,
    )

    if settings.environment.lower() == "production":
        background_tasks.add_task(fm.send_message, message)
    else:
        logger.info("=" * 40)
        logger.info("📧 [MOCK EMAIL SYSTEM]")
        logger.info(f"To: {user.email}")
        logger.info(f"Link: {settings.frontend_url}/reset-password?token={reset_token}")
        logger.info("=" * 40)

    return generic_response


async def reset_password(request: ResetPasswordRequest, session: AsyncSession):
    query = select(EmailVerification).where(EmailVerification.token == request.token)
    verification = await session.scalar(query)

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недійсний або прострочений токен відновлення.",
        )

    if verification.expires_at < datetime.now(UTC).replace(tzinfo=None):
        await session.delete(verification)
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Термін дії токена минув. Зробіть запит на відновлення ще раз.",
        )

    user_query = select(User).where(User.user_id == verification.user_id)
    user = await session.scalar(user_query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено.",
        )

    hashed_pwd = hash_password(request.new_password)
    user.hash_password = (
        hashed_pwd.decode("utf-8") if isinstance(hashed_pwd, bytes) else hashed_pwd
    )

    await session.delete(verification)
    await session.commit()

    return {"message": "Пароль успішно змінено"}


async def register_user(
    session: AsyncSession,
    user_in: UserRegistration,
    background_tasks: BackgroundTasks,
    fm: FastMail,
) -> User:
    query = select(User).where(User.email == user_in.email).limit(1)
    result = await session.execute(query)

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким email вже існує",
        )

    hashed_pwd = hash_password(user_in.password)
    safe_hash = (
        hashed_pwd.decode("utf-8") if isinstance(hashed_pwd, bytes) else hashed_pwd
    )

    new_user = User(
        email=user_in.email,
        hash_password=safe_hash,
        is_active=False,
    )

    session.add(new_user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Помилка при реєстрації. Можливо, email або телефон вже використовуються.",
        )

    await session.refresh(new_user)

    verification_code = str(random.randint(100000, 999999))
    expire_time = (datetime.now(UTC) + timedelta(minutes=15)).replace(tzinfo=None)
    new_verification = EmailVerification(
        user_id=new_user.user_id,
        token=verification_code,
        expires_at=expire_time,
    )
    session.add(new_verification)
    await session.commit()

    html_content = f"""
    <h2>Підтвердження реєстрації</h2>
    <p>Ваш код для підтвердження email:</p>
    <h1 style="letter-spacing: 5px;">{verification_code}</h1>
    <p>Код дійсний 15 хвилин.</p>
    """

    message = MessageSchema(
        subject="Підтвердження реєстрації",
        recipients=[user_in.email],
        body=html_content,
        subtype=MessageType.html,
    )

    if settings.environment.lower() == "production":
        background_tasks.add_task(fm.send_message, message)
    else:
        logger.info(f"📧 [MOCK EMAIL] To: {user_in.email} | Code: {verification_code}")

    return new_user


async def verify_email_code(session: AsyncSession, verify_data: VerifyEmailRequest):
    user_query = select(User).where(User.email == verify_data.email)
    user = await session.scalar(user_query)

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if user.is_active:
        return {"message": "Email вже підтверджено"}

    verify_query = select(EmailVerification).where(
        EmailVerification.user_id == user.user_id,
        EmailVerification.token == verify_data.code,
    )
    verification = await session.scalar(verify_query)

    if not verification:
        raise HTTPException(status_code=400, detail="Невірний код підтвердження")

    if verification.expires_at < datetime.now(UTC).replace(tzinfo=None):
        await session.delete(verification)
        await session.commit()
        raise HTTPException(status_code=400, detail="Час дії коду вичерпано")

    user.is_active = True
    await session.delete(verification)
    await session.commit()

    return {"message": "Email успішно підтверджено. Тепер ви можете увійти."}


async def user_login(
    session: AsyncSession,
    user_in: UserLogin,
) -> dict:
    stmt = select(User).where(User.email == user_in.email).limit(1)
    result = await session.execute(stmt)
    user: User | None = result.scalar_one_or_none()

    if not user:
        validate_password(user_in.password, DUMMY_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний email або пароль"
        )

    if not validate_password(user_in.password, user.hash_password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний email або пароль"
        )

    if getattr(user, "is_active", None) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Будь ласка, підтвердіть ваш email. Код відправлено на пошту.",
        )

    access_token = encode_jwt(
        payload={
            "sub": str(user.user_id),
            "type": "access",
            "jti": str(uuid.uuid4()),
        },
        expire_minutes=15,
    )
    refresh_token = encode_jwt(
        payload={"sub": str(user.user_id), "type": "refresh", "jti": str(uuid.uuid4())},
        expire_minutes=60 * 24 * 30,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }


async def refresh_access_token(session: AsyncSession, refresh_token: str) -> TokenInfo:
    try:
        payload = decode_jwt(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id = payload.get("sub")

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сесія закінчилася.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Недійсний токен"
        )

    stmt = select(User).where(User.id == int(user_id)).limit(1)
    result = await session.execute(stmt)
    user: User | None = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    new_access_token = encode_jwt(
        payload={"sub": str(user.id), "type": "access"}, expire_minutes=15
    )
    new_refresh_token = encode_jwt(
        payload={"sub": str(user.id), "type": "refresh"}, expire_minutes=60 * 24 * 30
    )

    return TokenInfo(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="Bearer",
    )
