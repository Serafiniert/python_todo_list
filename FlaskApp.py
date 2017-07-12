import sqlite3
import time
import datetime
from flask import Flask, render_template, flash, g, request, redirect

app = Flask(__name__)

DATABASE = 'todo.db'


@app.route('/')
def index():
    create_table()
    entries = read_from_db()

    return render_template('home.html', entries=entries)


@app.route('/search_by_id', methods=['POST'])
def search():
    serial = request.form['search']
    entries = search(serial)
    print(entries)
    return render_template('home.html', entries=entries)


@app.route('/add', methods=['POST'])
def add():
    task = request.form['task']
    description = request.form['description']
    due = request.form['due']

    add_todo(task, description, due)

    return redirect('/')


@app.route('/complete')
def complete():
    serial = request.args['serial_to_complete']
    state = request.args['done_to_complete']
    change_done(serial, state)
    return redirect('/')


@app.route('/create_example_db', methods=['POST'])
def create_example_db():
    fill_example_data()

    return redirect('/')


@app.route('/delete')
def delete():
    serial = request.args['serial_to_delete']
    print(serial)
    delete(serial)

    return redirect('/')


def get_highest_serial():
    conn = get_db()
    c = conn.cursor()
    ser = 0
    c.execute('SELECT * FROM todo')
    for row in c.fetchall():
        ser = row[0]
    return ser


def get_db():
    if not hasattr(g, 'sqlite_db'):
        conn = sqlite3.connect('todo.db')
        g.sqlite_db = conn
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def create_table():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS todo(serial INTEGER, task TEXT, description TEXT, due TEXT, done TEXT, date TEXT)')


def add_todo(task, description, due):
    conn = get_db()
    c = conn.cursor()
    serial = get_highest_serial() + 1

    unix = time.time()
    done = 'new'
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M Uhr'))

    c.execute("INSERT INTO todo(serial, task, description, due, done, date) VALUES (?, ?, ?, ?, ?, ?)",
              (serial, task, description, due, done, date))
    conn.commit()


def read_from_db():
    if get_highest_serial() == 0:
        flash('Todo-List is empty.' + '\n')
    else:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM todo')
        entries = []
        for row in c.fetchall():
            e = {
                'serial': row[0],
                'task': row[1],
                'description': row[2],
                'due': row[3],
                'done': row[4],
                'date': row[5]
            }
            entries.append(e)
        return entries


def change_done(serial, state):
    conn = get_db()
    c = conn.cursor()
    if state == 'new':
        c.execute("UPDATE todo SET done = 'finished' WHERE serial = ?", (serial,))
    else:
        c.execute("UPDATE todo SET done = 'new' WHERE serial = ?", (serial,))
    conn.commit()


def delete(serial):
    conn = get_db()
    c = conn.cursor()

    c.execute('DELETE FROM todo WHERE serial = ?', (serial,))
    conn.commit()


def search(serial):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM todo WHERE serial = ?', (serial,))
    entries = []
    for row in c.fetchall():
        e = {
            'serial': row[0],
            'task': row[1],
            'description': row[2],
            'due': row[3],
            'done': row[4],
            'date': row[5]
        }
        entries.append(e)
    return entries


def fill_example_data():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM todo')
    for row in c.fetchall():
        delete(row[0])
    add_todo("Einkaufen", "kein Essen da!", "2017-07-06")
    add_todo("Sport", "zu fett", "2018-07-20")
    add_todo("Praktikum finden", "muss Arbeiten", "2017-10-01")
    add_todo("Japanisch", "Konnichiwa", "2017-08-04")
    add_todo("Python", "Python ist toll!", "2017-07-17")
    print('Example Todo-List created.')
    read_from_db()


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
