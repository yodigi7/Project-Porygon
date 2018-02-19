from flask import Flask, request, render_template, session, abort, url_for, redirect, flash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = "This isn't very secret"

users = {}


# Decorator to redirect to login page if not logged in.
def require_login(func):
	@wraps(func)
	def f(*args, **kwargs):
		if 'username' not in session:
			return redirect(url_for('login'))
		return func(*args, **kwargs)
	return f


def user_exists(username):
	return username in users


def valid_login(username, password):
	return username in users and users[username] == password


@app.route('/')
def home():
	return render_template('home.html')


@app.route('/leaderboard/')
@require_login
def leaderboard():
	return render_template('leaderboard.html')


@app.route('/battle/')
def battle():
	return render_template('battle.html')


@app.route('/account/')
@require_login
def account():
	return render_template('account.html')


@app.route('/login/')
def login():
	if request.method == 'GET':
		return render_template('login.html')
	if request.method == 'POST':
		if not valid_login(request.form['username'], request.form['password']):
			flash("Invalid username or password.")
			return render_template('login.html')
		session['username'] = request.form['username']
		return redirect(url_for('home'))


@app.route('/signup/')
def signup():
	if request.method == 'GET':
		return render_template('signup.html')
	if request.method == 'POST':
		if user_exists(request.form['username']):
			flash("That username is already in use.")
			return render_template('signup.html')
		users[request.form['username']] = request.form['password']
		session['username'] = request.form['username']
		return redirect(url_for('home'))

if __name__ == '__main__':
	app.run(debug = True)