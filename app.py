import secrets
import paho.mqtt.publish as publish
from flask import Flask, redirect, session, request, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'my_secret_key'
CORS(app, supports_credentials=True)
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id='447d42b357c52b096081',
    client_secret='98d8f8fe2e589e8cfc2a4a0f5e866131c6813867',
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    client_kwargs={'scope': 'user:email'},
)


@app.route('/')
def hello_world():
    if 'user_name' not in session:
        login_button = '<a href="' + url_for('login') + '">Login</a>'
        return f'Hello, stranger. Please {login_button} to continue.'
    else:
        logout_button = '<a href="' + url_for('logout') + '">Logout</a>'
        return f'Hello, {session["user_name"]}. You are logged in. {logout_button}'


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect('/')


@app.route('/authorize')
def authorize():
    token = github.authorize_access_token()
    resp = oauth.github.get('https://api.github.com/user')
    resp.raise_for_status()
    profile = resp.json()
    session['user_name'] = profile['login']
    message = f"User logged in: {session.get('user_name', 'Stranger')}"
    publish.single("user/login", message, hostname="broker.emqx.io")
    return redirect('/')

