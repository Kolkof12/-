import os, sqlite3, uuid, time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# تفعيل CORS للسماح بالاتصال من موقعك على GitHub Pages
CORS(app)

DB_PATH = 'database.db'

def init_db():
    """تهيئة قاعدة البيانات وإضافة المنتجات والمفاتيح تلقائياً"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # إنشاء الجداول الأساسية
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, points INTEGER, ref_code TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, p_id INTEGER, key_data TEXT, sold INTEGER DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS daily_claims (email TEXT PRIMARY KEY, last_time REAL)')
    
    # قائمة المنتجات (أدوات وكورسات)
    prods = [
        (1, 'solx_wxle Framework', 150), 
        (2, 'RSS.DDOS.V3', 120),
        (3, 'CyberShield Toolkit', 100), 
        (4, 'WebAnalyzer Pro v1.4', 70),
        (5, 'IPGRAM Extractor', 60), 
        (6, 'Zero-Day Exploit Course', 500),
        (7, 'Trading Academy (0-100)', 400), 
        (8, 'Python Automation Mastery', 250),
        (9, 'Web Pentesting Masterclass', 350)
    ]
    c.executemany('INSERT OR REPLACE INTO products VALUES (?,?,?)', prods)
    
    # توليد مخزون (1000 مفتاح لكل منتج) إذا كانت قاعدة البيانات فارغة
    c.execute('SELECT COUNT(*) FROM inventory')
    if c.fetchone()[0] < 500:
        for p_id in range(1, 10):
            keys = [(p_id, f"WXL-{uuid.uuid4().hex[:12].upper()}") for _ in range(1000)]
            c.executemany('INSERT INTO inventory (p_id, key_data) VALUES (?,?)', keys)
    
    conn.commit()
    conn.close()

@app.route('/api/sync', methods=['POST'])
def sync():
    """مزامنة بيانات المستخدم والتعامل مع روابط الدعوة (50 نقطة)"""
    data = request.json
    email = data.get('email')
    ref_by = data.get('ref_by') # كود الشخص الداعي
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    
    if not user:
        new_ref = str(uuid.uuid4())[:8]
        # تسجيل جديد
        conn.execute('INSERT INTO users (email, points, ref_code) VALUES (?, 0, ?)', (email, new_ref))
        # إذا سجل عبر رابط دعوة، يحصل الداعي على 50 نقطة
        if ref_by and ref_by != "null" and ref_by != "undefined":
            conn.execute('UPDATE users SET points = points + 50 WHERE ref_code=?', (ref_by,))
        conn.commit()
        user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    
    res = {"points": user['points'], "ref": user['ref_code']}
    conn.close()
    return jsonify(res)

@app.route('/api/daily', methods=['POST'])
def daily():
    """المطالبة بالهدية اليومية (150 نقطة كل 24 ساعة)"""
    email = request.json.get('email')
    if not email: return jsonify({"success": False, "msg": "Email Required"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    now = time.time()
    
    last = conn.execute('SELECT last_time FROM daily_claims WHERE email=?', (email,)).fetchone()
    
    # فحص مرور 24 ساعة (86400 ثانية)
    if last and (now - last['last_time']) < 86400:
        hours_left = int((86400 - (now - last['last_time'])) / 3600)
        return jsonify({"success": False, "msg": f"عد بعد {hours_left} ساعة!"})
    
    # تحديث النقاط ووقت المطالبة
    conn.execute('INSERT OR REPLACE INTO daily_claims VALUES (?,?)', (email, now))
    conn.execute('UPDATE users SET points = points + 150 WHERE email=?', (email,))
    conn.commit()
    
    new_pts = conn.execute('SELECT points FROM users WHERE email=?', (email,)).fetchone()['points']
    conn.close()
    return jsonify({"success": True, "points": new_pts})

@app.route('/api/buy', methods=['POST'])
def buy():
    """عملية الشراء وخصم النقاط وتسليم المفتاح"""
    data = request.json
    email, p_id = data.get('email'), data.get('p_id')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    prod = conn.execute('SELECT * FROM products WHERE id=?', (p_id,)).fetchone()
    
    if user and prod and user['points'] >= prod['price']:
        # سحب مفتاح غير مباع من المخزون
        item = conn.execute('SELECT * FROM inventory WHERE p_id=? AND sold=0', (p_id,)).fetchone()
        if item:
            conn.execute('UPDATE users SET points = points - ? WHERE email=?', (prod['price'], email))
            conn.execute('UPDATE inventory SET sold=1 WHERE id=?', (item['id'],))
            conn.commit()
            conn.close()
            return jsonify({"success": True, "key": item['key_data']})
            
    conn.close()
    return jsonify({"success": False, "msg": "نقاطك لا تكفي أو انتهى المخزون!"})

if __name__ == '__main__':
    init_db()
    # التشغيل على المنفذ المخصص من Render
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
