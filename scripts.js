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

    let currentBoardId = null;

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
    try {
        const cardsResponse = await fetch(`http://127.0.0.1:8000/boards/${boardId}/cards`);
        const cards = await cardsResponse.json();

        const cardsList = document.getElementById("cardsList");
        cardsList.innerHTML = ""; // Очищаем перед обновлением

        cards.forEach(card => {
            const cardItem = document.createElement("div");
            cardItem.classList.add("card-item");

            const cardText = document.createElement("p");
            cardText.textContent = card.text;

            if (card.image_url) { // Если у карточки есть изображение
                const cardImage = document.createElement("img");
                cardImage.src = `http://127.0.0.1:8000/${card.image_url}`;
                cardImage.alt = "Изображение карточки";
                cardImage.classList.add("card-image");
                cardItem.appendChild(cardImage);
            }

            cardItem.appendChild(cardText);
            cardsList.appendChild(cardItem);
        });
    } catch (error) {
        console.error("Ошибка при загрузке карточек:", error);
        alert("Не удалось загрузить карточки.");
    }
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

    document.getElementById("createCardForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    let formData = new FormData();
    formData.append("text", document.getElementById("cardText").value);
    formData.append("description", document.getElementById("cardDescription").value);
    formData.append("board_id", currentBoardId); // Связываем карточку с доской

    let fileInput = document.getElementById("cardImage");
    if (fileInput.files.length > 0) {
        formData.append("image", fileInput.files[0]); // Добавляем файл в форму
    }

    try {
        let response = await fetch("http://127.0.0.1:8000/cards/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Ошибка при создании карточки");
        }

        closeCreateCardModal(); // Закрываем модалку после успешного создания
        loadBoardCards(currentBoardId); // Перезагружаем карточки
    } catch (error) {
        alert(error.message);
    }
});

        addCardModal.style.display = "none";
        cardText.value = "";
        cardDescription.value = "";

        await loadBoardCards(currentBoardId); // Теперь обновляет список карточек автоматически
    });

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
