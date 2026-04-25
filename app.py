from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import random
import string
import os

app = Flask(__name__)
app.secret_key = "wxl_e_secure_77"

# --- قاعدة البيانات المتطورة ---
def get_db():
    conn = sqlite3.connect('academy.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
                         points INTEGER DEFAULT 100, daily_date TEXT, role TEXT DEFAULT 'user')''')
        conn.execute('''CREATE TABLE IF NOT EXISTS inventory 
                        (user_id INTEGER, item_name TEXT)''')
        # إضافة حسابك كمسؤول
        try:
            conn.execute("INSERT INTO users (username, points, role) VALUES (?, ?, ?)", ('Bouhssoun_Yasser', 5000, 'admin'))
        except: pass
        conn.commit()

# قائمة الأدوات التي أرسلتها (ربط بالملفات الفعلية)
TOOLS = [
    {"id": 1, "name": "IPGRAM", "file": "IPGRAM.py", "cost": 40, "desc": "Instagram IP Extractor"},
    {"id": 2, "name": "DDOS WXLE v2", "file": "DDOS_wxle_v2.0.py", "cost": 80, "desc": "Advanced Attack Framework"},
    {"id": 3, "name": "CyberShield", "file": "password_WXLE_toolkit.py", "cost": 100, "desc": "Security Toolkit"},
    {"id": 4, "name": "WebAnalyzer", "file": "WebAnalyzer Pro v1.4.RUSS.py", "cost": 60, "desc": "Full Recon Engine"}
]

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    return render_template('dashboard.html', user=user, tools=TOOLS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        with get_db() as conn:
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                curr = conn.execute("INSERT INTO users (username) VALUES (?)", (username,))
                user_id = curr.lastrowid
            else:
                user_id = user['id']
            session['user_id'] = user_id
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/download/<int:tool_id>')
def download(tool_id):
    tool = next((t for t in TOOLS if t['id'] == tool_id), None)
    with get_db() as conn:
        user = conn.execute("SELECT points FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if user['points'] >= tool['cost']:
            conn.execute("UPDATE users SET points = points - ? WHERE id = ?", (tool['cost'], session['user_id']))
            conn.commit()
            return send_file(tool['file'], as_attachment=True)
    return "Insufficient Points", 403

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
