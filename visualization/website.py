from flask import Flask, request, render_template, session, abort
import os

app = Flask(__name__)

@app.route('/')
def home():
	#if not session.get('logged_in'):
	#	return render_template('login.html')
	#else:
		return render_template('home.html')

@app.route('/leaderboard_page/')
def leaderboard():
	return render_template('leaderboard.html')

@app.route('/battle_page/')
def battle():
	return render_template('battle.html')

@app.route('/account_page/')
def account():
	return render_template('account.html')

@app.route('/login_page/')
def login():
	return render_template('login.html')

if __name__ == '__main__':
	app.run(debug = True)