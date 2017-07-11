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

'''
def init_input():
    print('What do you want to do:' + '\n' +
          '1: Show all tasks' + '\n' +
          '2: Search and/or complete a task' + '\n' +
          '3: Add a new task' + '\n' +
          '4: Delete a task' + '\n' +
          '5: Exit the Todo-List' + '\n' +
          '6: Create sample Todo-List' + '\n')

    choice = input('Please choose a number (1-6) ')
    print("You've selected: " + choice)

    if choice == '1':
        read_from_db()

    elif choice == '2':
        search_choice = input('What task do you want to look at? ')
        search(search_choice)
        change_done_choice = input('Is this task finished? Answer with yes or no ')

        if change_done_choice == 'yes':
            get_serial_by_name(search_choice)
            change_done(get_serial_by_name(search_choice))
            print('The task ' + search_choice + ' is now set to finished.')
            delete_choice = input('Do you want to delete the task? Answer with yes or no ')

            if delete_choice == 'yes':
                print('The task' + search_choice + ' is now deleted.')
                delete(get_serial_by_name(search_choice))

            else:
                print('Okay then!')

        else:
            print('Okay good luck with your task!')

    elif choice == '3':
        task = input("Please enter the task's name: ")
        description = input("Please enter its description: ")
        due = input("Please enter the date its due: DD.MM.YYYY ")
        add_todo(task, description, due)
        print('A new task has been entered.' + '\n' + 'Here is your entry.')
        search(task)

    elif choice == '4':
        read_from_db()
        del_choice = input('What task do you want to delete? Serial required ')
        delete(del_choice)
        print('The ' + del_choice + '. entry has been successfully deleted.')

    elif choice == '5':
        print('Bye')
        return

    elif choice == '6':
        fill_example_data()
    print(50 * '#' + '\n')
    init_input()
'''


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
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M'))

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

'''
def get_serial_by_id(serial):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM todo WHERE serial = ?', (serial,))
    for row in c.fetchall():
        return row[0]
'''


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
