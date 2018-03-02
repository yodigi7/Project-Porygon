from flask import Flask, request, render_template, session, abort, url_for, redirect, flash
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from functools import wraps
import os
import json
import uuid
from server.Room import Room, Player
import pokeutils as pokeutils

# Shortcuts

def persistent():
    """ Shortcut for user_settings[session['username']] """
    if session['username'] not in user_settings:
        user_settings[session['username']] = {
            'bots': []
        }
        save_to_file(user_settings, user_settings_file)
    return user_settings[session['username']]

def connection():
    """ Shortcut for connected_users[request.sid] """
    return connected_users[request.sid]

# Helper functions

def save_to_file(data, filepath):
    """ Saves JSON from 'data' to a file at 'filepath'. """
    with open(filepath, 'w') as f:
        json.dump(data, f)

def load_from_file(filepath):
    """ Returns a JSON structure loaded from 'filepath'. """
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            u = json.load(f)
        return u
    return {}

def user_exists(username):
    """ Returns true if the 'username' is an existing one. """
    return username in usernames

def valid_login(username, password):
    """ Returns true if the username/password combination is a match. """
    return username in usernames and usernames[username] == password

# Decorators

def require_login(func):
    """ Decorator to redirect to the login page if not logged in. """
    @wraps(func)
    def f(*args, **kwargs):
        if 'username' not in session:
            flash("You must be logged in to visit this page.", 'error')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return f

def require_logged_out(func):
    """ Decorator to redirect to home page if already logged in. """
    @wraps(func)
    def f(*args, **kwargs):
        if 'username' in session:
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return f

# Initialization

MAX_BOTS = 5
MAX_TEAMS = 5
NUM_ROOMS = 10

app = Flask(__name__)
app.secret_key = "This isn't very secret"
socketio = SocketIO(app)

users_file = 'users.json'
user_settings_file = 'user_settings.json'

usernames = load_from_file(users_file)
user_settings = load_from_file(user_settings_file)
rooms = [Room() for _ in range(NUM_ROOMS)]
connected_users = {}

# Socket functions

def bot_login(obj):
    for u, s in user_settings.items():
        for bot in s['bots']:
            if bot['key'] == obj['login']:
                session['username'] = u
                session['bot'] = bot
                emit('json', {'success': 'logged in'})
                print("Bot identified as: {}, {} with key: {}".format(u, bot['name'], bot['key']))
                return
    emit('json', {'failure', 'invalid login'})

def bot_join_room(obj):
    if 'room' not in obj or 'team' not in obj:
        emit('json', {'failure': 'send room and team choice'})
        return

    # Try to pick a room to join. A room choice outside room index bounds becomes auto-assign.
    room = None
    if 0 <= obj['room'] < NUM_ROOMS and not rooms[obj['room']].is_full():
            room = obj['room']
    elif 0 > obj['room'] or NUM_ROOMS <= obj['room']:
        for r in range(len(rooms)):
            if not rooms[r].is_full():
                room = r
                break

    # Try to pick a team to use. If team name is invalid, cannot join room.
    team = None
    for team_name in persistent()['teams']:
        if team_name == obj['team']:
            team = team_name
            break

    # If both the room and team were valid choices, join the room using the team requested.
    if room is None or team is None:
        emit('json', {
            'failure': {
                'room': ('full' if room is None else 'available'),
                'team': ('invalid' if team is None else 'valid')
        }})
        print('Invalid room/team request from {}'.format(session['username']))
        return

    # Connect user to room, send success message.
    connection()['room'] = room
    rooms[room].players.append(Player(request.sid, session['username'], team))
    join_room(room)
    emit('json', {'success': 'room joined'})
    print('{} joined room {}.'.format(session['username'], room))

def start_battle(room_id):
    team_one = pokeutils.load_data('../examples/bugcatchercindy/87759413-5681-40eb-8546-9cc7f5874e88.json')
    team_two = pokeutils.load_data('../examples/bugcatchersteve/410a089a-9e6b-4a8b-bddd-c5480f02c389.json')
    pokeutils.initBattle(team_one, team_two)
    battle_json = pokeutils.load_data('../examples/exampleBattle.json')
    emit('json', {'battleState': battle_json}, room=room_id) #Sending BattleJSON

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

@app.route('/teambuilder/')
@require_login
def teambuilder():
    return render_template('teambuilder.html')

