from flask import Flask, request, jsonify
from flask_cors import CORS  # ضروري جداً لإصلاح الخطأ
import sqlite3
import uuid

app = Flask(__name__)
CORS(app) # يسمح بالاتصال من أي موقع (مثل GitHub Pages)

DB_NAME = 'store.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        email = data.get('email')
        ref_by = data.get('ref_by') # كود الشخص الذي دعا المستخدم الجديد

        if not email:
            return jsonify({"error": "الإيميل مطلوب"}), 400

        conn = get_db_connection()
        
        # البحث عن المستخدم
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user:
            # إذا كان موجوداً، نكتفي بإعادة بياناته
            res = {"referral_code": user['referral_code'], "points": user['points']}
            conn.close()
            return jsonify(res)

        # إذا كان مستخدم جديد، ننشئ له كود دعوة
        new_ref_code = str(uuid.uuid4())[:8]
        
        # إضافة المستخدم الجديد
        conn.execute('INSERT INTO users (email, referral_code, points) VALUES (?, ?, ?)', 
                     (email, new_ref_code, 0))
        
        # إذا جاء عن طريق رابط دعوة، نزيد نقاط صاحب الرابط
        if ref_by and ref_by != "null" and ref_by != "undefined":
            conn.execute('UPDATE users SET points = points + 1 WHERE referral_code = ?', (ref_by,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"referral_code": new_ref_code, "points": 0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
