from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3

app = FastAPI()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("players.db")
    cur = conn.cursor()
    # Создаём таблицу игроков
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY,
        coins INTEGER DEFAULT 0,
        coins_per_tap INTEGER DEFAULT 1,
        passive_income INTEGER DEFAULT 0,
        last_daily TEXT DEFAULT ""
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Получить игрока по user_id
def get_player(user_id):
    conn = sqlite3.connect("players.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

# Создать игрока, если его ещё нет
def create_if_not_exists(user_id):
    if not get_player(user_id):
        conn = sqlite3.connect("players.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO players (id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()

# Обновить поле игрока
def update_player(user_id, field, value):
    conn = sqlite3.connect("players.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE players SET {field} = ? WHERE id = ?", (value, user_id))
    conn.commit()
    conn.close()

# Модель прокачки
class UpgradeModel(BaseModel):
    user_id: int
    upgrade_type: str  # "tap" или "passive"

# Получение статистики
@app.get("/api/stats/{user_id}")
def stats(user_id: int):
    create_if_not_exists(user_id)
    player = get_player(user_id)
    return {
        "id": player[0],
        "coins": player[1],
        "coins_per_tap": player[2],
        "passive_income": player[3]
    }

# Обработка тапов
@app.post("/api/tap/{user_id}")
def tap(user_id: int):
    create_if_not_exists(user_id)
    player = get_player(user_id)
    new_coins = player[1] + player[2]
    update_player(user_id, "coins", new_coins)
    return {"message": "Монеты добавлены."}

# Улучшения
@app.post("/api/upgrade")
def upgrade(data: UpgradeModel):
    create_if_not_exists(data.user_id)
    player = get_player(data.user_id)
    if player[1] < 10:
        raise HTTPException(status_code=400, detail="Недостаточно монет")

    update_player(data.user_id, "coins", player[1] - 10)

    if data.upgrade_type == "tap":
        update_player(data.user_id, "coins_per_tap", player[2] + 1)
    elif data.upgrade_type == "passive":
        update_player(data.user_id, "passive_income", player[3] + 1)
    else:
        raise HTTPException(status_code=400, detail="Тип прокачки не найден")

    return {"message": "Улучшение успешно."}

# Ежедневная награда
@app.post("/api/daily/{user_id}")
def daily(user_id: int):
    create_if_not_exists(user_id)
    player = get_player(user_id)
    now = datetime.utcnow()
    last = player[4]
    if last:
        last_time = datetime.strptime(last, "%Y-%m-%d")
        if last_time.date() == now.date():
            return {"message": "Ты уже получил награду сегодня!"}

    update_player(user_id, "coins", player[1] + 50)
    update_player(user_id, "last_daily", now.strftime("%Y-%m-%d"))
    return {"message": "Ты получил 50 монет за вход!"}
