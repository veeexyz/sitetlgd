import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates")

# Configuração do banco de dados SQLite
db_path = os.path.join(os.path.dirname(__file__), "chat.db")

def create_tables():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

def get_user_id(username):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    user_id = c.fetchone()
    conn.close()
    return user_id[0] if user_id else None

def create_user(username):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return user_id

def create_message(user_id, content):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, content) VALUES (?, ?)", (user_id, content))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    create_tables()
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    message = request.form["message"]
    username = request.form["username"]
    if not message.strip() or not username.strip():
        return jsonify({"error": "Mensagem e nome de usuário são obrigatórios!"}), 400

    user_id = get_user_id(username)
    if not user_id:
        user_id = create_user(username)

    create_message(user_id, message)
    return "", 204

@app.route("/get_messages")
def get_messages():
    last_message_index = int(request.args.get("last_message_index", 0))
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT messages.id, username, content FROM messages INNER JOIN users ON messages.user_id=users.id WHERE messages.id > ?", (last_message_index,))
    new_messages = [{"id": msg[0], "username": msg[1], "content": msg[2]} for msg in c.fetchall()]
    conn.close()
    return jsonify({"messages": new_messages})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
