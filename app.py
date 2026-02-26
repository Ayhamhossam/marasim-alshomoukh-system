from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "marasim_secret_key"

USERNAME = "ali"
PASSWORD = "776940187"

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "بيانات الدخول غير صحيحة"
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template("dashboard.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run()
