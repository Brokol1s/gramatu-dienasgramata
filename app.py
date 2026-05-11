from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'papa_12'

fails = "projekts_gramatudienasgramata.db"

def get_db():
    conn = sqlite3.connect(fails)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def izveidot_db():
    conn = sqlite3.connect(fails)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS Lietotaji (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lietotajvards TEXT UNIQUE NOT NULL,
        parole TEXT NOT NULL,
        vards TEXT
    );
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS Gramatas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nosaukums TEXT NOT NULL,
        lapas INTEGER,
        vertejums TEXT,
        lietotaja_id INTEGER NOT NULL,
        FOREIGN KEY (lietotaja_id) REFERENCES Lietotaji (id)
    );
    """)

    conn.commit()
    conn.close()
    print("Datubāze ir veiksmīgi pārbaudīta/izveidota!")


izveidot_db()




books = [
]


@app.route('/')
def sakums():
    return render_template('index.html')

@app.route('/pieteikties', methods=['GET', 'POST'])
def pieteikties():
    if request.method == 'POST':
        vards = request.form.get('lietotajs').strip()
        parole = request.form.get('parole').strip()
        
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM Lietotaji WHERE lietotajvards = ?", (vards,))
        user_data = cur.fetchone()
        conn.close()

        if user_data and check_password_hash(user_data['parole'], parole):
            session['user'] = vards
            if vards == 'admin':
                return redirect(url_for('admin_panelis'))
            return redirect(url_for('saraksts'))
        
        return "Nepareizs lietotājvārds vai parole!"
    return render_template('pieteikties.html')

@app.route('/registreties', methods=['GET', 'POST'])
def registreties():
    if request.method == 'POST':
        lietotajvards = request.form.get('lietotajs') 
        vards = request.form.get('vards')            
        parole = request.form.get('parole')          

        if not lietotajvards or not parole:
            return "Kļūda: Aizpildi visus laukus!"

        hash_parole = generate_password_hash(parole)

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Lietotaji (lietotajvards, parole, vards) 
                VALUES (?, ?, ?)
            """, (lietotajvards, hash_parole, vards))
            conn.commit()
            return redirect(url_for('pieteikties'))
        except sqlite3.IntegrityError:
            return "Šis lietotājvārds jau ir aizņemts!"
        finally:
            conn.close()

    return render_template('registreties.html')

@app.route('/saraksts')
def saraksts():
    if 'user' not in session: return redirect(url_for('pieteikties'))
    
    lietotajvards = session['user']
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT Gramatas.* FROM Gramatas 
        JOIN Lietotaji ON Gramatas.lietotaja_id = Lietotaji.id 
        WHERE Lietotaji.lietotajvards = ?
    """, (lietotajvards,))
    
    user_books = cur.fetchall()
    conn.close()
    
    return render_template('saraksts.html', books=user_books)

@app.route('/pievienot', methods=['GET', 'POST'])
def pievienot():
    if 'user' not in session: 
        return redirect(url_for('pieteikties'))
    
    if request.method == 'POST':
        nosaukums = request.form.get('nosaukums')
        lapas = request.form.get('lapas')
        vertejums = request.form.get('vertejums')
        lietotajvards = session['user']

        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM Lietotaji WHERE lietotajvards = ?", (lietotajvards,))
        user_row = cur.fetchone()
        
        if user_row:
            user_id = user_row['id']
            cur.execute("INSERT INTO Gramatas (nosaukums, lapas, vertejums, lietotaja_id) VALUES (?, ?, ?, ?)",
                        (nosaukums, lapas, vertejums, user_id))
            conn.commit()
        
        conn.close()
        return redirect(url_for('saraksts'))
        
    return render_template('pievienot.html')


@app.route('/admin')
def admin_panelis():
    if session.get('user') != 'admin': return "Piekļuve liegta!"
    conn = get_db()
    all_books = conn.execute("SELECT * FROM Gramatas").fetchall()
    conn.close()
    return render_template('admin.html', books=all_books)

@app.route('/dzest/<int:book_id>')
def dzest_gramatu(book_id):
    if session.get('user') != 'admin':
        return "Piekļuve liegta!"

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Gramatas WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    
    print(f"Grāmata ar ID {book_id} ir izdzēsta no datubāzes!")
    return redirect(url_for('admin_panelis'))

@app.route('/iziet')
def iziet():
    session.clear()
    return redirect(url_for('sakums'))

if __name__ == '__main__':
    app.run(debug=True)