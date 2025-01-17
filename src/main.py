from fastapi import FastAPI
from src.boards.router import router as boards_router
from src.cards.router import router as cards_router

app = FastAPI(title="Choice Helper API", version="1.0.0")

# Подключение маршрутов
app.include_router(boards_router, prefix="/boards", tags=["Boards"])
app.include_router(cards_router, prefix="/cards", tags=["Cards"])

@app.get("/")
def root():
    return {"message": "Добро пожаловать в Choice Helper API"}


