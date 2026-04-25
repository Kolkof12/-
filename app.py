from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "wxl_e_secure_key" # مفتاح لتأمين الجلسات

# إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect('users_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            points INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    # التقاط الـ ID الخاص بالداعي من الرابط (مثال: site.com/?ref=1)
    ref_id = request.args.get('ref')
    if ref_id:
        session['referrer'] = ref_id
    return "<h1>مرحباً بك في المنصة</h1><a href='/register'>سجل الآن واحصل على 50 نقطة</a>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['username']
        
        conn = sqlite3.connect('users_data.db')
        cursor = conn.cursor()
        
        try:
            # 1. إضافة المستخدم الجديد مع 50 نقطة هدية ترحيبية
            cursor.execute("INSERT INTO users (username, points) VALUES (?, ?)", (user_name, 50))
            new_user_id = cursor.lastrowid
            
            # 2. التحقق إذا كان هناك "داعي" لهذا المستخدم
            if 'referrer' in session:
                inviter_id = session['referrer']
                # إضافة 50 نقطة للشخص الذي أرسل الرابط
                cursor.execute("UPDATE users SET points = points + 50 WHERE id = ?", (inviter_id,))
                session.pop('referrer') # تنظيف الجلسة
                
            conn.commit()
            return redirect(url_for('dashboard', uid=new_user_id))
        except sqlite3.IntegrityError:
            return "الإسم مستخدم بالفعل، اختر اسماً آخر."
        finally:
            conn.close()
            
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="اختر اسم مستخدم" required>
            <button type="submit">إنشاء حساب</button>
        </form>
    '''

@app.route('/dashboard/<int:uid>')
def dashboard(uid):
    conn = sqlite3.connect('users_data.db')
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    conn.close()
    
    if user:
        # إنشاء رابط الدعوة الخاص بهذا المستخدم
        my_ref_link = f"{request.host_url}?ref={user[0]}"
        return f'''
            <div style="text-align:center; margin-top:50px; font-family:Arial;">
                <h2>لوحة التحكم: {user[1]}</h2>
                <h3 style="color:green;">رصيدك الحالي: {user[2]} نقطة</h3>
                <hr>
                <p>شارك هذا الرابط لتربح 50 نقطة عن كل صديق يسجل:</p>
                <input type="text" value="{my_ref_link}" readonly style="width:300px; padding:10px;">
                <br><br>
                <button>تصفح الحسابات والكورسات</button>
            </div>
        '''
    return "المستخدم غير موجود"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
