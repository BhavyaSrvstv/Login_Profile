from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  
db = SQLAlchemy(app)
redis_client = redis.Redis(host='127.0.0.1', port=6379)

class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = password

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return 'Username already exists!'

       
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if redis_client.exists(username):
            stored_password = redis_client.get(username).decode()

            if stored_password == password:
                return render_template('profile.html')

       
        user = User.query.filter_by(username=username, password=password).first()
        if user and user.password==password:
            redis_client.set(username, password)
            return render_template('profile.html')

        return 'Invalid username or password!'

    return render_template('login.html')

@app.route('/profile')
def profile():
 return render_template("profile.html")


@app.route('/logout')
def logout():
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)