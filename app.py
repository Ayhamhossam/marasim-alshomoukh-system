from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder="templates")
app.secret_key = "marasim_secret_key"

USERNAME = "ali"
PASSWORD = "776940187"

DB = "store.db"

# =========================
# إنشاء قاعدة البيانات
# =========================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            purchase_price REAL,
            quantity INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity_sold INTEGER,
            sale_price REAL,
            date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER,
            reason TEXT,
            date TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# تسجيل الدخول
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["user"] = USERNAME
            return redirect("/dashboard")
        else:
            return "بيانات الدخول خاطئة"
    return render_template("login.html")


# =========================
# لوحة التحكم
# =========================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    total_products = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_stock = c.execute("SELECT IFNULL(SUM(quantity),0) FROM products").fetchone()[0]
    total_sales = c.execute("SELECT IFNULL(SUM(quantity_sold * sale_price),0) FROM sales").fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_stock=total_stock,
        total_sales=total_sales
    )


# =========================
# تسجيل خروج
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# المشتريات
# =========================
@app.route("/purchases", methods=["GET", "POST"])
def purchases():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        type_ = request.form["type"]
        price = float(request.form["price"])
        qty = int(request.form["qty"])

        existing = c.execute(
            "SELECT id, quantity FROM products WHERE name=?",
            (name,)
        ).fetchone()

        if existing:
            new_qty = existing[1] + qty
            c.execute(
                "UPDATE products SET quantity=?, purchase_price=? WHERE id=?",
                (new_qty, price, existing[0])
            )
        else:
            c.execute(
                "INSERT INTO products (name, type, purchase_price, quantity) VALUES (?, ?, ?, ?)",
                (name, type_, price, qty)
            )

        conn.commit()
        conn.close()
        return redirect("/purchases")

    products = c.execute("SELECT * FROM products").fetchall()
    conn.close()

    return render_template("purchases.html", products=products)


# =========================
# المبيعات
# =========================
@app.route("/sales", methods=["GET", "POST"])
def sales():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    products = c.execute("SELECT * FROM products").fetchall()

    if request.method == "POST":
        product_id = int(request.form["product"])
        qty = int(request.form["qty"])
        price = float(request.form["sale_price"])

        current_qty = c.execute(
            "SELECT quantity FROM products WHERE id=?",
            (product_id,)
        ).fetchone()[0]

        if qty > current_qty:
            conn.close()
            return "الكمية غير متوفرة"

        c.execute(
            "UPDATE products SET quantity = quantity - ? WHERE id=?",
            (qty, product_id)
        )

        c.execute(
            "INSERT INTO sales (product_id, quantity_sold, sale_price, date) VALUES (?, ?, ?, ?)",
            (product_id, qty, price, datetime.now())
        )

        conn.commit()
        conn.close()
        return redirect("/sales")

    conn.close()
    return render_template("sales.html", products=products)


# =========================
# المرتجعات
# =========================
@app.route("/returns", methods=["GET", "POST"])
def returns_page():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    products = c.execute("SELECT * FROM products").fetchall()

    if request.method == "POST":
        product_id = int(request.form["product"])
        qty = int(request.form["qty"])
        reason = request.form["reason"]

        if reason == "مرتجع زبون":
            c.execute(
                "UPDATE products SET quantity = quantity + ? WHERE id=?",
                (qty, product_id)
            )
        elif reason == "مرتجع تاجر":
            c.execute(
                "UPDATE products SET quantity = quantity - ? WHERE id=?",
                (qty, product_id)
            )

        c.execute(
            "INSERT INTO returns (product_id, quantity, reason, date) VALUES (?, ?, ?, ?)",
            (product_id, qty, reason, datetime.now())
        )

        conn.commit()
        conn.close()
        return redirect("/returns")

    conn.close()
    return render_template("returns.html", products=products)


# =========================
# المخزون
# =========================
@app.route("/inventory")
def inventory():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    products = c.execute("SELECT * FROM products").fetchall()
    conn.close()

    return render_template("inventory.html", products=products)


if __name__ == "__main__":
    app.run()