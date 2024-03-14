from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'toto'
bcrypt = Bcrypt(app)

# BASE DE DONNEES

DATABASE = 'site.db'

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

with app.app_context():
    if not os.path.exists(DATABASE):
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        print("La base de données a été créée avec succès.")
    else:
        print("La base de données existe déjà.")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# ROUTES

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            if (user['password'], password):
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('index'))  
            else:
                return 'Mot de passe incorrect. Veuillez réessayer.'
        else:
            return 'Nom d\'utilisateur non trouvé. Veuillez vous inscrire.'
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Nom d\'utilisateur déjà utilisé. Veuillez en choisir un autre.', 'error')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            db.commit()
            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))

    return render_template('inscription.html')

