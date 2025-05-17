from flask import Flask, render_template, url_for, flash, redirect, request, send_from_directory, session
import os
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
import pipeline
from werkzeug.security import check_password_hash, generate_password_hash

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.secret_key = 'key'

users = {
    'user1': generate_password_hash('password1'),
    'user2': generate_password_hash('password2'),
    'user3': generate_password_hash('password3')
}

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', result=None)
    return redirect(url_for('login'))

@app.route('/assessment', methods=['GET', 'POST'])
def upload_and_classify():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        model_results = pipeline.pipe(filepath)
        return render_template('results.html', result=model_results, scroll='third', filename=filename)
    flash('Invalid file format. Please try again.')
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists. Please choose a different one.')
        else:
            users[username] = generate_password_hash(password)
            flash('Sign up successful! Please log in.')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    # flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

