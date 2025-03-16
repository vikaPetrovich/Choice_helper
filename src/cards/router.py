'''
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import shutil
import os
from src.cards.services import create_card_service
from src.cards.schemas import CardResponse
from src.db import get_db

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
'''
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import shutil
import os
from src.cards.services import create_card_service
from src.cards.schemas import CardResponse
from src.db import get_db
from src.cards.schemas import CardCreate, CardUpdate
import time
router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import shutil
import os
from src.cards.services import create_card_service, get_all_cards_service,get_card_service,update_card_service, delete_card_service
from src.cards.schemas import CardCreate, CardResponse
from src.db import get_db

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

'''
@router.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"image_url": file_location}
'''
@router.post("/", response_model=CardResponse)
async def create_card(
    text: str = Form(...),
    short_description: str = Form(""),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    image_url = None
    if image:
        timestamp = int(time.time())
        file_location = f"{UPLOAD_DIR}/{timestamp}_{image.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = file_location

    card_data = CardCreate(
        text=text,
        short_description=short_description,
        image_url=image_url
    )

    return await create_card_service(card_data, db)


'''
@router.post("/upload_image/")

async def upload_image(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"image_url": file_location}

@router.post("/", response_model=CardResponse)
async def create_card(card: CardCreate, db: AsyncSession = Depends(get_db)):
    return await create_card_service(card_data=card, db=db)
'''

@router.get("/", response_model=list[CardResponse])
async def get_cards(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_all_cards_service(skip=skip, limit=limit, db=db)

@router.get("/{card_id}", response_model=CardResponse)
async def get_card(card_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_card_service(card_id=card_id, db=db)

@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: UUID,
    text: str = Form(None),
    short_description: str = Form(None),
    status: str = Form(None),
    image: UploadFile = File(None),  # Файл загружается как `multipart/form-data`
    db: AsyncSession = Depends(get_db),
):
    return await update_card_service(
        card_id=card_id, text=text, short_description=short_description, status=status, image=image, db=db)

@router.delete("/{card_id}")
async def delete_card(card_id: UUID, db: AsyncSession = Depends(get_db)):
    return await delete_card_service(card_id=card_id, db=db)
