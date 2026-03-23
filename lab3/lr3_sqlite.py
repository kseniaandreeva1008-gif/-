from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
import time
import re
import random
import os

app = Flask(__name__)
app.secret_key = "secret_key_123"

# Путь к базе данных SQLite
DATABASE = os.path.join(os.path.dirname(__file__), 'lab3_db.sqlite')


# ================== SORT ==================
def tree_sort(arr):
    if len(arr) <= 1:
        return arr
    root = arr[0]
    left = [x for x in arr[1:] if x < root]
    right = [x for x in arr[1:] if x >= root]
    return tree_sort(left) + [root] + tree_sort(right)


# ================== DB ==================
def get_db():
    """Подключение к SQLite базе данных"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Чтобы можно было обращаться по именам колонок
    return conn


def init_db():
    """Инициализация базы данных"""
    conn = get_db()
    cursor = conn.cursor()

    # Создание таблицы users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Создание таблицы arrays
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arrays(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original TEXT,
            sorted TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ================== PARSE ==================
def parse_array(text):
    """Парсинг строки в массив чисел"""
    text = text.replace(" ", ",")
    if not re.fullmatch(r"[0-9,\s\-]+", text):
        raise ValueError("Неверный формат массива")
    return [int(x) for x in text.split(",") if x.strip()]


# ================== AUTH ==================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data["username"], data["password"])
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify(success=False, error="Неверный логин или пароль")

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify(success=True)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users(username, password) VALUES(?, ?)",
            (data["username"], data["password"])
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify(success=False, error="Пользователь существует")
    finally:
        conn.close()
    return jsonify(success=True)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify(success=True)


# ================== UI ==================
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html", username=session["username"])


# ================== API ==================
@app.route("/api/generate", methods=["POST"])
def generate():
    d = request.get_json()
    arr = [random.randint(d["min"], d["max"]) for _ in range(d["size"])]
    return jsonify(success=True, array=arr)


@app.route("/api/sort", methods=["POST"])
def sort_array():
    try:
        arr = parse_array(request.get_json()["array"])
    except Exception as e:
        return jsonify(success=False, error=str(e))

    t = time.time()
    sorted_arr = tree_sort(arr)
    return jsonify(success=True, original=arr, sorted=sorted_arr, time=round(time.time() - t, 6))


@app.route("/api/save", methods=["POST"])
def save():
    if "user_id" not in session:
        return jsonify(success=False)

    arr = parse_array(request.get_json()["array"])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO arrays(user_id, original, sorted)
        VALUES(?, ?, ?)
    """, (
        session["user_id"],
        ",".join(map(str, arr)),
        ",".join(map(str, tree_sort(arr)))
    ))
    conn.commit()
    conn.close()
    return jsonify(success=True)


@app.route("/api/my_arrays")
def my_arrays():
    if "user_id" not in session:
        return jsonify(success=False, error="Не авторизован")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, sorted, created_at
        FROM arrays WHERE user_id=?
        ORDER BY created_at DESC
    """, (session["user_id"],))
    rows = cursor.fetchall()
    conn.close()

    return jsonify(arrays=[
        {
            "id": r["id"],
            "sorted": r["sorted"],
            "created_at": r["created_at"]
        }
        for r in rows
    ])


@app.route("/api/delete_array/<int:array_id>", methods=["DELETE"])
def delete_array(array_id):
    if "user_id" not in session:
        return jsonify(success=False, error="Не авторизован")

    conn = get_db()
    cursor = conn.cursor()

    # Проверяем, что массив принадлежит пользователю
    cursor.execute("SELECT user_id FROM arrays WHERE id = ?", (array_id,))
    array = cursor.fetchone()

    if not array or array["user_id"] != session["user_id"]:
        conn.close()
        return jsonify(success=False, error="Нет доступа")

    # Удаляем массив
    cursor.execute("DELETE FROM arrays WHERE id = ?", (array_id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)


# ================== RUN ==================
if __name__ == "__main__":
    # Создаем базу данных при запуске
    init_db()
    print(f"База данных создана: {DATABASE}")
    print("Запуск сервера на http://127.0.0.1:5000")
    app.run(debug=True)