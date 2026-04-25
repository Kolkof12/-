import sqlite3

def add_items():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    # قائمة الأدوات التي حددناها بناءً على ملفاتك
    tools = [
        ('solx_wxle Framework', 'Tools', 150),
        ('RSS.DDOS.V3', 'Tools', 120),
        ('CyberShield Toolkit', 'Tools', 100),
        ('WebAnalyzer Pro', 'Tools', 70),
        ('IPGRAM Extractor', 'Tools', 60)
    ]

    # قائمة الكورسات
    courses = [
        ('Advanced Zero-Day Exploit', 'Courses', 500),
        ('Professional Trading Academy', 'Courses', 400),
        ('Python for Automation', 'Courses', 250)
    ]

    # إضافة الأدوات
    cursor.executemany('INSERT OR IGNORE INTO products (name, category, price) VALUES (?, ?, ?)', tools)
    
    # إضافة الكورسات
    cursor.executemany('INSERT OR IGNORE INTO products (name, category, price) VALUES (?, ?, ?)', courses)

    conn.commit()
    conn.close()
    print("✅ تم ملء المتجر بالمنتجات والأسعار!")

if __name__ == "__main__":
    add_items()
