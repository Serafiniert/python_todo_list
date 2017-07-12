import sqlite3
import time
import datetime
from flask import Flask, render_template, g, request, redirect

app = Flask(__name__)

DATABASE = 'todo.db'


# Root-Route for showing every entry in the Todo-List
@app.route('/')
def index():
    create_table()
    entries = read_from_db()

    return render_template('home.html', entries=entries)


# Route for addind a new Todo-Item
@app.route('/add', methods=['POST'])
def add():
    task = request.form['task']
    description = request.form['description']
    due = request.form['due']

    add_todo(task, description, due)

    return redirect('/')


# Route for searching by an ID
@app.route('/search_by_id', methods=['POST'])
def search():
    serial = request.form['search']
    entries = search(serial)
    print(entries)
    return render_template('home.html', entries=entries)


# Route for creating an example Database
@app.route('/create_example_db', methods=['POST'])
def create_example_db():
    fill_example_data()

    return redirect('/')


# Route for changing the state of a Todo-Item
@app.route('/complete')
def complete():
    serial = request.args['serial_to_complete']
    state = request.args['state_to_complete']
    change_state(serial, state)
    return redirect('/')


# Route for deleting a Todo-Item
@app.route('/delete')
def delete():
    # requesting the hidden input to get the serial by pressing the "Remove"-Button in the same row
    serial = request.args['serial_to_delete']
    print(serial)
    delete(serial)

    return redirect('/')


# function that returns the connection to the database
def get_db():
    if not hasattr(g, 'sqlite_db'):
        conn = sqlite3.connect('todo.db')
        g.sqlite_db = conn
    return g.sqlite_db


# function that creates the table "todo", if it doesn't exist, with following values:
# serial INTEGER - unique ID for every Item
# task TEXT - name of the task
# description TEXT - description of the task
# due TEXT - due date of the task
# state TEXT - state of the task, new or finished
# date TEXT - the date, the item was added
def create_table():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS todo(serial INTEGER, task TEXT, description TEXT, due TEXT, state TEXT, date TEXT)')


# function that returns all database entries as a dictionary
def read_from_db():
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
            'state': row[4],
            'date': row[5]
        }
        entries.append(e)
    return entries


# function that returns the highest serial currently in the database
def get_highest_serial():
    conn = get_db()
    c = conn.cursor()
    ser = 0
    c.execute('SELECT * FROM todo')
    for row in c.fetchall():
        ser = row[0]
    return ser


# function that adds a Todo-Item to the list
def add_todo(task, description, due):
    conn = get_db()
    c = conn.cursor()

    # take the highest serial and add 1 to get unique ID
    serial = get_highest_serial() + 1

    # state is always new for a new Todo-Item
    state = 'new'

    # date saved in format YYYY-MM-DD Hour:Min
    unix = time.time()
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M Uhr'))

    # inserts calculated values and input values into the table
    c.execute("INSERT INTO todo(serial, task, description, due, state, date) VALUES (?, ?, ?, ?, ?, ?)",
              (serial, task, description, due, state, date))
    conn.commit()


# function that returns the database entry of a searched item as a dictionary
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
            'state': row[4],
            'date': row[5]
        }
        entries.append(e)
    return entries


# function that clears the list and fills it with example dara
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


# function that changes the state of a item by checking the current state and serial
def change_state(serial, state):
    conn = get_db()
    c = conn.cursor()
    if state == 'new':
        c.execute("UPDATE todo SET state = 'finished' WHERE serial = ?", (serial,))
    else:
        c.execute("UPDATE todo SET state = 'new' WHERE serial = ?", (serial,))
    conn.commit()


# function that deletes a Todo-Item
def delete(serial):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM todo WHERE serial = ?', (serial,))
    conn.commit()


# function that disconnects from the database after the template is rendered
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    # setting the secret key, lets the program work with an empty database
    app.secret_key = 'super secret key'
    app.run(debug=True)
