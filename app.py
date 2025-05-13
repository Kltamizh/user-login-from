from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')  

# Create database
with app.app_context():
    db.create_all()

# Create default admin if not exists
with app.app_context():
    admin_username = "admin"
    admin_password = "admin123"  # You can change this anytime
    admin_user = User.query.filter_by(username=admin_username).first()
    if not admin_user:
        hashed_pw = generate_password_hash(admin_password)
        admin_user = User(username=admin_username, password=hashed_pw, role='admin')
        db.session.add(admin_user)
        db.session.commit()


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role='user')
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hardcoded admin credentials
        admin_username = "admin"
        admin_password = "admin123"

        if username == admin_username and password == admin_password:
            session['user'] = admin_username
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))

        # Check database for normal users
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            session['role'] = user.role
            return redirect(url_for('content'))

        flash("Invalid username or password.")
        return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        flash("Admin access only.")
        return redirect(url_for('login'))

    admin = User.query.filter_by(username=session['user']).first()
    users = User.query.all()
    return render_template('dashboard.html', user=admin, users=users)


@app.route('/content')
def content():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('content.html', username=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
