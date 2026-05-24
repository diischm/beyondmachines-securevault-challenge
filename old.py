from flask import Flask, request, render_template_string, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # 🚩 Red flag #1

# "Secure" user database
users = {
    "admin": "password123",
    "user": "qwerty", 
    "guest": "guest"
}

# Password vault
vault = {
    "admin": ["gmail:admin@email.com:MySecureP@ssw0rd", "bank:admin:VerySecret123"],
    "user": ["facebook:user@email.com:password123"],
    "guest": []
}

@app.route('/')
def home():
    if 'username' in session:
        return f'''
        <h1>Welcome to SecureVault, {session['username']}!</h1>
        <a href="/vault">View Your Passwords</a> | 
        <a href="/admin">Admin Panel</a> | 
        <a href="/logout">Logout</a>
        '''
    return '''
    <h1>SecureVault - Ultra Secure Password Manager</h1>
    <form method="POST" action="/login">
        Username: <input name="username" required><br><br>
        Password: <input name="password" type="password" required><br><br>
        <button>Login</button>
    </form>
    <p><small>Try: admin/password123 or user/qwerty</small></p>
    '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Super secure authentication logic
    if username in users and users[username] == password:
        session['username'] = username
        return redirect('/')
    
    return "Invalid credentials! <a href='/'>Try again</a>"

@app.route('/vault')
def vault_view():
    if 'username' not in session:
        return redirect('/')
    
    username = session['username']
    user_passwords = vault.get(username, [])
    
    html = f"<h1>{username}'s Password Vault</h1>"
    if user_passwords:
        html += "<ul>"
        for pwd in user_passwords:
            html += f"<li>{pwd}</li>"
        html += "</ul>"
    else:
        html += "<p>No passwords stored yet.</p>"
    
    html += "<br><a href='/'>Home</a>"
    return html

@app.route('/admin')
def admin_panel():
    if 'username' not in session:
        return redirect('/')
    
    # 🚩 Red flag #2 - What's wrong with this check?
    if session['username'] == 'admin':
        return '''
        <h1>Admin Panel - TOP SECRET</h1>
        <h2>All User Data:</h2>
        <pre>''' + str(vault) + '''</pre>
        <h2>System Info:</h2>
        <p>Flag: CHALLENGE_COMPLETED</p>
        <a href="/">Home</a>
        '''
    
    return "Access Denied! Admins only! <a href='/'>Home</a>"

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if 'username' not in session:
        return redirect('/')
    
    # 🚩 Red flag #3 - This looks suspicious...
    template = f'''
    <h1>Search Results for: {query}</h1>
    <p>No results found.</p>
    <form>
        <input name="q" placeholder="Search..." value="{query}">
        <button>Search</button>
    </form>
    <a href="/">Home</a>
    '''
    
    return render_template_string(template)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
