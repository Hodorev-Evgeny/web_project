import flask
from data import db_session

app = flask.Flask(__name__)
app.secret_key = 'secret'


@app.route('/')
def index():
    return flask.render_template('chat.html')


if __name__ == '__main__':
    db_session.global_init('db/data.db')
    app.run('', port=5000, debug=True)

