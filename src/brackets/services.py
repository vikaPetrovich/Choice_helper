from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from src.brackets.models import Bracket
from src.swipes.models import Swipe
from uuid import UUID
import random
import json
from .schemas import VoteRequest
from sqlalchemy.orm.attributes import flag_modified


async def create_bracket_service(session_id: UUID, db: AsyncSession):
    query = select(Swipe.card_id).where(Swipe.session_id == session_id, Swipe.liked == True)
    result = await db.execute(query)
    liked_cards = [str(row[0]) for row in result.all()]

    if len(liked_cards) < 2:
        raise HTTPException(status_code=400, detail="Недостаточно карточек для турнира")

    random.shuffle(liked_cards)

    # Первая пара — первые 2 карты
    participant_1, participant_2 = liked_cards[:2]
    remaining = liked_cards[2:]

    results = {
        "rounds": [
            {
                "participant_1": participant_1,
                "participant_2": participant_2,
                "winner": None
            }
        ],
        "final_winner": None,
        "remaining": remaining
    }

    bracket = Bracket(session_id=session_id, results=results)
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


async def vote_in_bracket_service(bracket_id: UUID, vote_data: VoteRequest, db: AsyncSession):
    query = select(Bracket).where(Bracket.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalars().first()
    if not bracket:
        raise HTTPException(status_code=404, detail="Турнир не найден")

    results = bracket.results
    rounds = results.get("rounds", [])
    remaining = results.get("remaining", [])

    print("▶️  ДО голосования:")
    print("Текущий раунд:", vote_data.round_number)
    print("Победитель:", vote_data.winner_id)
    print("Осталось карточек:", remaining)

    if vote_data.round_number >= len(rounds):
        raise HTTPException(status_code=400, detail="Некорректный номер раунда")

    # Обновляем победителя
    rounds[vote_data.round_number]["winner"] = str(vote_data.winner_id)
    previous_winner = str(vote_data.winner_id)

    # Добавляем следующий раунд или финал
    if not any(r.get("winner") is None for r in rounds):
        if remaining:
            next_card = remaining.pop(0)
            print("➡️  Добавляем новый раунд с", previous_winner, "vs", next_card)
            rounds.append({
                "participant_1": previous_winner,
                "participant_2": next_card,
                "winner": None
            })
        else:
            print("🏁 Турнир завершён. Финал:", previous_winner)
            results["final_winner"] = previous_winner

    # Сохраняем
    bracket.results = {
        "rounds": rounds,
        "remaining": remaining,
        "final_winner": results.get("final_winner")
    }
    flag_modified(bracket, "results")
    print({
        "rounds": rounds,
        "remaining": remaining,
        "final_winner": results.get("final_winner")})

    await db.commit()
    await db.refresh(bracket)

    print("✅ Сохранено. Всего раундов:", len(rounds))
    return bracket


async def get_next_pair_service(bracket_id: UUID, db: AsyncSession):
    query = select(Bracket).where(Bracket.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalars().first()

    if not bracket:
        raise HTTPException(status_code=404, detail="Турнир не найден")

    rounds = bracket.results.get("rounds", [])
    for idx, rnd in enumerate(rounds):
        if rnd.get("winner") is None:
            return {
                "round_number": idx,
                "participant_1": rnd["participant_1"],
                "participant_2": rnd["participant_2"],
                "finished": False
            }

    # Если все раунды завершены
    return {
        "round_number": None,
        "participant_1": None,
        "participant_2": None,
        "finished": True
    }
