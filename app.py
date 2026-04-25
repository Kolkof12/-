from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "wxl_e_secret"

# إنشاء قاعدة البيانات
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, points INTEGER, referred_by INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    # الحصول على ID الشخص اللي استدعى (من الرابط)
    ref = request.args.get('ref')
    if ref:
        session['ref_id'] = ref
    return "<h1>مرحباً بك في منصة WXL-E للتبادل</h1><p>سجل الآن للحصول على 50 نقطة!</p><a href='/register'>تسجيل</a>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # إضافة المستخدم الجديد بـ 50 نقطة
        c.execute("INSERT INTO users (email, points) VALUES (?, ?)", (email, 50))
        new_user_id = c.lastrowid
        
        # إذا سجل عن طريق رابط دعوة، نزيد 50 نقطة لصاحب الرابط
        if 'ref_id' in session:
            inviter_id = session['ref_id']
            c.execute("UPDATE users SET points = points + 50 WHERE id = ?", (inviter_id,))
            session.pop('ref_id') # حذف الـ ID من الجلسة بعد الاستعمال
            
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard', user_id=new_user_id))
    
    return '''<form method="post">الإيميل: <input type="email" name="email"><input type="submit" value="ابدأ"></form>'''

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    
    if user:
        # رابط الدعوة الخاص بالمستخدم
        invite_link = f"{request.host_url}?ref={user[0]}"
        return f'''
        <h2>لوحة التحكم</h2>
        <p>الإيميل: {user[1]}</p>
        <p style="color:green; font-weight:bold;">رصيد نقاطك: {user[2]}</p>
        <hr>
        <p>رابط الدعوة الخاص بك (ارسله لتربح 50 نقطة عن كل شخص):</p>
        <input type="text" value="{invite_link}" readonly style="width:300px;">
        '''
    return "خطأ في المستخدم"

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
