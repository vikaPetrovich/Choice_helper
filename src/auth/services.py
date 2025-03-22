from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError as JWTError
from sqlalchemy.future import select

from src.auth.models import User
from src.auth.schemas import UserCreate
from fastapi import HTTPException, status, Depends

from src.db import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()  # Объявляем security локально

# Конфигурация JWT
SECRET_KEY = "your_secret_key"
REFRESH_SECRET_KEY = "your_refresh_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля и его хеша."""
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(db: AsyncSession, username: str):
    """Получает пользователя по username."""
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()





async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """ Декодирование и проверка JWT-токена """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Извлекаем непосредственно строку-токен
    token = credentials.credentials

    try:
        # Декодируем строковый токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Проверяем, что пользователь существует
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user



async def create_user(db: AsyncSession, user: UserCreate):
    """Создает нового пользователя в БД."""
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    """Аутентифицирует пользователя по логину и паролю."""
    user = await get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Создает access токен."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """Создает refresh токен."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


async def save_refresh_token(db: AsyncSession, username: str, refresh_token: str):
    """Сохраняет refresh токен пользователя в БД."""
    user = await get_user(db, username)
    if user:
        user.refresh_token = refresh_token
        await db.commit()


async def verify_refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):

    """Проверяет refresh токен и возвращает пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print('мы зашили в функцию')
    print(refresh_token)
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(db, username)
    print(user.id)
    if not user or user.refresh_token != refresh_token:
        raise credentials_exception

    return user
