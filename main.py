import flask
from flask_socketio import SocketIO

from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.message import Message
from data.user import User
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from uuid import uuid4

app = flask.Flask(__name__)
app.secret_key = 'secret'
login_mgr = LoginManager()
login_mgr.init_app(app)
sock = SocketIO(app)

sessions = {}


@login_mgr.user_loader
def load_user(token):
    session = db_session.create_session()
    return session.query(User).filter(User.token == token).first()


@login_mgr.unauthorized_handler
def unauthorized():
    return flask.redirect('/login')


@app.route('/')
@login_required
def index():
    return flask.redirect('/chat')


@app.route('/chat/<int:to_id>')
@app.route('/chat')
@login_required
def chat_page(to_id=None):
    session = db_session.create_session()
    users = set()
    chats = session.query(Message).filter(Message.from_id == current_user.id or Message.to_id == current_user.id).all()
    for chat in chats:
        if chat in users:
            continue
        if chat.from_id == current_user.id:
            users.add(session.query(User).filter(User.id == chat.to_id).first())
        else:
            users.add(session.query(User).filter(User.id == chat.from_id).first())
    return flask.render_template('chat.html', chats=users, token=current_user.token, to_id=to_id,
                                 user=current_user.safe_serialize(), is_chat=to_id is not None)


@sock.on('auth')
def on_connect(auth: dict):
    token = auth.get('token')
    if not token:
        return
    session = db_session.create_session()
    user = session.query(User).filter(User.token == token).first()
    if not user:
        return
    global sessions
    sessions[user.id] = flask.request.sid
    if auth.get('target'):
        messages = session.query(Message).all()
        messages = list(filter(lambda x: x.from_id == user.id and x.to_id == auth['target'] \
                                         or x.from_id == auth['target'] and x.to_id == user.id, messages))
        sock.emit('msg_init', {'messages': [message.to_dict() for message in messages]},
                  room=flask.request.sid)


@sock.on('disconnect')
def on_disconnect():
    if current_user.id in sessions:
        del sessions[current_user.id]


@sock.on('msg_send')
def on_msg_send(data: dict):
    if not {'token', 'text', 'to'}.issubset(set(data.keys())) \
            or not data['text'] or not data['to'] \
            or type(data['to']) != int:
        return
    session = db_session.create_session()
    user = session.query(User).filter(User.token == data['token']).first()
    if not user:
        return
    message = Message()
    message.text = data['text']
    message.from_id = user.id
    message.to_id = data['to']
    session.add(message)
    session.commit()
    if data['to'] not in sessions or data['to'] == user.id:
        return
    sock.emit('msg_recv', message.to_dict(), room=sessions.get(data['to']))


@sock.on('get_user')
def on_get_user(data: dict):
    if not {'id'}.issubset(set(data.keys())):
        return
    session = db_session.create_session()
    user = session.query(User).filter(User.id == data['id']).first()
    if not user:
        return
    sock.emit('user', user.safe_serialize(), room=flask.request.sid)


@app.route('/search/')
def search():
    session = db_session.create_session()
    users = session.query(User).filter(User.name.like(f'%{flask.request.args.get("name")}%')).all()
    return flask.render_template('search.html', users=[user.safe_serialize() for user in users],
                                 query=flask.request.args.get("name"), count=len(users))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html', form=LoginForm())
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return flask.redirect('/')
        form.form_errors.append('Неверный логин или пароль')
        return flask.render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return flask.redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        return flask.render_template('register.html', form=RegisterForm())
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            form.form_errors.append('Пароли не совпадают')
            return flask.render_template('register.html', form=form)
        session = db_session.create_session()
        if session.query(User).filter(User.username == form.username.data).first():
            form.form_errors.append('Пользователь с таким логином уже существует')
            return flask.render_template('register.html', form=form)
        user = User()
        user.name = form.name.data
        user.username = form.username.data
        user.set_password(form.password.data)
        user.token = str(uuid4())
        session.add(user)
        session.commit()
        return flask.redirect('/login')
    return flask.render_template('register.html', form=form)


if __name__ == '__main__':
    db_session.global_init('db/data.db')
    sock.run(app, '0.0.0.0', port=8300, debug=True, allow_unsafe_werkzeug=True)
