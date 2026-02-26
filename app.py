from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "store.db"  # قاعدة البيانات الدائمة

# --- اتصال بقاعدة البيانات ---
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# --- صفحة تسجيل الدخول ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "ali" and password == "776940187":
            return redirect(url_for("dashboard"))
    return render_template("login.html")

# --- Dashboard ---
@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_stock = conn.execute("SELECT SUM(qty) FROM products").fetchone()[0] or 0
    total_sales = conn.execute("SELECT SUM(qty*sale_price) FROM sales").fetchone()[0] or 0
    total_purchase_cost = conn.execute("SELECT SUM(qty*purchase_price) FROM products").fetchone()[0] or 0
    net_profit = total_sales - total_purchase_cost
    total_returns_store = conn.execute("SELECT SUM(qty) FROM returns WHERE type='للمحل'").fetchone()[0] or 0
    total_returns_supplier = conn.execute("SELECT SUM(qty) FROM returns WHERE type='للتاجر'").fetchone()[0] or 0
    conn.close()
    return render_template("dashboard.html", total_products=total_products, total_stock=total_stock,
                           total_sales=total_sales, net_profit=net_profit,
                           total_returns_store=total_returns_store, total_returns_supplier=total_returns_supplier)

# --- المشتريات ---
@app.route("/purchases", methods=["GET", "POST"])
def purchases():
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["name"]
        type_ = request.form["type"]
        price = float(request.form["price"])
        qty = int(request.form["qty"])

        existing = conn.execute("SELECT id, qty FROM products WHERE name=?", (name,)).fetchone()
        if existing:
            # تحديث الكمية إذا المنتج موجود
            new_qty = existing["qty"] + qty
            conn.execute("UPDATE products SET qty=?, purchase_price=? WHERE id=?", (new_qty, price, existing["id"]))
        else:
            conn.execute("INSERT INTO products (name,type,purchase_price,qty) VALUES (?,?,?,?)", (name,type_,price,qty))
        conn.commit()

    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("purchases.html", products=products)

# --- المبيعات ---
@app.route("/sales", methods=["GET", "POST"])
def sales():
    conn = get_db_connection()
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        qty = int(request.form["qty"])
        sale_price = float(request.form["sale_price"])
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # التأكد من وجود كمية كافية
        product = conn.execute("SELECT qty FROM products WHERE id=?", (product_id,)).fetchone()
        if product and product["qty"] >= qty:
            new_qty = product["qty"] - qty
            conn.execute("UPDATE products SET qty=? WHERE id=?", (new_qty, product_id))
            conn.execute("INSERT INTO sales (product_id, qty, sale_price, date) VALUES (?,?,?,?)",
                         (product_id, qty, sale_price, date))
            conn.commit()
    products = conn.execute("SELECT id,name,qty FROM products").fetchall()
    sales_data = conn.execute("""
        SELECT s.qty, s.sale_price, s.date, p.name
        FROM sales s
        JOIN products p ON s.product_id=p.id
        ORDER BY s.date DESC
    """).fetchall()
    conn.close()
    return render_template("sales.html", products=products,
                           sales=[{"qty":s["qty"], "sale_price":s["sale_price"], "date":s["date"], "product_name":s["name"]} for s in sales_data])

# --- المرتجعات ---
@app.route("/returns", methods=["GET","POST"])
def returns():
    conn = get_db_connection()
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        qty = int(request.form["qty"])
        type_ = request.form["type"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # تحديث المخزون حسب نوع المرتجع
        product = conn.execute("SELECT qty FROM products WHERE id=?", (product_id,)).fetchone()
        if product:
            new_qty = product["qty"] + qty if type_=="للمحل" else max(0, product["qty"] - qty)
            conn.execute("UPDATE products SET qty=? WHERE id=?", (new_qty, product_id))
            conn.execute("INSERT INTO returns (product_id, qty, type, date) VALUES (?,?,?,?)",
                         (product_id, qty, type_, date))
            conn.commit()

    products = conn.execute("SELECT id,name,qty FROM products").fetchall()
    conn.close()
    return render_template("returns.html", products=products)

# --- المخزون ---
@app.route("/inventory")
def inventory():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("inventory.html", products=products)

# --- تسجيل الخروج ---
@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)