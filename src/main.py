from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer

from src.boards.router import router as boards_router
from src.cards.router import router as cards_router
from src.sessions.router import router as sessions_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.swipes.router import router as swipes_router
from src.brackets.router import router as brackets_router
from src.auth.router import router as auth_router
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.auth.services import get_current_user
from src.auth.models import User
from src.friends.router import router as friends_router




app = FastAPI(title="Choice Helper API", version="1.0.0")

app.include_router(brackets_router, prefix="/brackets", tags=["Brackets"])
app.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(swipes_router, prefix="/swipes", tags=["Swipes"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(friends_router, prefix="/friends", tags=["friends"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешает запросы с любого источника
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(boards_router, prefix="/boards", tags=["Boards"])
app.include_router(cards_router, prefix="/cards", tags=["Cards"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Разрешить запросы с frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root(current_user: User = Depends(get_current_user)):
    print(current_user)
    return {"message": "Добро пожаловать в Choice Helper API"}




