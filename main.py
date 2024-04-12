import flask
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.user import User
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from uuid import uuid4

app = flask.Flask(__name__)
app.secret_key = 'secret'
login_mgr = LoginManager()
login_mgr.init_app(app)


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
    return flask.render_template('chat.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html', form=LoginForm())
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.username.data).first()
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
        if session.query(User).filter(User.email == form.username.data).first():
            form.form_errors.append('Пользователь с таким логином уже существует')
            return flask.render_template('register.html', form=form)
        user = User()
        user.name = form.name.data
        user.email = form.username.data
        user.set_password(form.password.data)
        user.token = str(uuid4())
        session.add(user)
        session.commit()
        return flask.redirect('/login')
    return flask.render_template('register.html', form=form)


if __name__ == '__main__':
    db_session.global_init('db/data.db')
    app.run('', port=8300, debug=True)

