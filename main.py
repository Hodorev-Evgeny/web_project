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



if __name__ == '__main__':
    db_session.global_init('db/data.db')
    app.run(port=20000, host='127.0.0.1')

