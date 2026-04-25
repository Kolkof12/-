@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    ref_by = data.get('ref_by')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if user:
        # إذا كان موجوداً نرجع بياناته الحالية
        return jsonify({"referral_code": user['referral_code'], "points": user['points']})

    # إنشاء مستخدم جديد
    new_code = str(uuid.uuid4())[:8]
    conn.execute('INSERT INTO users (email, referral_code, points) VALUES (?, ?, 0)', (email, new_code))
    
    # زيادة نقاط الشخص الذي دعاه (إذا وجد)
    if ref_by:
        conn.execute('UPDATE users SET points = points + 1 WHERE referral_code = ?', (ref_by,))
    
    conn.commit()
    conn.close()
    return jsonify({"referral_code": new_code, "points": 0})
