import json
import os
from flask import Flask, redirect, url_for, session, render_template
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import pytz

with open("config.json") as f:
    config = json.load(f)

app = Flask(__name__)
app.secret_key = os.urandom(24)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=config["GOOGLE_CLIENT_ID"],
    client_secret=config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
    authorize_params={'prompt': 'select_account'}
)

@app.route('/')
def index():
    user = session.get('user')
    ist = pytz.timezone('Asia/Kolkata')
    indian_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    
    if user:
        return render_template('dashboard.html', title="Dashboard", user=user, time=indian_time)
    return render_template('login.html', title="Login")

@app.route('/login')
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    if user_info:
        session['user'] = user_info
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    end_session_endpoint = google.server_metadata.get('end_session_endpoint')
    if end_session_endpoint:
        post_logout_redirect_uri = url_for('index', _external=True)
        return redirect(f"{end_session_endpoint}?post_logout_redirect_uri={post_logout_redirect_uri}")
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, port=1831)