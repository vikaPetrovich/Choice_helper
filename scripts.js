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

    const startSessionButton = document.getElementById("startSessionButton");
    const sessionScreen = document.getElementById("sessionScreen");
    const sessionCardImage = document.getElementById("sessionCardImage");
    const sessionCardText = document.getElementById("sessionCardText");
    const prevCardButton = document.getElementById("prevCard");
    const nextCardButton = document.getElementById("nextCard");
    const exitSessionButton = document.getElementById("exitSession");

    const likedCardsModal = document.getElementById("likedCardsModal");
    const likedCardsList = document.getElementById("likedCardsList");
    const closeLikedCardsModal = document.getElementById("closeLikedCardsModal");
    const confirmEndSessionButton = document.getElementById("confirmEndSession");
    const closeLikedCardsButton = document.getElementById("closeLikedCards");
    const addBoardButton = document.getElementById("addBoardButton");
    const addBoardModal = document.getElementById("addBoardModal");
    const closeAddBoardModal = document.getElementById("closeAddBoardModal");
    const addBoardForm = document.getElementById("addBoardForm");



    let currentBoardId = null;
    let sessionId = null;
    let cards = [];
    let currentCardIndex = 0;
    let isLoadingBoards = false;
    let viewedCards = new Set(); // Для отслеживания уже просмотренных карточек


// Функция создания доски
   async function createBoard(event) {
    event.preventDefault();

    const boardTitle = document.getElementById("boardTitleCreate");
    const boardDescription = document.getElementById("boardDescriptionCreate");

    const title = boardTitle.value.trim();
    const description = boardDescription.value.trim();

    if (!title) {
        alert("Введите название доски");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/boards/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description })
        });

        if (!response.ok) {
            const errorMessage = await response.text();
            throw new Error(`Ошибка создания доски: ${errorMessage}`);
        }

        const newBoard = await response.json();
        console.log("Создана новая доска:", newBoard);

        // Создаем элемент списка (li)
        const li = document.createElement("li");
        li.textContent = newBoard.title;
        li.dataset.id = newBoard.id;

        // Создаем контейнер для кнопок
        const actions = document.createElement("div");
        actions.className = "board-actions";

        // Кнопка редактирования
        const editButton = document.createElement("button");
        editButton.innerHTML = "✏️";
        editButton.className = "icon-button edit";
        editButton.addEventListener("click", (e) => {
            e.stopPropagation();
            currentBoardId = newBoard.id;
            editTitle.value = newBoard.title;
            editDescription.value = newBoard.description;
            editModal.style.display = "flex";
        });

        // Кнопка удаления
        const deleteButton = document.createElement("button");
        deleteButton.innerHTML = "🗑";
        deleteButton.className = "icon-button delete";
        deleteButton.addEventListener("click", async (e) => {
            e.stopPropagation();
            await fetch(`http://127.0.0.1:8000/boards/${newBoard.id}`, { method: "DELETE" });
            li.remove(); // Удаляем доску из списка
        });

        // Добавляем кнопки в контейнер
        actions.appendChild(editButton);
        actions.appendChild(deleteButton);
        li.appendChild(actions);

        // Добавляем обработчик клика для открытия доски
        li.addEventListener("click", async () => {
            currentBoardId = newBoard.id;
            const boardResponse = await fetch(`http://127.0.0.1:8000/boards/${newBoard.id}`);
            const boardData = await boardResponse.json();

            boardTitle.textContent = boardData.title;
            boardDescription.textContent = boardData.description || "Описание отсутствует";

            await loadBoardCards(newBoard.id);

            boardModal.style.display = "flex";
        });

        // Добавляем доску в список
        document.getElementById("boardsList").appendChild(li);

        // Закрываем модальное окно и очищаем форму
        document.getElementById("addBoardModal").style.display = "none";
        boardTitle.value = "";
        boardDescription.value = "";

    } catch (error) {
        console.error("Ошибка при создании доски:", error);
        alert("Ошибка при создании доски.");
    }
}


// Добавляем обработчик событий на форму
document.getElementById("addBoardForm").addEventListener("submit", createBoard);


     addBoardButton.addEventListener("click", () => {
        addBoardModal.style.display = "flex";
    });

    closeAddBoardModal.addEventListener("click", () => {
        addBoardModal.style.display = "none";
    });

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
           cardImageElem.src = `http://127.0.0.1:8000/uploads/${card.image_url.replace(/^uploads\//, "")}`;
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
'!!'
'лайк'
async function sendSwipe(liked) {
        if (!sessionId || currentCardIndex >= cards.length) return;

        // Записываем свайп (лайк/дизлайк)
        await fetch("http://127.0.0.1:8000/swipes/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: sessionId,
                card_id: cards[currentCardIndex].id,
                user_id: null,
                liked: liked
            })
        });

        // Добавляем карточку в список просмотренных
        viewedCards.add(cards[currentCardIndex].id);

        // Поиск новой карточки, которая еще не была просмотрена
        let foundNewCard = false;
        for (let i = 0; i < cards.length; i++) {
            if (!viewedCards.has(cards[i].id)) {
                currentCardIndex = i;
                foundNewCard = true;
                break;
            }
        }

        // Если все карточки просмотрены, показать уведомление
        if (!foundNewCard) {
            alert("Карточки доски закончились. Желаете ли завершить сессию и посмотреть результаты?");
            return;
        }

        updateSessionCard();
    }

    function updateSessionCard() {
        if (currentCardIndex < cards.length) {
            sessionCardText.textContent = cards[currentCardIndex].text;
            sessionCardImage.src = cards[currentCardIndex].image_url || "";
        }
    }

    nextCardButton.addEventListener("click", () => sendSwipe(true));
    prevCardButton.addEventListener("click", () => sendSwipe(false));

 // Функция загрузки лайкнутых карточек
