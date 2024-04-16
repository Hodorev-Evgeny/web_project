import flask
import sqlite3

from flask import request
from data import db_session

app = flask.Flask(__name__)
app.secret_key = 'secret'

con = con = sqlite3.connect('db/data.db')
cur = con.cursor()
que = """SELECT users.name
             FROM users"""
data = list(cur.execute(que))
message = []
name_users = 'Me'
user_id = '1'


@app.route('/')
def index():
    return flask.render_template('chat.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    message.append(request.values.get('text'))
    return flask.render_template('chat2.html', data=data, message=message, name_users=name_users)


@app.route('/settings')
def settings():
    return flask.render_template('settings.html')

@app.route('/settings_account', methods=['GET', 'POST'])
def settings_account():
    user_name = request.values.get('username')
    email = request.values.get('email')
    user_id = 1
    con = sqlite3.connect('db/data.db')
    cur = con.cursor()

    if user_name is not None and email is not None:
        qur = """UPDATE users
                SET name = ?,
                email = ?
                WHERE id = ?"""
        cur.execute(qur, (user_name, email, user_id))
        return flask.render_template('chat2.html')

    return flask.render_template('set.html')


if __name__ == '__main__':
    db_session.global_init('db/data.db')
    app.run(port=800, host='127.0.0.1')

