import os, sqlite3, uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = 'store.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # إنشاء الجداول
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, points INTEGER, ref_code TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, p_id INTEGER, details TEXT, sold INTEGER DEFAULT 0)')
    
    # إضافة المنتجات (الأدوات والكورسات)
    items = [
        (1, 'solx_wxle Framework', 'Tools', 150),
        (2, 'RSS.DDOS.V3', 'Tools', 120),
        (3, 'CyberShield Toolkit', 'Tools', 100),
        (4, 'WebAnalyzer Pro v1.4', 'Tools', 70),
        (5, 'IPGRAM Instagram Extractor', 'Tools', 60),
        (6, 'Zero-Day Exploit Course', 'Courses', 500),
        (7, 'Trading Academy (Professional)', 'Courses', 400),
        (8, 'Python Automation Mastery', 'Courses', 250),
        (9, 'Web Pentesting Masterclass', 'Courses', 350)
    ]
    c.executemany('INSERT OR REPLACE INTO products VALUES (?,?,?,?)', items)
    
    # إضافة مخزون ضخم (أمثلة لـ 1000 نسخة لكل منتج)
    for i in range(1, 10):
        for _ in range(1000):
            c.execute('INSERT INTO inventory (p_id, details) VALUES (?,?)', (i, f"Product_Key_{uuid.uuid4().hex[:10]}"))
            
    conn.commit()
    conn.close()

@app.route('/api/sync', methods=['POST'])
def sync():
    data = request.json
    email, ref_by = data.get('email'), data.get('ref_by')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    
    if not user:
        new_ref = str(uuid.uuid4())[:8]
        conn.execute('INSERT INTO users (email, points, ref_code) VALUES (?,0,?)', (email, new_ref))
        if ref_by and ref_by != "null":
            conn.execute('UPDATE users SET points = points + 5 WHERE ref_code=?', (ref_by,))
        conn.commit()
        user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    
    res = {"points": user['points'], "ref": user['ref_code']}
    conn.close()
    return jsonify(res)

@app.route('/api/buy', methods=['POST'])
def buy():
    data = request.json
    email, p_id = data.get('email'), data.get('p_id')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    prod = conn.execute('SELECT * FROM products WHERE id=?', (p_id,)).fetchone()
    
    if user['points'] >= prod['price']:
        item = conn.execute('SELECT * FROM inventory WHERE p_id=? AND sold=0', (p_id,)).fetchone()
        if item:
            conn.execute('UPDATE users SET points = points - ? WHERE email=?', (prod['price'], email))
            conn.execute('UPDATE inventory SET sold=1 WHERE id=?', (item['id'],))
            conn.commit()
            return jsonify({"success": True, "data": item['details']})
    return jsonify({"success": False, "msg": "Insufficient points!"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
