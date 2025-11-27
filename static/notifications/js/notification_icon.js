// ===================== IndexedDB Setup =====================
const DB_NAME = "notificationsDB";
const STORE_NAME = "notifications";
const DB_VERSION = 1;

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };

    request.onsuccess = (event) => resolve(event.target.result);
    request.onerror = (event) => reject(event.target.error);
  });
}

async function saveNotification(notif) {
  const db = await openDB();
  const tx = db.transaction(STORE_NAME, "readwrite");
  const store = tx.objectStore(STORE_NAME);
  store.put(notif);
  return tx.complete;
}

async function getAllNotifications() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const request = store.getAll();

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

// ===================== Render Notification =====================
function renderNotification(notif, prepend = true) {
  const list = document.getElementById("notification-list");

  const div = document.createElement("div");
  div.className = `notification-item ${notif.isRead ? "" : "unread"}`;
  div.dataset.id = notif.id;
  div.innerHTML = `
    <p>${notif.message}</p>
    <small>${new Date(notif.createdAt).toLocaleString()}</small>
    ${notif.isRead ? "" : '<button class="mark-read">Mark as read</button>'}
  `;

  if (prepend) {
    list.insertBefore(div, list.firstChild);
  } else {
    list.appendChild(div);
  }

  if (!notif.isRead) {
    updateBadge(1);
  }
}

// ===================== Badge Update =====================
function updateBadge(change) {
  const badge = document.getElementById("notification-badge");
  let count = parseInt(badge.textContent || "0");
  count += change;
  if (count > 0) {
    badge.style.display = "flex";
    badge.textContent = count;
  } else {
    badge.style.display = "none";
    badge.textContent = "0";
  }
}

// ===================== WebSocket =====================
const socket = new WebSocket("ws://" + window.location.host + "/ws/notifications/");

socket.onmessage = async function (e) {
  const data = JSON.parse(e.data);
  const notif = {
    id: Date.now(),
    message: data.message,
    createdAt: new Date().toISOString(),
    isRead: false
  };

  await saveNotification(notif);
  renderNotification(notif, true);
};

socket.onopen = () => console.log("WebSocket connected");
socket.onclose = () => console.log("WebSocket disconnected");

// ===================== Mark as Read =====================
async function markAsRead(id, item) {
  item.classList.remove("unread");
  const button = item.querySelector(".mark-read");
  if (button) button.remove();
  updateBadge(-1);

  const db = await openDB();
  const tx = db.transaction(STORE_NAME, "readwrite");
  const store = tx.objectStore(STORE_NAME);
  const request = store.get(Number(id));
  request.onsuccess = () => {
    const notif = request.result;
    notif.isRead = true;
    store.put(notif);
  };
  await tx.complete;
}

// ===================== DOMContentLoaded =====================
document.addEventListener("DOMContentLoaded", async () => {
  // Load stored notifications from IndexedDB
  const notifications = await getAllNotifications();
  notifications
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .forEach(notif => renderNotification(notif, false));

  // Toggle panel
  const button = document.getElementById("notification-button");
  const panel = document.getElementById("notification-panel");

  if (button && panel) {
    button.addEventListener("click", (e) => {
      e.stopPropagation();
      panel.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
      if (!button.contains(e.target) && !panel.contains(e.target)) {
        panel.classList.remove("show");
      }
    });
  }

  // Handle "mark as read"
  document.getElementById("notification-list").addEventListener("click", (e) => {
    if (e.target.classList.contains("mark-read")) {
      const item = e.target.closest(".notification-item");
      const id = item.dataset.id;
      markAsRead(id, item);
    }
  });

  // Mark all as read
  document.getElementById("mark-all-read").addEventListener("click", async () => {
    const unreadItems = document.querySelectorAll(".notification-item.unread");
    for (const item of unreadItems) {
      const id = item.dataset.id;
      await markAsRead(id, item);
    }
  });
});

// ===================== Make Notification Icon Draggable =====================
const btn = document.querySelector('.notification-button');
if (btn) {
  let isDragged = false;
  let startX, startY, initialTop, initialRight;

  btn.addEventListener('mousedown', e => {
    isDragged = true;
    startX = e.clientX;
    startY = e.clientY;

    const styles = window.getComputedStyle(btn);
    initialTop = parseInt(styles.top, 10);
    initialRight = parseInt(styles.right, 10);

    e.preventDefault();
  });

  document.addEventListener('mouseup', () => {
    isDragged = false;
  });

  document.addEventListener('mousemove', e => {
    if (!isDragged) return;

    let dx = e.clientX - startX;
    let dy = e.clientY - startY;

    btn.style.top = (initialTop + dy) + 'px';
    btn.style.right = (initialRight - dx) + 'px';

    e.preventDefault();
  });
}
