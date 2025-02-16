document.addEventListener("DOMContentLoaded", () => {
    const boardsList = document.getElementById("boardsList");
    const loadBoardsButton = document.getElementById("loadBoards");

    const editModal = document.getElementById("editModal");
    const closeEditModal = document.getElementById("closeEditModal");
    const editForm = document.getElementById("editForm");
    const editTitle = document.getElementById("editTitle");
    const editDescription = document.getElementById("editDescription");

    const boardModal = document.getElementById("boardModal");
    const closeBoardModal = document.getElementById("closeBoardModal");
    const boardTitle = document.getElementById("boardTitle");
    const boardDescription = document.getElementById("boardDescription");
    const cardsList = document.getElementById("cardsList");

    const addCardModal = document.getElementById("addCardModal");
    const closeAddCardModal = document.getElementById("closeAddCardModal");
    const addCardForm = document.getElementById("addCardForm");
    const cardText = document.getElementById("cardText");
    const cardImage = document.getElementById("cardImage");
    const openAddCardModal = document.getElementById("openAddCardModal");

    '////'


    const startSessionButton = document.getElementById("startSessionButton");
    const sessionScreen = document.getElementById("sessionScreen");
    const sessionCardImage = document.getElementById("sessionCardImage");
    const sessionCardText = document.getElementById("sessionCardText");
    const prevCardButton = document.getElementById("prevCard");
    const nextCardButton = document.getElementById("nextCard");
    const exitSessionButton = document.getElementById("exitSession");

     '////'
    let currentBoardId = null;
     '////'
    let sessionId = null;
    let cards = [];
    let currentCardIndex = 0;
    let isLoadingBoards = false;
     '////'
    async function loadBoards() {
        const response = await fetch("http://127.0.0.1:8000/boards");
        const boards = await response.json();

        boardsList.innerHTML = "";
        boards.forEach(board => {
            const li = document.createElement("li");
            li.textContent = board.title;
            li.dataset.id = board.id;

            const actions = document.createElement("div");
            actions.className = "board-actions";

            const editButton = document.createElement("button");
            editButton.innerHTML = "✏️";
            editButton.className = "icon-button edit";
            editButton.addEventListener("click", (e) => {
                e.stopPropagation();
                currentBoardId = board.id;
                editTitle.value = board.title;
                editDescription.value = board.description;
                editModal.style.display = "flex";
            });

            const deleteButton = document.createElement("button");
            deleteButton.innerHTML = "🗑";
            deleteButton.className = "icon-button delete";
            deleteButton.addEventListener("click", async (e) => {
                e.stopPropagation();
                await fetch(`http://127.0.0.1:8000/boards/${board.id}`, { method: "DELETE" });
                loadBoards();
            });

            actions.appendChild(editButton);
            actions.appendChild(deleteButton);
            li.appendChild(actions);

            li.addEventListener("click", async () => {
                currentBoardId = board.id;
                const boardResponse = await fetch(`http://127.0.0.1:8000/boards/${board.id}`);
                const boardData = await boardResponse.json();

                boardTitle.textContent = boardData.title;
                boardDescription.textContent = boardData.description || "Описание отсутствует";

                await loadBoardCards(board.id);

                boardModal.style.display = "flex";
            });

            boardsList.appendChild(li);
        });
    }

async function loadBoardCards(boardId) {
    const response = await fetch(`http://127.0.0.1:8000/boards/${boardId}/cards`);
    const cards = await response.json();

    cardsList.innerHTML = "";
    cards.forEach(card => {
        const cardItem = document.createElement("div");
        cardItem.classList.add("card-item");

        const cardTextElem = document.createElement("p");
        cardTextElem.textContent = card.text;

        if (card.image_url) {
            const cardImageElem = document.createElement("img");
            cardImageElem.src = `http://127.0.0.1:8000/${card.image_url}`;
            cardImageElem.alt = "Card Image";
            cardImageElem.classList.add("card-image");
            cardItem.appendChild(cardImageElem);
        }

        cardItem.appendChild(cardTextElem);
        cardsList.appendChild(cardItem);
    });
}


    editForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            await fetch(`http://127.0.0.1:8000/boards/${currentBoardId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title: editTitle.value,
                    description: editDescription.value
                })
            });

            editModal.style.display = "none";
            loadBoards();
        } catch (error) {
            console.error("Ошибка при сохранении изменений:", error);
            alert("Ошибка при сохранении доски.");
        }
    });

    addCardForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("text", cardText.value.trim());
    formData.append("short_description", cardDescription.value.trim());

    if (cardImage.files[0]) {
        formData.append("image", cardImage.files[0]);
    }

    const response = await fetch("http://127.0.0.1:8000/cards/", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        alert("Ошибка при создании карточки.");
        return;
    }

    const createdCard = await response.json();

    // Привязка карточки к текущей доске
    const boardAttachResponse = await fetch(`http://127.0.0.1:8000/boards/${currentBoardId}/cards/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ card_id: createdCard.id })
    });

    if (!boardAttachResponse.ok) {
        alert("Ошибка при привязке карточки к доске.");
        return;
    }

    addCardModal.style.display = "none";
    cardText.value = "";
    cardDescription.value = "";
    cardImage.value = "";

    await loadBoardCards(currentBoardId);
});


