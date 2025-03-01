from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from src.brackets.models import Bracket
from src.swipes.models import Swipe
from uuid import UUID
import random
import json

async def create_bracket_service(session_id: UUID, db: AsyncSession):
    # Получаем лайкнутые карточки
    query = select(Swipe.card_id).where(Swipe.session_id == session_id, Swipe.liked == True)
    result = await db.execute(query)
    liked_cards = [str(row[0]) for row in result.all()]

    if len(liked_cards) < 2:
        raise HTTPException(status_code=400, detail="Недостаточно карточек для турнира")

    # Перемешиваем карточки и формируем пары
    random.shuffle(liked_cards)
    pairs = {str(i): {"pair": liked_cards[i:i+2], "winner": None} for i in range(0, len(liked_cards), 2)}

    bracket = Bracket(session_id=session_id, structure={"round_1": pairs}, results={})
    db.add(bracket)
    await db.commit()
    await db.refresh(bracket)

    return bracket

async def get_bracket_service(bracket_id: UUID, db: AsyncSession):
    query = select(Bracket).where(Bracket.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalars().first()

    if not bracket:
        raise HTTPException(status_code=404, detail="Турнирная сетка не найдена")

    return bracket


async def vote_in_bracket_service(bracket_id: UUID, vote_data, db: AsyncSession):
    query = select(Bracket).where(Bracket.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalars().first()

    if not bracket:
        raise HTTPException(status_code=404, detail="Турнирная сетка не найдена")

    round_key = f"round_{vote_data.round_number}"
    if round_key not in bracket.structure:
        raise HTTPException(status_code=400, detail="Некорректный раунд")

    # Заполняем победителей
    for match_id, winner_id in vote_data.votes.items():
        if match_id in bracket.structure[round_key]:
            bracket.structure[round_key][match_id]["winner"] = str(winner_id)

    # Формируем следующий раунд
    winners = [pair["winner"] for pair in bracket.structure[round_key].values() if pair["winner"]]
    if len(winners) > 1:
        next_round = f"round_{vote_data.round_number + 1}"
        new_pairs = {}

        i = 0
        while i < len(winners):
            if i + 1 < len(winners):
                new_pairs[str(i)] = {"pair": [winners[i], winners[i + 1]], "winner": None}
            else:
                new_pairs[str(i)] = {"pair": [winners[i]], "winner": None}
            i += 2

        bracket.structure[next_round] = new_pairs

    # Обновляем результаты, не затирая старые
    if round_key not in bracket.results:
        bracket.results[round_key] = {}

    bracket.results[round_key].update(vote_data.votes)

    # Сохраняем изменения в базе
    await db.commit()
    await db.refresh(bracket)

    return bracket