async function loadLikedCards() {
    if (!sessionId) {
        alert("Ошибка: сессия не найдена.");
        return;
    }

    try {
        console.log(`Запрашиваем лайкнутые карточки для сессии: ${sessionId}`);

        // Получаем список всех свайпов в этой сессии
        const swipesResponse = await fetch(`http://127.0.0.1:8000/swipes/session/${sessionId}`);
        if (!swipesResponse.ok) {
            const errorText = await swipesResponse.text();
            console.error("Ошибка запроса свайпов:", errorText);
            alert(`Ошибка при загрузке лайкнутых карточек: ${errorText}`);
            return;
        }
        const swipes = await swipesResponse.json();
        console.log("Список всех свайпов:", swipes);

        // Фильтруем только лайкнутые карточки
        const likedSwipes = swipes.filter(swipe => swipe.liked === true);
        console.log("Отфильтрованные лайкнутые свайпы:", likedSwipes);

        if (likedSwipes.length === 0) {
            likedCardsList.innerHTML = "<p>Вы не лайкнули ни одной карточки.</p>";
            likedCardsModal.style.display = "flex"; // Открываем модальное окно
            return;
        }

        likedCardsList.innerHTML = ""; // Очищаем список перед добавлением

        // Загружаем карточки по `card_id`
        const cardFetchPromises = likedSwipes.map(swipe =>
            fetch(`http://127.0.0.1:8000/cards/${swipe.card_id}`).then(res => res.json())
        );

        const likedCards = await Promise.all(cardFetchPromises);
        console.log("Данные о лайкнутых карточках:", likedCards);

        // Отображаем карточки
        likedCards.forEach(card => {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("liked-card");

    // Изображение карточки
    if (card.image_url) {
        const imageUrl = `http://127.0.0.1:8000/uploads/${card.image_url.replace(/^uploads\//, "")}`;

        const cardImage = document.createElement("img");
        cardImage.classList.add("liked-card-image");
        cardImage.src = imageUrl;
        cardImage.alt = card.text;
        cardDiv.appendChild(cardImage);
    }

    // Название карточки
    const cardTitle = document.createElement("h3");
    cardTitle.classList.add("liked-card-title");
    cardTitle.textContent = card.text || "Название отсутствует";
    cardDiv.appendChild(cardTitle);

    // Описание карточки
    const cardDesc = document.createElement("p");
    cardDesc.classList.add("liked-card-desc");
    cardDesc.textContent = card.short_description || "Описание отсутствует";
    cardDiv.appendChild(cardDesc);

    likedCardsList.appendChild(cardDiv);
});

        likedCardsModal.style.display = "flex"; // Открываем модальное окно
    } catch (error) {
        console.error("Ошибка при загрузке лайкнутых карточек:", error);
        alert("Ошибка при загрузке лайкнутых карточек.");
    }
}




    // Обработчик кнопки "Закончить сессию"
    exitSessionButton.addEventListener("click", loadLikedCards);

    // Обработчик кнопки "Завершить сессию"
    confirmEndSessionButton.addEventListener("click", async () => {
        if (!sessionId) {
            alert("Сессия не найдена.");
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/sessions/${sessionId}`, {
                method: "DELETE"
            });

            if (!response.ok) throw new Error("Ошибка при удалении сессии.");

            alert("Сессия завершена.");
            likedCardsModal.style.display = "none"; // Закрываем окно лайкнутых карточек
            document.getElementById("sessionScreen").style.display = "none"; // Закрываем экран сессии
        } catch (error) {
            console.error("Ошибка при завершении сессии:", error);
            alert("Ошибка при завершении сессии.");
        }
    });

    // Обработчик кнопки "Закрыть"
    closeLikedCardsButton.addEventListener("click", () => {
        likedCardsModal.style.display = "none";
        document.getElementById("sessionScreen").style.display = "none"; // Закрываем экран сессии
    });

    // Обработчик кнопки "×" (закрытие модального окна)
    closeLikedCardsModal.addEventListener("click", () => {
        likedCardsModal.style.display = "none";
        document.getElementById("sessionScreen").style.display = "none"; // Закрываем экран сессии
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
