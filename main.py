import flask
from data import db_session

app = flask.Flask(__name__)
app.secret_key = 'secret'


@app.route('/')
def index():
    return flask.render_template('chat.html')


@app.route('/home')
def home():
    return flask.render_template('chat2.html')


@app.route('/settings')
def settings():
    return flask.render_template('settings.html')



if __name__ == '__main__':
    db_session.global_init('db/data.db')
    app.run(port=20000, host='127.0.0.1')

