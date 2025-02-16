from fastapi import FastAPI
from src.boards.router import router as boards_router
from src.cards.router import router as cards_router
from src.sessions.router import router as sessions_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.swipes.router import router as swipes_router


app = FastAPI(title="Choice Helper API", version="1.0.0")
app.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(swipes_router, prefix="/swipes", tags=["Swipes"])
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

@app.get("/")
def root():
    return {"message": "Добро пожаловать в Choice Helper API"}


