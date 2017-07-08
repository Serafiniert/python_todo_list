import sqlite3
import time
import datetime
from flask import Flask, render_template, flash, g

app = Flask(__name__)

DATABASE = 'todo.db'


@app.route('/')
def index():
    entries = read_from_db()
    return render_template('home.html', entries=entries)

conn = sqlite3.connect('todo.db')
c = conn.cursor()


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


def get_highest_serial():
    ser = 0
    c.execute('SELECT * FROM todo')
    for row in c.fetchall():
        ser = row[0]
    return ser


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def create_table():
    c.execute(
        'CREATE TABLE IF NOT EXISTS todo(serial INTEGER, task TEXT, description TEXT, due TEXT, done TEXT, date TEXT)')


def add_todo(task, description, due):
    serial = get_highest_serial() + 1

    unix = time.time()
    done = 'new'
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%d.%m.%Y %H:%M'))

    c.execute("INSERT INTO todo(serial, task, description, due, done, date) VALUES (?, ?, ?, ?, ?, ?)",
              (serial, task, description, due, done, date))
    conn.commit()


def read_from_db():
    if get_highest_serial() == 0:
        flash('Todo-List is empty.' + '\n')
    else:

        c.execute('SELECT * FROM todo')
        entries = c.fetchall()
        return entries


def change_done(serial):
    c.execute("UPDATE todo SET done = 'finished' WHERE serial = ? AND done = 'new'", (serial,))
    conn.commit()


def delete(serial):
    c.execute('DELETE FROM todo WHERE serial = ?', (serial,))
    conn.commit()


def get_serial_by_name(name):
    c.execute('SELECT * FROM todo WHERE task = ?', (name,))
    for row in c.fetchall():
        return row[0]


def search(name):
    if get_highest_serial() == 0:
        print('Todo-List is empty.' + '\n')
    else:
        c.execute('SELECT * FROM todo WHERE task = ?', (name,))
        [print(row) for row in c.fetchall()]
        print('\n')


def fill_example_data():
    c.execute('SELECT * FROM todo')
    for row in c.fetchall():
        delete(row[0])
    add_todo("Einkaufen", "kein Essen da!", "06.07.2017")
    add_todo("Sport", "zu fett", "20.07.2018")
    add_todo("Praktikum finden", "muss Arbeiten", "01.10.2017")
    add_todo("Japanisch", "Konnichiwa", "04.08.2017")
    add_todo("Python", "Python ist toll!", "17.07.2017")
    print('Example Todo-List created.')
    read_from_db()


create_table()
#init_input()

if __name__ == '__main__':
    app.run(debug=True)

c.close()
conn.close()
