from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = "wxl_e_secure_77" # مفتاح أمان مشفر

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, points INTEGER, role TEXT DEFAULT 'user')''')
    # جدول الأكواد
    c.execute('''CREATE TABLE IF NOT EXISTS promo_codes 
                 (code TEXT PRIMARY KEY, value INTEGER, status TEXT DEFAULT 'active')''')
    # حساب الأدمن الخاص بك
    try:
        c.execute("INSERT INTO users (username, points, role) VALUES (?, ?, ?)", ('admin_yasser', 1000, 'admin'))
    except: pass
    conn.commit()
    conn.close()

# --- 2. التصميم (HTML + CSS) ---
# وضعت لك تصميم "نينجا" أحمر وأسود كما تحب
CSS_STYLE = """
<style>
    body { background-color: #0b0f0c; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 0; }
    .container { max-width: 500px; margin: 50px auto; padding: 30px; border: 2px solid #ff0000; border-radius: 20px; background: #111; box-shadow: 0 0 20px #ff0000; }
    h1 { color: #ff0000; text-shadow: 2px 2px #000; }
    input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid #ff0000; background: #000; color: #fff; text-align: center; }
    .btn { background: #ff0000; color: #fff; padding: 12px 30px; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; transition: 0.3s; }
    .btn:hover { background: #b30000; transform: scale(1.05); }
    .points-box { font-size: 30px; color: #00ff00; margin: 20px 0; border: 1px dashed #00ff00; padding: 10px; border-radius: 10px; }
    .footer { margin-top: 20px; font-size: 12px; color: #555; }
</style>
"""

# --- 3. المسارات (Routes) ---

@app.route('/')
def home():
    content = f"""
    {CSS_STYLE}
    <div class="container">
        <h1>WXL-E ACADEMY</h1>
        <p>مرحباً بك في منصة الاحتراف</p>
        <img src="https://i.imgur.com/xO7xY6O.png" width="100" style="border-radius: 50%;"> <br><br>
        <a href="/login" class="btn">تسجيل الدخول / البدء</a>
        <div class="footer">حقوق البرمجة محفوظة @wxl_e</div>
    </div>
    """
    return render_template_string(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        conn = sqlite3.connect('academy.db')
        c = conn.cursor()
        user = c.execute("SELECT id FROM users WHERE username = ?", (user_name,)).fetchone()
        if user:
            user_id = user[0]
        else:
            c.execute("INSERT INTO users (username, points) VALUES (?, ?)", (user_name, 50))
            user_id = c.lastrowid
            conn.commit()
        conn.close()
        return redirect(url_for('dashboard', user_id=user_id))
    
    content = f"""
    {CSS_STYLE}
    <div class="container">
        <h2>ادخل اسمك للبدء</h2>
        <form method="post">
            <input name="username" placeholder="اسم المستخدم" required>
            <button class="btn">دخول</button>
        </form>
    </div>
    """
    return render_template_string(content)

@app.route('/dashboard/<int:user_id>', methods=['GET', 'POST'])
def dashboard(user_id):
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    
    msg = ""
    if request.method == 'POST':
        code = request.form.get('code')
        promo = c.execute("SELECT value FROM promo_codes WHERE code = ? AND status = 'active'", (code,)).fetchone()
        if promo:
            c.execute("UPDATE users SET points = points + ? WHERE id = ?", (promo[0], user_id))
            c.execute("UPDATE promo_codes SET status = 'used' WHERE code = ?", (code,))
            conn.commit()
            msg = "<p style='color:cyan'>✅ تم الشحن بنجاح!</p>"
        else:
            msg = "<p style='color:orange'>❌ الكود خطأ</p>"

    user = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    
    admin_btn = '<br><a href="/admin" class="btn" style="background:gray">لوحة الإدارة</a>' if user[3] == 'admin' else ''

    content = f"""
    {CSS_STYLE}
    <div class="container">
        <h2>لوحة التحكم: {user[1]}</h2>
        <div class="points-box">{user[2]} <small>نقطة</small></div>
        {msg}
        <form method="post">
            <input name="code" placeholder="أدخل كود الشحن">
            <button class="btn">شحن الكود</button>
        </form>
        <hr style="border:0.5px solid #333; margin:20px 0;">
        <h3>الدورات المتاحة</h3>
        <div style="padding:10px; border:1px solid #333;">🔒 كورس SENTINEL-X (500 نقطة)</div>
        {admin_btn}
    </div>
    """
    return render_template_string(content)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        new_code = 'WXL-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        c.execute("INSERT INTO promo_codes (code, value) VALUES (?, 500)")
        conn.commit()

    codes = c.execute("SELECT code FROM promo_codes WHERE status = 'active'").fetchall()
    conn.close()
    
    content = f"""
    {CSS_STYLE}
    <div class="container">
        <h2>لوحة الإدارة 🛠</h2>
        <form method="post"><button class="btn">توليد كود (500 نقطة)</button></form>
        <h4>الأكواد النشطة:</h4>
        <div style="text-align:left; background:#000; padding:10px;">
            {"".join([f"<p>🎟 {x[0]}</p>" for x in codes])}
        </div>
        <br><a href="/" style="color:#fff;">الخروج</a>
    </div>
    """
    return render_template_string(content)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
