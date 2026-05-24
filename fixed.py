from datetime import timedelta
from flask import Flask, request, render_template_string, session, redirect, url_for
import os
import secrets
import bcrypt

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY') # added an environemnt variable based secret key
if not app.secret_key:
    raise RuntimeError('FLASK_SECRET_KEY not set')

app.config.update( # more security options for preventing cookie forgery
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,        # this should be changed to True in deployment, localhost is http so this would brake the app in production testing
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30), # session lasted 31 days lol
)

roles = { #not checking by username, but checking the role of the user
    "admin": "administrator",
    "user": "user",
    "guest": "user"
}

_initial_users = {
    "admin": "password123",
    "user": "qwerty",
    "guest": "guest"
}

users = {
    name: bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    for name, password in _initial_users.items()
}

del _initial_users

vault = {
    name : []
    for name in users
}
vault["admin"].extend([
    "gmail:admin@email.com:MySecureP@ssw0rd",
    "bank:admin:VerySecret123",
])
vault["user"].append("facebook:user@email.com:password123")


@app.route('/')
def home():
    if 'username' in session:
        return render_template_string(
            '''
            <h1>Welcome to SecureVault, {{ username }}!</h1>
            <a href="/vault">View Your Passwords</a> | 
            <a href="/admin">Admin Panel</a> | 
            <a href="/logout">Logout</a>
            ''',
            username=session['username'],
        )
    return '''
    <h1>SecureVault - Ultra Secure Password Manager</h1>
    <form method="POST" action="/login">
        Username: <input name="username" required><br><br>
        Password: <input name="password" type="password" required><br><br>
        <button>Login</button>
    </form>
    '''



@app.route('/login', methods=['POST'])
def login():

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    stored_hash = users.get(username)

    if stored_hash and bcrypt.checkpw(password.encode(), stored_hash):
        session['username'] = username
        session['role'] = roles.get(username, 'user')
        session.permanent = True
        return redirect('/')

    return "Invalid credentials! <a href='/'>Try again</a>", 401 # interesting feature, error code for no such user and wrong password


@app.route('/vault')
def vault_view():
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    user_passwords = vault.get(username, [])

    return render_template_string(
        '''
        <h1>{{ username }}'s Password Vault</h1>
        {% if passwords %}
            <ul>
            {% for pwd in passwords %}
                <li>{{ pwd }}</li>
            {% endfor %}
            </ul>
        {% else %}
            <p>No passwords stored yet.</p>
        {% endif %}
        <br><a href="/">Home</a>
        ''',
        username=username,
        passwords=user_passwords,
    )


@app.route('/admin')
def admin_panel():
    if 'username' not in session:
        return redirect('/')

    if session.get('role') != 'administrator':
        return "Access Denied! Admins only! <a href='/'>Home</a>", 403

    user_summary = {name: len(vault.get(name, [])) for name in users} # no need for admin to see sensitive info, that is being viewed by accessing vault

    return render_template_string(
        '''
        <h1>Admin Panel</h1>
        <h2>Users:</h2>
        <ul>
        {% for name, count in users.items() %}
            <li>{{ name }} — {{ count }} vault entries</li>
        {% endfor %}
        </ul>
        <p>Flag: CHALLENGE_COMPLETED</p>
        <a href="/">Home</a>
        ''',
        users=user_summary,
    )


@app.route('/search')
def search():
    if 'username' not in session:
        return redirect('/')

    query = request.args.get('q', '')

    return render_template_string(
        '''
            <h1>Search Results for: {{ query }}</h1>
            <p>No results found.</p>
            <form>
                <input name="q" placeholder="Search..." value="{{ query }}">
                <button>Search</button>
            </form>
            <a href="/">Home</a>
            ''',
            query = query,
    )





@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=5000) #debug=True is not bad at the moment, could be environement controlled but that would be annoying in development, this should be False when deployed