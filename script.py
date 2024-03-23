# Imporations des modules 

from flask import Flask, render_template, request, redirect, url_for, session, g, flash  # Import des modules Flask
import sqlite3  
import os 
from flask_bcrypt import Bcrypt  

# Création de l'application Flask avec clé secrète et système de hachage

app = Flask(__name__)  
app.secret_key = 'toto'  
bcrypt = Bcrypt(app)  

# Chemin vers la base de données SQLite

DATABASE = 'site.db'  

# Fonction pour obtenir la connexion à la base de données

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Vérification et création de la base de données si elle n'existe pas

with app.app_context():  

    # Vérification si la base de données existe déjà sur le système de fichiers
    if not os.path.exists(DATABASE):  
        # Appel la fonction de connexion vers la base de donnée
        db = get_db() 
        # Ouverture du fichier SQL
        with app.open_resource('schema.sql', mode='r') as f: 
            # Execution du script SQL
            db.executescript(f.read())
        db.commit()  
        print("La base de données a été créée avec succès.")  

    # Si la base de données existe déjà sur le système de fichiers, envoi un message d'info
    else:  
        print("La base de données existe déjà.") 


# Fonction pour fermer la connexion à la base de données
        
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Route avec fonctionnalités :

# Redirection automatique vers la page de connexion 
        
@app.route('/')
def redirect_to_login():
    return redirect(url_for('login'))

# Route pour la page de connexion, prenant en charge les méthodes GET et POST

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  

        # Récupération des données user
        username = request.form['username']  
        password = request.form['password']  

        # Connexion à la base de données
        db = get_db()  
        cursor = db.cursor()  
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))  
        user = cursor.fetchone()  

        if user and bcrypt.check_password_hash(user['password'], password):  
            session['logged_in'] = True  
            session['username'] = username  
            return redirect(url_for('index'))  
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')  
    return render_template('login.html') 

# Routage vers la page d'inscription

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
            # Sécurisation du mdp avec un hachage des données
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))  
            # Validation des données
            db.commit() 
            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')  
            return redirect(url_for('login')) 
        
    # Affichage du formulaire d'inscription
    return render_template('inscription.html') 

# Route vers la page d'index 

@app.route('/index')
def index():
    # Vérification de la session utilisateur
    if 'username' in session:  
        username = session['username']  
        db = get_db() 
        cursor = db.cursor() 
        cursor.execute('SELECT id, note FROM notes WHERE user_id = (SELECT id FROM users WHERE username = ?)', (username,))  
        # Récupération de toutes les notes de l'utilisateur
        notes = cursor.fetchall()  
        return render_template('index.html', notes=notes)  
    else:
        return redirect(url_for('login'))  #

# Route pour ajouter une nouvelle note
    
@app.route('/add_note', methods=['POST'])
def add_note():
    if 'username' in session:  

        # Récupération de la nouvelle note
        note = request.form['note'] 
        username = session['username'] 
        db = get_db()  
        cursor = db.cursor() 
        cursor.execute('INSERT INTO notes (user_id, note) VALUES ((SELECT id FROM users WHERE username = ?), ?)', (username, note)) 
        db.commit()  
    return redirect(url_for('index')) 

# Route pour supprimer une note existante

@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'username' in session:  
        db = get_db()  
        cursor = db.cursor()  

        # Suppression de la note de la base de données
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))  
        db.commit() 
    return redirect(url_for('index'))  

# Route pour se déconnecter

@app.route('/logout')
def logout():

    # Suppression de l'utilisateur de la session
    session.pop('username', None) 

    # Déconnexion de l'utilisateur
    session.pop('logged_in', None)  

    flash('Vous avez été déconnecté.', 'info') 
    return redirect(url_for('login'))  

# Route pour la modification du mot de passe

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' in session:  
        if request.method == 'POST':  
            # Récupération de l'ancien mot de passe
            old_password = request.form['old_password']  
            # Récupération du nouveau mot de passe et de sa confirmation
            new_password = request.form['new_password']  
            confirm_password = request.form['confirm_password'] 

            db = get_db()  
            cursor = db.cursor() 
            cursor.execute('SELECT * FROM users WHERE username = ?', (session['username'],)) 
            user = cursor.fetchone() 

             # Si l'utilisateur existe et l'ancien mot de passe est correct
            if user and bcrypt.check_password_hash(user['password'], old_password): 
                if new_password == confirm_password:  
                    # Hachage sécurisé du nouveau mot de passe
                    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')  
                    cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, session['username']))  
                    db.commit()  
                    flash('Mot de passe modifié avec succès!', 'success')  
                    return redirect(url_for('index'))  
                else:
                    flash('Les nouveaux mots de passe ne correspondent pas.', 'error')  
            else:
                flash('Ancien mot de passe incorrect.', 'error') 

        return render_template('change_password.html')  
    else:
        # Redirection vers la page de connexion si l'utilisateur n'est pas connecté
        return redirect(url_for('login'))  
