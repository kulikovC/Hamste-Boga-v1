let tg = window.Telegram.WebApp;
let user = tg?.initDataUnsafe?.user;

window.addEventListener("DOMContentLoaded", () => {
  tg.expand();
  tg.ready();

  if (!user) {
    alert("❌ Не удалось получить данные Telegram. Запусти игру через Telegram.");
    return;
  }

  document.getElementById("login").classList.add("hidden");
  document.getElementById("game").classList.remove("hidden");
  document.getElementById("welcome").textContent = `Привет, ${user.first_name}!`;

  loadStats();
});

function loadStats() {
  fetch(`/api/stats/${user.id}`).then(res => res.json()).then(data => {
    document.getElementById("coins").textContent = `🪙 Монеты: ${data.coins}`;
  });
}

function tap() {
  fetch(`/api/tap/${user.id}`, { method: "POST" }).then(() => loadStats());
}

function upgrade(type) {
  fetch("/api/upgrade", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: user.id, upgrade_type: type })
  }).then(res => {
    if (!res.ok) return res.json().then(d => { throw d.detail });
    return res.json();
  }).then(() => loadStats()).catch(err => alert(err));
}

function claimDaily() {
  fetch(`/api/daily/${user.id}`, { method: "POST" })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      loadStats();
    });
}