@app.route('/account/', methods=['GET', 'POST'])
@require_login
def account():
    if request.method == 'POST':
        if 'newAI' in request.form:
            if len(persistent()['bots']) >= MAX_BOTS:
                flash("You are at the maximum number of AIs already.")
            else:
                bot_name = "Bot " + str(len(persistent()['bots']))
                bot_key = uuid.uuid4().hex
                persistent()['bots'].append({'name': bot_name, 'key': bot_key})
                save_to_file(user_settings, user_settings_file)
        elif 'deleteAI' in request.form:
            for i in range(len(persistent()['bots'])):
                if persistent()['bots'][i]['key'] == request.form['deleteAI']:
                    del persistent()['bots'][i]
                    save_to_file(user_settings, user_settings_file)
                    break
    return render_template('account.html', bots=persistent()['bots'])

@app.route('/signup/', methods=['GET', 'POST'])
@require_logged_out
def signup():
    if request.method == 'POST':
        if user_exists(request.form['username']):
            flash("That username is already in use.", 'error')
        else:
            usernames[request.form['username']] = request.form['password']
            save_to_file(usernames, users_file)
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
def on_connect():
    connected_users[request.sid] = {}
    print("Bot connected with session id: " + request.sid)

@socketio.on('disconnect')
def on_disconnect():
    if 'room' in connection():
        print("Player disconnected from room {}. Resetting room...".format(connection()['room']))
        leave_room(connection()['room'])
        r = rooms[connection()['room']]

        # Send a message to all other players in the room that one player disconnected.
        #   Then, remove all players from the room.
        for i in range(len(r.players)):
            if r.players[i].sid != request.sid:
                emit('json', {'disconnect': 'another player has disconnected'}, room=r.players[i].sid)
                del connected_users[r.players[i].sid]['room']
        r.players = []

    # Remove the user from our connected users.
    print("Bot disconnected with session id: " + request.sid)
    del connected_users[request.sid]

@socketio.on('message')
def on_message(msg):
    if 'bot' not in session:
        print("Unauthorized message")
        return

    print('Message: ' + msg)

#  alternatively depending on what the client is sending,
#  we could just send json based on events specified
@socketio.on('json')
def on_json(obj):
    # Exhaustive search to find out which bot this is...
    if 'bot' not in session and 'login' in obj:
        bot_login(obj)
        return

    if 'bot' not in session:
        print("Unauthorized JSON")
        return

    # If the bot is not yet in a room,
    if 'room' not in connection():
        bot_join_room(obj)
        if 'room' in connection() and rooms[connection()['room']].is_full():
            start_battle(connection()['room'])
        return

    # AI is alreay in a room
    print("AI of {} sent json << {} >> from room: {}".format(session['username'], obj, connection()['room']))


@socketio.on('text')
def on_textfile(data):
    content = data['txtdata']
    print(content)

    #reading in the filename from the header specified from the request header
    filename = data['filename']

    if not os.path.exists('text/'): #making sure text directory is created
        os.makedirs('text')

    with open('text/' + filename, 'w') as f:
        f.write(content) #writing text contents in text directory with file specified in header

    return 'Received Battle File for visualization'

@socketio.on('action')
def on_action(data):
    print("Action << {} >> called from Room #{} sent by {}".format(data, connection()['room'], session['username']))
    r = rooms[connection()['room']]

    #This block is used to check if a player has sent more than one action
    for player in r.players:
        if player.username == session['username']:
            if player.actionUsed == False:
                player.actionUsed = data
            else:
                print("Player: {} sent action twice".format(player.username))

    #This is where we would prob call the main battle function (which would return the updated battle json)
    battle_json = pokeutils.load_data('../examples/exampleBattle.json')

    #Through the main battle function check if the player lost or won
    endCondition = False #Temporary use of an end condition (if false loop occurs)
    if (endCondition):
        for i in r.players:
            if i.sid == request.sid:
                if (data['action'] == "attack 2"):
                    emit('json', {'end': 'Winner of Room#{}'.format(connection()['room'])}, room=request.sid)
                elif (data['action'] == "attack 4"):
                    emit('json', {'end': 'Loser of Room#{}'.format(connection()['room'])}, room=request.sid)
        print("Battle Ended Successfully")
    else:
        #Send an updated battleJSON if no end condition has been met
        if all(player.actionUsed != False for player in r.players):
           print('Updated Battle JSON sent to all players in the room #{}'.format(connection()['room']))
           emit('json', {'battleState': 'Updated Battle JSON sent to all players in the room #{}'.format(connection()['room'])}, room=connection()['room'])
           for player in r.players:
               player.actionUsed = False
							 
socketio.run(app, debug=False)
