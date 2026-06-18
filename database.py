import sqlite3

db = sqlite3.connect("bot.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    accepted INTEGER DEFAULT 0,
    warns INTEGER DEFAULT 0,
    banned INTEGER DEFAULT 0
)
""")

db.commit()

def create_user(user_id):
    cur.execute(
        "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
        (user_id,)
    )
    db.commit()

def get_user(user_id):
    create_user(user_id)

    cur.execute(
        "SELECT accepted,warns,banned FROM users WHERE user_id=?",
        (user_id,)
    )

    return cur.fetchone()

def accept_rules(user_id):
    cur.execute(
        "UPDATE users SET accepted=1 WHERE user_id=?",
        (user_id,)
    )
    db.commit()

def add_warn(user_id):
    cur.execute(
        "UPDATE users SET warns=warns+1 WHERE user_id=?",
        (user_id,)
    )
    db.commit()

def ban_user(user_id):
    cur.execute(
        "UPDATE users SET banned=1 WHERE user_id=?",
        (user_id,)
    )
    db.commit()
