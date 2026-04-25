
import sqlite3

def populate_inventory():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    # 1. قائمة إيميلات حسابات إنستغرام (التي أرسلتها أنت)
    # سنربطها بمنتج "Instagram Account" (افترضنا أن الـ ID الخاص به هو 5)
    instagram_accounts = [
        "solomarthe2013@gmail.com",
        "narangtabio@gmail.com",
        "florache1515@gmail.com",
        "seliiintoprak@gmail.com",
        "iamfauu@gmail.com",
        "seziethedayshoutouts@gmail.com",
        "yeezyboostreseller@gmail.com",
        "mjinipatamu@gmail.com"
    ]

    # جلب ID منتج إنستغرام من قاعدة البيانات للتأكد
    cursor.execute("SELECT id FROM products WHERE name LIKE '%Instagram%'")
    product_row = cursor.fetchone()
    
    if product_row:
        product_id = product_row[0]
        for acc in instagram_accounts:
            cursor.execute('''
                INSERT INTO inventory (product_id, item_details, is_sold) 
                VALUES (?, ?, 0)
            ''', (product_id, acc))
        print(f"✅ تم إضافة {len(instagram_accounts)} حساب إنستغرام للمخزون.")
    else:
        print("❌ لم يتم العثور على منتج باسم Instagram في جدول المنتجات.")

    # 2. إضافة روابط الكورسات (أمثلة بروابط Mega أو Drive)
    # سنربطها بمنتجات الكورسات (الأرقام 6، 7، 8 حسب ترتيب الإضافة)
    courses_links = [
        ("Advanced Zero-Day Exploit", "https://mega.nz/folder/example_link_zero_day"),
        ("Professional Trading Academy", "https://drive.google.com/drive/folders/trading_academy"),
        ("Python for Automation", "https://github.com/your-private-repo/python-course")
    ]

    for name, link in courses_links:
        cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
        p_row = cursor.fetchone()
        if p_row:
            cursor.execute('''
                INSERT INTO inventory (product_id, item_details, is_sold) 
                VALUES (?, ?, 0)
            ''', (p_row[0], link))
            print(f"✅ تم إضافة رابط الكورس: {name}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_inventory()
