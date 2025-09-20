import json
import os
from flask import Flask, redirect, url_for, session, render_template, request, jsonify, Response
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

def generate_letter_diamond(n):
    s = 'FORMULAQSOLUTIONS'
    if n % 2 == 0:
        n += 1
    length = n // 2
    idx = 0
    ans = []

    for i in range(0, length + 1):
        spaces = length - i
        string = ' ' * spaces
        for j in range(0, 2 * i + 1):
            string += s[(idx + j) % len(s)]
        ans.append(string)
        idx += 1

    for i in range(length - 1, -1, -1):
        spaces = length - i
        string = ' ' * spaces
        for j in range(0, 2 * i + 1):
            string += s[(idx + j) % len(s)]
        ans.append(string)
        idx += 1

    return "\n".join(ans)


@app.route('/')
def index():
    user = session.get('user')
    if user:
        ist = pytz.timezone('Asia/Kolkata')
        indian_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
        return render_template('dashboard.html', user=user, time=indian_time)
    return render_template('login.html')

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

@app.route('/api/data')
def api_data():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    n_lines = request.args.get('num_lines', default=21, type=int)
    if n_lines < 1 or n_lines > 100:
        return jsonify({"error": "num_lines must be between 1 and 100"}), 400

    pattern = generate_letter_diamond(n_lines)
    return Response(pattern, mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True, port=1831)
