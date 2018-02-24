from flask import Flask, request, render_template, session, abort, url_for, redirect, flash
from flask_socketio import SocketIO, send
from functools import wraps
import os
import json
import uuid


MAX_BOTS = 5

app = Flask(__name__)
app.secret_key = "This isn't very secret"
socketio = SocketIO(app)

users_file = 'users.json'
user_settings_file = 'user_settings.json'


def user():
    if session['username'] not in user_settings:
        user_settings[session['username']] = {
            'bots': []
        }
        save_to_file(user_settings, user_settings_file)
    return user_settings[session['username']]

def save_to_file(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f)

def load_from_file(filepath):
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            u = json.load(f)
        return u
    return {}

def user_exists(username):
    return username in users

def valid_login(username, password):
    return username in users and users[username] == password


# Decorator to redirect to login page if not logged in.
def require_login(func):
    @wraps(func)
    def f(*args, **kwargs):
        if 'username' not in session:
            flash("You must be logged in to visit this page.", 'error')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return f

# Decorator to redirect to home page if logged in.
def require_logged_out(func):
    @wraps(func)
    def f(*args, **kwargs):
        if 'username' in session:
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return f

# ************** #
# WEBSITE ROUTES #
# ************** #

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/leaderboard/')
@require_login
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/battle/')
@require_login
def battle():
    return render_template('battle.html')

@app.route('/account/', methods=['GET', 'POST'])
@require_login
def account():
    if request.method == 'POST':
        if 'newAI' in request.form:
            if len(user()['bots'] >= MAX_BOTS):
                flash("You are at the maximum number of AIs already.")
            else:
                bot_name = "Bot " + str(len(user()['bots']))
                bot_key = uuid.uuid4()
                user()['bots'].append({'name': bot_name, 'key': bot_key})
                save_to_file(user_settings, user_settings_file)
        elif 'deleteAI' in request.form:
            for i in range(len(user()['bots'])):
                if user()['bots'][i]['key'] == request.form['deleteAI']:
                    del user()['bots'][i]
                    save_to_file(user_settings, user_settings_file)
                    break
    return render_template('account.html', bots=user()['bots'])

@app.route('/signup/', methods=['GET', 'POST'])
@require_logged_out
def signup():
    if request.method == 'POST':
        if user_exists(request.form['username']):
            flash("That username is already in use.", 'error')
        else:
            users[request.form['username']] = request.form['password']
            save_to_file(users, users_file)
            session['username'] = request.form['username']
            return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login/', methods=['GET', 'POST'])
@require_logged_out
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        if not valid_login(request.form['username'], request.form['password']):
            flash("Invalid username or password.", 'error')
        else:
            session['username'] = request.form['username']
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout/')
def logout():
    if 'username' in session:
        del session['username']

    return redirect(url_for('login'))

# ************* #
# SOCKET EVENTS #
# ************* #

@socketio.on('connect')
def connect():
    print("User Connected.")

@socketio.on('message')
def messageHandler(msg):
    print('Message: ' + msg)

#  alternatively depending on what the client is sending,
#  we could just send json based on events specified
@socketio.on('jsonParse')
def parse_Json(jsonObject):
    send("JSONObject Obtained")
    jsonData = jsonObject['jsondata']
    print(jsonData)

    if 'pokemon' in jsonData:  # Trainer Json
        Trainer = jsonObject['trainer']
        FileName = jsonObject['filename']

        if not os.path.exists('Trainers/' + Trainer):
            os.makedirs('Trainers/' + Trainer)
        # else the trainer directory already exists

        with open('Trainers/' + Trainer + '/' + FileName, 'w') as F:
            F.write(json.dumps(jsonData, indent=2))

        print('Player JSON Received')
        return 'Player JSON Received'

    elif 'players' in jsonData:  # exampleBattle.json
        print('Battle JSON Received')  # Do something with Battle JSON
        return 'Battle JSON Received'

    else:
        print("JSON had trouble parsing")
        return 'Error reading in JSON'

@socketio.on('textFiles')
def battleFiles(data):
    content = data['txtdata']
    print(content)

    #reading in the filename from the header specified from the request header
    filename = data['filename']

    if not os.path.exists('text/'): #making sure text directory is created
        os.makedirs('text')

    with open ('text/' + filename, 'w') as f:
        f.write(content) #writing text contents in text directory with file specified in header

    return 'Received Battle File for visualization'


if __name__ == '__main__':
    users = load_from_file(users_file)
    user_settings = load_from_file(user_settings_file)
    socketio.run(app, debug=True)