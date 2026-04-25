import os, sqlite3, uuid, time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # السماح بجميع الاتصالات لضمان عمل الموقع على GitHub

DB_PATH = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # جداول المستخدمين، المنتجات، المخزون، والجوائز اليومية
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, points INTEGER, ref_code TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, p_id INTEGER, key_data TEXT, sold INTEGER DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS daily_claims (email TEXT PRIMARY KEY, last_time REAL)')
    
    # إضافة منتجاتك الـ 9 الأساسية بمخزون ضخم
    prods = [
        (1, 'solx_wxle Framework', 150), (2, 'RSS.DDOS.V3', 120),
        (3, 'CyberShield Toolkit', 100), (4, 'WebAnalyzer Pro v1.4', 70),
        (5, 'IPGRAM Extractor', 60), (6, 'Zero-Day Exploit Course', 500),
        (7, 'Trading Academy (0-100)', 400), (8, 'Python Automation Mastery', 250),
        (9, 'Web Pentesting Masterclass', 350)
    ]
    c.executemany('INSERT OR REPLACE INTO products VALUES (?,?,?)', prods)
    
    # توليد 1000 مفتاح لكل منتج لضمان عدم النفاد
    c.execute('SELECT COUNT(*) FROM inventory')
    if c.fetchone()[0] < 1000:
        for p_id in range(1, 10):
            keys = [(p_id, f"WXL-{uuid.uuid4().hex[:12].upper()}") for _ in range(1000)]
            c.executemany('INSERT INTO inventory (p_id, key_data) VALUES (?,?)', keys)
    
    conn.commit()
    conn.close()

@app.route('/api/sync', methods=['POST'])
def sync():
    data = request.json
    email, ref_by = data.get('email'), data.get('ref_by')
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    
    if not user:
        new_ref = str(uuid.uuid4())[:8]
        # تسجيل جديد: إذا جاء عبر رابط، يحصل الداعي على 50 نقطة
        conn.execute('INSERT INTO users (email, points, ref_code) VALUES (?,0,?)', (email, new_ref))
        if ref_by and ref_by != "null":
            conn.execute('UPDATE users SET points = points + 50 WHERE ref_code=?', (ref_by,))
        conn.commit()
        user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    
    res = {"points": user['points'], "ref": user['ref_code']}
    conn.close(); return jsonify(res)

@app.route('/api/daily', methods=['POST'])
def daily():
    email = request.json.get('email')
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    now = time.time()
    last = conn.execute('SELECT last_time FROM daily_claims WHERE email=?', (email,)).fetchone()
    
    if last and (now - last['last_time']) < 86400:
        return jsonify({"success": False, "msg": "عد بعد 24 ساعة!"})
    
    conn.execute('INSERT OR REPLACE INTO daily_claims VALUES (?,?)', (email, now))
    conn.execute('UPDATE users SET points = points + 150 WHERE email=?', (email,))
    conn.commit()
    new_pts = conn.execute('SELECT points FROM users WHERE email=?', (email,)).fetchone()['points']
    conn.close(); return jsonify({"success": True, "points": new_pts})

@app.route('/api/buy', methods=['POST'])
def buy():
    data = request.json
    email, p_id = data.get('email'), data.get('p_id')
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    prod = conn.execute('SELECT * FROM products WHERE id=?', (p_id,)).fetchone()
    
    if user and prod and user['points'] >= prod['price']:
        item = conn.execute('SELECT * FROM inventory WHERE p_id=? AND sold=0', (p_id,)).fetchone()
        if item:
            conn.execute('UPDATE users SET points = points - ? WHERE email=?', (prod['price'], email))
            conn.execute('UPDATE inventory SET sold=1 WHERE id=?', (item['id'],))
            conn.commit(); conn.close()
            return jsonify({"success": True, "key": item['key_data']})
    conn.close(); return jsonify({"success": False, "msg": "نقاط غير كافية أو نفذ المخزون!"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
