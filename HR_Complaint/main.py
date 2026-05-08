import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key"
DATA_FILE = 'data.json'

# --- JSON HELPER FUNCTIONS ---
def load_data():
    if not os.path.exists(DATA_FILE):
        # Create default structure if file doesn't exist
        initial_data = {"users": {}, "complaints": []}
        save_data(initial_data)
        return initial_data
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- ROUTES ---

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('username')
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        data = load_data()

        if email in data['users']:
            flash("An account with this email already exists.", "warning")
            return redirect(url_for('register'))

        # Save user (Email is the unique key)
        data['users'][email] = {
            'full_name': full_name,
            'password': generate_password_hash(password),
            'role': 'employee',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_data(data)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email_id').lower().strip()
        password = request.form.get('password')

        data = load_data()
        user = data['users'].get(email)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = email
            return redirect(url_for('complaint'))
        
        flash("Invalid Credentials", "danger")
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = load_data()
        
        new_complaint = {
            'user': session['user_id'],
            'subject': request.form['subject'],
            'description': request.form['description'],
            'anonymous': True if request.form.get('anonymous') else False,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        data['complaints'].append(new_complaint)
        save_data(data)
        return "<h1>Success! HR has received your complaint.</h1>"
    
    return render_template('complaint.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
