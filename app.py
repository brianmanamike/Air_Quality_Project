from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import threading
import webbrowser
import time

# Add these lines at the top of app.py
import os
app.secret_key = os.environ.get('SECRET_KEY', 'dev')  # For session security

# Update database configuration (replace SQLite with Heroku's PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db').replace("postgres://", "postgresql://", 1)
# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Create the database tables
def create_database():
    with app.app_context():
        db.create_all()

# Function to open the dashboard in a browser
def run_dashboard():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8050")

# Route for home
@app.route('/')
def home():
    if 'email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['email'] = email
            # Start dashboard in a subprocess
            subprocess.Popen(['python', 'multi_vizro.py'])
            # Open dashboard in browser
            threading.Thread(target=run_dashboard).start()
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

# Route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already exists')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

# Route for dashboard
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

# Run the Flask app
if __name__ == '__main__':
    create_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
