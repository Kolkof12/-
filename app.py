from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = "wxl_e_secure_key"

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, points INTEGER, role TEXT DEFAULT 'user')''')
    # جدول أكواد الشحن
    c.execute('''CREATE TABLE IF NOT EXISTS promo_codes 
                 (code TEXT PRIMARY KEY, value INTEGER, status TEXT DEFAULT 'active')''')
    
    # إضافة حساب أدمن افتراضي (إذا لم يكن موجوداً)
    try:
        c.execute("INSERT INTO users (username, points, role) VALUES (?, ?, ?)", ('admin_wxl', 999999, 'admin'))
    except: pass
    
    conn.commit()
    conn.close()

# التصميم الموحد (Dark Style)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>WXL-E ACADEMY</title>
    <style>
        body { background-color: #0d1117; color: white; font-family: sans-serif; text-align: center; }
        .container { max-width: 600px; margin: 30px auto; padding: 20px; border: 1px solid #30363d; border-radius: 15px; background: #161b22; }
        input { width: 80%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: white; }
        .btn { background-color: #238636; color: white; padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
        .admin-btn { background-color: #da3633; }
        .card { background: #0d1117; border: 1px solid #30363d; padding: 15px; margin: 10px; border-radius: 10px; }
        .points { color: #3fb950; font-size: 24px; font-weight: bold; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { border: 1px solid #30363d; padding: 10px; }
    </style>
</head>
<body>
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    ref = request.args.get('ref')
    if ref: session['ref_id'] = ref
    content = '<h1>WXL-E ACADEMY</h1><p>منصة التداول والاختراق الاحترافية</p><a href="/register" class="btn">دخول / تسجيل</a>'
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['username']
        conn = sqlite3.connect('academy.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, points) VALUES (?, ?)", (user_name, 50))
            user_id = c.lastrowid
            if 'ref_id' in session:
                c.execute("UPDATE users SET points = points + 50 WHERE id = ?", (session['ref_id'],))
            conn.commit()
            return redirect(url_for('dashboard', user_id=user_id))
        except: return "الاسم موجود مسبقاً!"
        finally: conn.close()
    return render_template_string(HTML_TEMPLATE, content='<h2>تسجيل جديد</h2><form method="post"><input name="username" placeholder="اسم المستخدم" required><br><button class="btn">ابدأ الآن</button></form>')

@app.route('/dashboard/<int:user_id>', methods=['GET', 'POST'])
def dashboard(user_id):
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    
    # معالجة كود الشحن
    msg = ""
    if request.method == 'POST':
        code = request.form.get('code')
        promo = c.execute("SELECT value FROM promo_codes WHERE code = ? AND status = 'active'", (code,)).fetchone()
        if promo:
            c.execute("UPDATE users SET points = points + ? WHERE id = ?", (promo[0], user_id))
            c.execute("UPDATE promo_codes SET status = 'used' WHERE code = ?", (code,))
            conn.commit()
            msg = f"<p style='color:green'>تم شحن {promo[0]} نقطة بنجاح!</p>"
        else: msg = "<p style='color:red'>كود غير صالح أو مستخدم</p>"

    user = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    
    admin_link = f'<br><a href="/admin" class="btn admin-btn">لوحة الإدارة</a>' if user[3] == 'admin' else ''
    invite_link = f"{request.host_url}?ref={user[0]}"
    
    content = f'''
        <h2>أهلاً {user[1]}</h2>
        <div class="points">{user[2]} نقطة</div>
        {msg}
        <form method="post">
            <input name="code" placeholder="أدخل كود الشحن هنا">
            <button class="btn">تفعيل الكود</button>
        </form>
        <div class="card">
            <p>رابط دعوة الأصدقاء (+50 نقطة):</p>
            <small style="color:#8b949e">{invite_link}</small>
        </div>
        <h3>المتجر</h3>
        <div class="card">🚀 كورس التداول للمحترفين - 500 نقطة</div>
        {admin_link}
    '''
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()
    
    # توليد كود جديد
    if request.method == 'POST' and 'gen_code' in request.form:
        new_code = 'WXL-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        val = request.form.get('value', 100)
        c.execute("INSERT INTO promo_codes (code, value) VALUES (?, ?)", (new_code, val))
        conn.commit()

    users = c.execute("SELECT * FROM users").fetchall()
    codes = c.execute("SELECT * FROM promo_codes WHERE status = 'active'").fetchall()
    conn.close()
    
    content = f'''
        <h2>لوحة التحكم (Admin)</h2>
        <form method="post">
            <input type="number" name="value" placeholder="قيمة الكود (مثلاً 500)">
            <button name="gen_code" class="btn">توليد كود شحن جديد</button>
        </form>
        <h3>الأكواد النشطة:</h3>
        <ul>{"".join([f"<li>{x[0]} ({x[1]} نقطة)</li>" for x in codes])}</ul>
        <h3>المستخدمين:</h3>
        <table><tr><th>ID</th><th>الاسم</th><th>النقاط</th></tr>
        {"".join([f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td></tr>" for u in users])}
        </table>
        <br><a href="/" class="btn">العودة للرئيسية</a>
    '''
    return render_template_string(HTML_TEMPLATE, content=content)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
