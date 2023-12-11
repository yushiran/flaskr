# flaskr.py
# all the imports
from __future__ import with_statement
from contextlib import closing  # contextlib.closing()会帮它加上__enter__()和__exit__()，使其满足with的条件。
import sqlite3
import time
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
 
# configuration
DATABASE = './flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = '1'
PASSWORD = '1'
 
app = Flask(__name__)
app.config.from_object(__name__)
 
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
 
 
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])
 
 
def init_db():
    with closing(connect_db()) as db:
        with open('schema.sql', mode='r', encoding='utf-8') as f:  # 确保以文本模式和正确的编码打开
            db.cursor().executescript(f.read())
        db.commit()
 
 
@app.before_request
def before_request():
    g.db = connect_db()
 
 
@app.after_request
def after_request(response):
    g.db.close()
    return response
 
 
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)
 
 
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
 
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)
 
 
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
 
 
if __name__ == '__main__':
    app.run()