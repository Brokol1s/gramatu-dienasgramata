from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'papa_12'


books = [{"id": 1, "nosaukums": "Grāmata A", "lapas": 250, "vertējums": 8},{"id": 2, "nosaukums": "Grāmata B", "lapas": 120, "vertējums": 9},]

@app.route('/')
def sakums():
    return render_template('index.html')

@app.route('/pieteikties', methods=['GET', 'POST'])
def pieteikties():
    if request.method == 'POST':
        lietotajvards = request.form.get('username')
        parole = request.form.get('password')
        
        if lietotajvards == 'admin':
            return redirect(url_for('admin_panelis'))
        return redirect(url_for('saraksts'))
    return render_template('pieteikties.html')

@app.route('/registreties', methods=['GET', 'POST'])
def registreties():
    if request.method == 'POST':
        return redirect(url_for('pieteikties'))
    return render_template('registreties.html')

@app.route('/saraksts')
def saraksts():
    return render_template('saraksts.html', books=books)

@app.route('/pievienot', methods=['GET', 'POST'])
def pievienot():
    if request.method == 'POST':
        jauna_gramata = {
            len(books) + 1,
            request.form.get('nosaukums'),
            request.form.get('lapas'),
            request.form.get('vertējums')
        }
        books.append(jauna_gramata)
        return redirect(url_for('saraksts'))
        return render_template('pievienot.html')

@app.route('/admin')
def admin_panelis():
    return render_template('admin.html', books=books)

@app.route('/dzest/<int:book_id>')
def dzest_gramatu(book_id):
    global books
    books = [b for b in books if b['id'] != book_id]
    return redirect(url_for('admin_panelis'))

if __name__ == '__main__':
    app.run(debug=True)
