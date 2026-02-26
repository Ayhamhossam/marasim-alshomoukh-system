import sqlite3

DB = "store.db"  # اسم قاعدة البيانات

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # جدول المنتجات
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            purchase_price REAL,
            qty INTEGER
        )
    """)

    # جدول المبيعات
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            qty INTEGER,
            sale_price REAL,
            date TEXT
        )
    """)

    # جدول المرتجعات
    c.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            qty INTEGER,
            type TEXT,
            date TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database store.db جاهزة ومخزنة بشكل دائم ✅")

if __name__ == "__main__":
    init_db()