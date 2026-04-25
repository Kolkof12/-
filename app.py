from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import uuid

app = Flask(__name__)
CORS(app) # للسماح للموقع (GitHub) بالتواصل مع السيرفر

DB_NAME = 'store.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- 1. تسجيل مستخدم جديد أو جلب بياناته ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    ref_by = data.get('ref_by') # كود الشخص الذي دعاه

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if user:
        return jsonify({"referral_code": user['referral_code'], "points": user['points']})

    # إذا كان مستخدم جديد
    new_ref_code = str(uuid.uuid4())[:8]
    conn.execute('INSERT INTO users (email, referral_code, points) VALUES (?, ?, ?)', 
                 (email, new_ref_code, 0))
    
    # زيادة نقاط الشخص الذي دعاه
    if ref_by:
        conn.execute('UPDATE users SET points = points + 1 WHERE referral_code = ?', (ref_by,))
    
    conn.commit()
    conn.close()
    return jsonify({"referral_code": new_ref_code, "points": 0})

# --- 2. جلب قائمة المنتجات للموقع ---
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])

# --- 3. عملية الشراء ---
@app.route('/api/buy', methods=['POST'])
def buy():
    data = request.json
    email = data.get('email')
    product_id = data.get('product_id')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

    if not user or not product:
        return jsonify({"error": "المعلومات غير صحيحة"}), 404

    if user['points'] < product['price']:
        return jsonify({"error": "نقاطك غير كافية"}), 400

    # جلب عنصر من المخزون لم يُبع بعد
    item = conn.execute('SELECT * FROM inventory WHERE product_id = ? AND is_sold = 0', 
                        (product_id,)).fetchone()

    if not item:
        return jsonify({"error": "نفذت الكمية حالياً"}), 400

    # تنفيذ العملية: خصم النقاط وتحديث حالة المنتج
    conn.execute('UPDATE users SET points = points - ? WHERE email = ?', (product['price'], email))
    conn.execute('UPDATE inventory SET is_sold = 1 WHERE id = ?', (item['id'],))
    
    conn.commit()
    conn.close()

    # هنا يمكنك إضافة كود إرسال إيميل آلي للزبون بـ item['item_details']
    return jsonify({"success": True, "details": item['item_details']})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
