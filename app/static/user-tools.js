const RIP_SESSION_KEY = "rip_supabase_session";

function ripReadSession() {
  try {
    return JSON.parse(localStorage.getItem(RIP_SESSION_KEY));
  } catch {
    return null;
  }
}

function ripSetStatus(target, message) {
  if (!target) return;
  target.textContent = message;
  target.classList.remove("hidden");
}

function ripRequireSession(target) {
  const session = ripReadSession();
  if (!session || !session.access_token) {
    ripSetStatus(target, "Войдите через Google в личном кабинете, затем повторите действие.");
    return null;
  }
  return session;
}

async function ripApiFetch(session, url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${session.access_token}`,
      ...(options.headers || {})
    }
  });

  if (!response.ok) {
    throw new Error("Не удалось выполнить действие");
  }
  if (response.status === 204) return null;
  return response.json();
}

function ripPublicationPayload(button) {
  return JSON.parse(button.dataset.publication);
}

function ripSearchPayload(button) {
  return JSON.parse(button.dataset.search);
}

function ripTopicPayload(button) {
  return JSON.parse(button.dataset.topic);
}

async function ripSaveFavorite(button, statusTarget) {
  const session = ripRequireSession(statusTarget);
  if (!session) return;
  ripSetStatus(statusTarget, "Сохраняем статью...");
  await ripApiFetch(session, "/api/v1/favorites", {
    method: "POST",
    body: JSON.stringify({ publication: ripPublicationPayload(button) })
  });
  ripSetStatus(statusTarget, "Статья добавлена в избранное. Она появится в личном кабинете.");
}

async function ripSaveSearch(button, statusTarget) {
  const session = ripRequireSession(statusTarget);
  if (!session) return;
  ripSetStatus(statusTarget, "Сохраняем поиск...");
  await ripApiFetch(session, "/api/v1/saved-searches", {
    method: "POST",
    body: JSON.stringify(ripSearchPayload(button))
  });
  ripSetStatus(statusTarget, "Поиск сохранен. В личном кабинете по нему можно вернуться к результатам.");
}

async function ripAddToCollection(button, statusTarget) {
  const session = ripRequireSession(statusTarget);
  if (!session) return;
  ripSetStatus(statusTarget, "Добавляем статью в подборку...");

  let collections = await ripApiFetch(session, "/api/v1/collections");
  if (!collections.length) {
    const created = await ripApiFetch(session, "/api/v1/collections", {
      method: "POST",
      body: JSON.stringify({
        name: "Моя подборка",
        description: "Статьи, которые вы отобрали для чтения"
      })
    });
    collections = [created];
  }

  await ripApiFetch(session, `/api/v1/collections/${collections[0].id}/items`, {
    method: "POST",
    body: JSON.stringify({ publication: ripPublicationPayload(button) })
  });
  ripSetStatus(statusTarget, `Статья добавлена в подборку "${collections[0].name}".`);
}

async function ripSubscribeTopic(button, statusTarget) {
  const session = ripRequireSession(statusTarget);
  if (!session) return;
  ripSetStatus(statusTarget, "Оформляем подписку на тему...");
  await ripApiFetch(session, "/api/v1/subscriptions", {
    method: "POST",
    body: JSON.stringify({ topic: ripTopicPayload(button) })
  });
  ripSetStatus(statusTarget, "Подписка добавлена. Тема появится в личном кабинете.");
}

document.addEventListener("click", async (event) => {
  const favoriteButton = event.target.closest("[data-action='save-favorite']");
  const searchButton = event.target.closest("[data-action='save-search']");
  const collectionButton = event.target.closest("[data-action='add-to-collection']");
  const topicButton = event.target.closest("[data-action='subscribe-topic']");
  const button = favoriteButton || searchButton || collectionButton || topicButton;
  if (!button) return;

  event.preventDefault();
  const statusTarget = document.querySelector(button.dataset.statusTarget || "#tool-status");

  try {
    if (favoriteButton) await ripSaveFavorite(button, statusTarget);
    if (searchButton) await ripSaveSearch(button, statusTarget);
    if (collectionButton) await ripAddToCollection(button, statusTarget);
    if (topicButton) await ripSubscribeTopic(button, statusTarget);
  } catch {
    ripSetStatus(statusTarget, "Действие не выполнено. Обновите страницу и попробуйте снова.");
  }
});