'////'
startSessionButton.addEventListener("click", async (e) => {
    e.preventDefault();

    if (!currentBoardId) {
        alert("Ошибка: не удалось определить ID доски.");
        return;
    }

    try {
        // Создаем новую сессию
        const response = await fetch("http://127.0.0.1:8000/sessions/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                board_id: currentBoardId,
                type: "individual"
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Ошибка при создании сессии:", errorText);
            alert(`Ошибка при создании сессии: ${errorText}`);
            return;
        }

        const createdSession = await response.json();
        sessionId = createdSession.id; // Запоминаем ID сессии

        // Загружаем карточки доски
        const cardsResponse = await fetch(`http://127.0.0.1:8000/boards/${currentBoardId}/cards`);
        cards = await cardsResponse.json();

        if (cards.length === 0) {
            alert("В этой доске нет карточек.");
            return;
        }

        currentCardIndex = cards.length - 1; // Показываем последнюю карточку
        updateSessionCard();

        sessionScreen.style.display = "flex"; // Открываем окно сессии
        boardModal.style.display = "none"; // Закрываем доску
    } catch (error) {
        console.error("Ошибка при отправке запроса:", error);
        alert("Ошибка при отправке запроса.");
    }
});

// Обновление отображаемой карточки
function updateSessionCard() {
    if (cards.length === 0 || currentCardIndex < 0 || currentCardIndex >= cards.length) {
        sessionCardImage.src = "";
        sessionCardText.textContent = "Нет карточек";
        return;
    }

    const card = cards[currentCardIndex];
    sessionCardImage.src = card.image_url ? `http://127.0.0.1:8000/${card.image_url}` : "";
    sessionCardText.textContent = card.text;
}

// Кнопка "Вперед"
nextCardButton.addEventListener("click", () => {
    if (currentCardIndex < cards.length - 1) {
        currentCardIndex++;
        updateSessionCard();
    }
});

// Кнопка "Назад"
prevCardButton.addEventListener("click", () => {
    if (currentCardIndex > 0) {
        currentCardIndex--;
        updateSessionCard();
    }
});

// Завершение сессии (удаление сессии)
exitSessionButton.addEventListener("click", async () => {
    if (!sessionId) {
        alert("Сессия не найдена.");
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/sessions/${sessionId}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            throw new Error("Ошибка при удалении сессии.");
        }

        alert("Сессия завершена.");
        sessionScreen.style.display = "none"; // Закрываем окно сессии
    } catch (error) {
        console.error("Ошибка при удалении сессии:", error);
        alert("Ошибка при завершении сессии.");
    }
});


'///'

    openAddCardModal.addEventListener("click", () => {
        addCardModal.style.display = "flex";
    });

    closeAddCardModal.addEventListener("click", () => {
        addCardModal.style.display = "none";
    });

    closeBoardModal.addEventListener("click", () => {
        boardModal.style.display = "none";
    });

    closeEditModal.addEventListener("click", () => {
    editModal.style.display = "none";
    });

    loadBoardsButton.addEventListener("click", loadBoards);
    loadBoards();
});
