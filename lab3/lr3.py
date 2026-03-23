from flask import Flask, render_template, request, jsonify, session, redirect
import mysql.connector
import time, re, random

app = Flask(__name__)
app.secret_key = "secret_key_123"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Rom2132412",
    "database": "lab3_db"
}


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
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    con = get_db()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(255)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS arrays(
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            original TEXT,
            sorted TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    con.commit()
    cur.close()
    con.close()


# ================== PARSE ==================
def parse_array(text):
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
    con = get_db()
    cur = con.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (data["username"], data["password"])
    )
    user = cur.fetchone()
    cur.close()
    con.close()

    if not user:
        return jsonify(success=False, error="Неверный логин или пароль")

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify(success=True)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (data["username"], data["password"])
        )
        con.commit()
    except:
        return jsonify(success=False, error="Пользователь существует")
    finally:
        cur.close()
        con.close()
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
    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO arrays(user_id,original,sorted)
        VALUES(%s,%s,%s)
    """, (
        session["user_id"],
        ",".join(map(str, arr)),
        ",".join(map(str, tree_sort(arr)))
    ))
    con.commit()
    cur.close()
    con.close()
    return jsonify(success=True)


@app.route("/api/my_arrays")
def my_arrays():
    con = get_db()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT id, sorted, created_at
        FROM arrays WHERE user_id=%s
        ORDER BY created_at DESC
    """, (session["user_id"],))
    rows = cur.fetchall()
    cur.close()
    con.close()
    return jsonify(arrays=[
        {
            "id": r["id"],
            "sorted": r["sorted"],
            "created_at": str(r["created_at"])
        }
        for r in rows
    ])


@app.route("/api/delete_array/<int:array_id>", methods=["DELETE"])
def delete_array(array_id):
    if "user_id" not in session:
        return jsonify(success=False)

    con = get_db()
    cur = con.cursor()

    # Проверяем, что массив принадлежит пользователю
    cur.execute("SELECT user_id FROM arrays WHERE id = %s", (array_id,))
    array = cur.fetchone()

    if not array or array[0] != session["user_id"]:
        cur.close()
        con.close()
        return jsonify(success=False, error="Нет доступа")

    # Удаляем массив
    cur.execute("DELETE FROM arrays WHERE id = %s", (array_id,))
    con.commit()

    cur.close()
    con.close()
    return jsonify(success=True)


# ================== RUN ==================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)