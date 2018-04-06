from flask import Flask, request, render_template, session, url_for, redirect, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from functools import wraps
import os
import json
import uuid
from Room import Room, Player
import pokeutils as pk
import battle as bt


# Initialization

DEBUG = False

MAX_BOTS = 5
MAX_TEAMS = 5
NUM_ROOMS = 10

app = Flask(__name__)
app.secret_key = os.urandom(12)
socketio = SocketIO(app)

users_file = 'users.json'
user_settings_file = 'user_settings.json'

usernames = pk.load_from_file(users_file)
user_settings = pk.load_from_file(user_settings_file)
rooms = [Room() for _ in range(NUM_ROOMS)]
connected_users = {}

if not os.path.exists('teams'):
    os.mkdir('teams')


# Shortcuts

def persistent():
    """ Shortcut for user_settings[session['username']] """
    if session['username'] not in user_settings:
        user_settings[session['username']] = {
            'bots': [],
            'teams': []
        }
        pk.save_to_file(user_settings, user_settings_file)
    return user_settings[session['username']]


def connection():
    """ Shortcut for connected_users[request.sid] """
    return connected_users[request.sid]


# Helper Functions

def save_team(team, username=None):
    """ Saves the current user's team to file. """
    if username is None:
        username = session['username']
    pk.save_to_file(team, pk.TEAM_PATH.format(username, team['team_name']))


def load_team(team_name, username=None):
    """ Loads an existing team for the current user with the specified team_name. """
    if username is None:
        username = session['username']
    return pk.load_from_file(pk.TEAM_PATH.format(username, team_name))


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


# Socket Functions

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
    room_num = 0
    if 0 <= obj['room'] < NUM_ROOMS:
        if not rooms[obj['room']].is_full():
            room_num = obj['room']
        else:
            emit('json', {'failure': 'Room is full.'})
            return

    elif 0 > obj['room'] or NUM_ROOMS <= obj['room']:
        for r in range(len(rooms)):
            if not rooms[r].is_full():
                room_num = r
                break
        else:
            emit('json', {'failure': 'All rooms are full.'})
            return
    room = rooms[room_num]

    # Try to pick a team to use. If team name is invalid, cannot join room.
    team = None
    for account_team in persistent()['teams']:
        if account_team == obj['team']:
            team = load_team(obj['team'])

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
    connection()['room_num'] = room_num
    rooms[room_num].players.append(Player(request.sid, session['username'], team))
    join_room(room_num)
    emit('json', {'success': 'room joined'})
    print('{} joined room {}.'.format(session['username'], room_num))


def start_battle(room, room_broadcast):
    team_one = room.players[0].team
    team_two = room.players[1].team
    battle_dict = pk.initBattle(team_one, team_two)
    room.battle = battle_dict
    emit('json', {'battleState': battle_dict}, room=room_broadcast)  # Sending BattleJSON


# Website Routes

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


@app.route('/teambuilder/', methods=['GET', 'POST'])
@require_login
def teambuilder():
    if 'team' not in request.args or request.args['team'] not in persistent()['teams']:
        flash('Invalid team to edit.')
        return redirect('account')
    team = load_team(request.args['team'])

    if request.method == 'POST':
        # Get the POSTed data and the slot to edit, if available.
        slot = None
        if 'edit' in request.form:
            data = json.loads(request.form['edit'])
            slot = data['edit']
        else:
            data = json.loads(request.form['submit'])

        # Get the IDs for the POSTed team.
        new_team = json.loads(data['team'])
        new_team_names = json.loads(data['teamNames'])

        # Check that the team POSTed is of valid length.
        if len(new_team) != 6 or len(new_team_names) != 6:
            flash("An error occurred. The new team's length was invalid.")
            return render_template('teambuilder.html',
                                   team=[(i['id'] if i is not None else -1) for i in team['pokemon']])

        # Loop through each slot, checking for differences in IDs.
        # If differences are found, create a new pokemon and replace the old one (or swap it for None).
        for i in range(6):
            pkid = int(new_team[i])
            if pkid > pk.MAX_POKEMON_ID:
                flash('Pokemon ID out of range: {}'.format(new_team[i]))
                new_team[i] = -1
            if pkid > 0:
                if team['pokemon'][i] is None or team['pokemon'][i]['id'] != new_team[i]:
                    team['pokemon'][i] = pk.new_default_pokemon(new_team[i], new_team_names[i])
            else:
                team['pokemon'][i] = None
        save_team(team)

        if slot is not None:
            if team['pokemon'][slot] is None:
                flash("That slot is empty.")
                return render_template('teambuilder.html',
                                       team=[(i['id'] if i is not None else -1) for i in team['pokemon']])
            return redirect(url_for('editor', team=request.args['team'], slot=slot))
        return redirect(url_for('account'))

    # Only on method == GET, return template for the teambuilder.
    return render_template('teambuilder.html',
                           team=[(i['id'] if i is not None else -1) for i in team['pokemon']])


@app.route('/editor/', methods=['GET', 'POST'])
@require_login
def editor():
    # Verify that all request.args were provided that are required to operate this page.
    if 'team' not in request.args or request.args['team'] not in persistent()['teams']:
        flash('Invalid team to edit.')
        return redirect('account')
    if 'slot' not in request.args:
        flash('A slot must be selected for editing.')
        return redirect(url_for('teambuilder', team=request.args['team']))
    slot = int(request.args['slot'])
    if slot < 0 or slot >= 6:
        flash('Invalid slot to edit.')
        return redirect(url_for('teambuilder', team=request.args['team']))
    team_json = load_team(request.args['team'])
    pkmn_json = team_json['pokemon'][slot]

    if request.method == 'POST':
        # Check that all necessary keys are in the post.
        for key in ['nickname', 'gender', 'nature', 'ability', 'item', 'move0', 'move1', 'move2', 'move3',
                    'hpIV', 'attackIV', 'defenseIV', 'specialAttackIV', 'specialDefenseIV', 'speedIV',
                    'hpEV', 'defenseEV', 'specialDefenseEV']:
            if key not in request.form:
                flash('Missing key in form. key=' + key)
                return redirect(url_for('teambuilder', team=request.args['team']))

        # Assign values to the pokemon's json object.
        pkmn_json['nickname'] = request.form['nickname']
        pkmn_json['gender'] = request.form['gender']
        pkmn_json['nature'] = request.form['nature']
        pkmn_json['ability'] = request.form['ability']  # TODO: HTML for ability (needs implementation)
        pkmn_json['item'] = request.form['item']        # TODO: HTML for item (needs fixing)
        pkmn_json['moves'] = [
            request.form['move0'],
            request.form['move1'],
            request.form['move2'],
            request.form['move3']
        ]
        pkmn_json['ivalues'] = {
            'hp': int(request.form['hpIV']),
            'attack': int(request.form['attackIV']),
            'defense': int(request.form['defenseIV']),
            'special-attack': int(request.form['specialAttackIV']),
            'special-defense': int(request.form['specialDefenseIV']),
            'speed': int(request.form['speedIV'])
        }
        pkmn_json['evalues'] = {
            'hp': int(request.form['hpEV']),
            'defense': int(request.form['defenseEV']),
            'special-defense': int(request.form['specialDefenseEV'])
        }

        # TODO: Verify that the pokemon sent is actually possible to be created.
        if False:
            flash('Pokemon edited is invalid for at least one reason: {}'.format("<reason returned by verify()>"))
            return redirect(url_for('teambuilder', team=request.args['team']))

        # Pokemon has been validated, add it to the team and save the team back to file.
        team_json['pokemon'][slot] = pkmn_json
        save_team(team_json)

        return redirect(url_for('teambuilder', team=request.args['team']))

    # Get the pokemon that we're planning on editing.
    api_pokemon = pk.pb.pokemon(pkmn_json['species'])
    api_moves = [i.move.name for i in api_pokemon.moves]
    moves = [('-NONE-', '-NONE-')] + sorted([(i, pk.display_name_of(i)) for i in api_moves])

    return render_template('pokemonEditor.html', pokemon=pkmn_json, moves=moves)


@app.route('/account/', methods=['GET', 'POST'])
@require_login
def account():
    if request.method == 'POST':
        # Create a new bot.
        if 'newAI' in request.form:
            if len(persistent()['bots']) >= MAX_BOTS:
                flash("You are at the maximum number of AIs already.")
            else:
                bot_name = request.form['newAI']
                bot_key = uuid.uuid4().hex
                persistent()['bots'].append({'name': bot_name, 'key': bot_key})
                pk.save_to_file(user_settings, user_settings_file)

        # Delete one of your bots.
        elif 'deleteAI' in request.form:
            for i in range(len(persistent()['bots'])):
                if persistent()['bots'][i]['key'] == request.form['deleteAI']:
                    del persistent()['bots'][i]
                    pk.save_to_file(user_settings, user_settings_file)
                    flash("Successfully deleted your bot with ID: {}.".format(request.form['deleteAI']))
                    break
            else:
                flash("A bot with that ID does not exist.")

        # Create a new team for your bots to use.
        elif 'newTeam' in request.form:
            if len(persistent()['teams']) >= MAX_TEAMS:
                flash("You are at the maximum number of Teams already.")
            else:
                # Check if the team name chosen already exists.
                for team in persistent()['teams']:
                    if team['name'] == request.form['newTeam']:
                        flash("Team name must be unique!")
                        break
                else:  # else is triggered if the break statement was not hit.
                    # If the team name chosen did not already exist, create it.
                    if not os.path.isdir(pk.USER_TEAMS_DIR.format(session['username'])):
                        os.mkdir(pk.USER_TEAMS_DIR.format(session['username']))
                    persistent()['teams'].append(request.form['newTeam'])
                    pk.save_to_file(user_settings, user_settings_file)
                    save_team(pk.new_default_team(session['username'], request.form['newTeam']))

        # Go to the editor to customize your team.
        elif 'editTeam' in request.form:
            return redirect(url_for('teambuilder', team=request.form['editTeam']))

        # Delete one of your teams.
        elif 'deleteTeam' in request.form:
            if request.form['deleteTeam'] in persistent()['teams']:
                # Delete the team from the user settings file, then delete the team file from the file system.
                index = persistent()['teams'].index(request.form['deleteTeam'])
                del persistent()['teams'][index]
                pk.save_to_file(user_settings, user_settings_file)
                os.remove(pk.TEAM_PATH.format(session['username'], request.form['deleteTeam']))
                if len(persistent()['teams']) == 0:
                    os.remove(pk.USER_TEAMS_DIR.format(session['username']))
                flash("Successfully deleted you team: {}.".format(request.form['deleteTeam']))
            else:
                flash("That team does not exist.")

    # Render the account page on either POST or GET.
    return render_template('account.html', bots=persistent()['bots'], teams=persistent()['teams'])


@app.route('/signup/', methods=['GET', 'POST'])
@require_logged_out
def signup():  # TODO: A link on the website to get to the signup page.
    if request.method == 'POST':
        if user_exists(request.form['username']):
            flash("That username is already in use.", 'error')
        else:
            usernames[request.form['username']] = request.form['password']
            pk.save_to_file(usernames, users_file)
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
def logout():  # TODO: A link on the website to logout.
    if 'username' in session:
        del session['username']

    return redirect(url_for('login'))


# Socket Events

@socketio.on('connect')
def on_connect():
    connected_users[request.sid] = {}
    print("Bot connected with session id: " + request.sid)


@socketio.on('disconnect')
def on_disconnect():
    if 'room_num' in connection():
        print("Player disconnected from room {}. Resetting room...".format(connection()['room_num']))
        leave_room(connection()['room_num'])
        r = rooms[connection()['room_num']]

        #  Send a message to all other players in the room that one player disconnected.
        #  Then, remove all players from the room.
        for i in range(len(r.players)):
            if r.players[i].sid != request.sid:
                emit('json', {'disconnect': 'another player has disconnected'}, room=r.players[i].sid)
                del connected_users[r.players[i].sid]['room_num']
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
    if 'room_num' not in connection():
        bot_join_room(obj)
        if 'room_num' in connection() and rooms[connection()['room_num']].is_full():
            start_battle(rooms[connection()['room_num']], connection()['room_num'])
        return

    # AI is alreay in a room
    print("AI of {} sent json << {} >> from room: {}".format(session['username'], obj, connection()['room_num']))


@socketio.on('text')
def on_textfile(data):
    content = data['txtdata']
    print(content)

    # reading in the filename from the header specified from the request header
    filename = data['filename']

    if not os.path.exists('text/'):  # making sure text directory is created
        os.makedirs('text')

    with open('text/' + filename, 'w') as f:
        f.write(content)  # writing text contents in text directory with file specified in header

    return 'Received Battle File for visualization'


@socketio.on('action')
def on_action(data):
    print("Action << {} >> called from Room #{} sent by {}".format(data, connection()['room_num'], session['username']))
    r = rooms[connection()['room_num']]

    # This block is used to check if a player has sent more than one action
    for player in r.players:
        if player.username == session['username']:
            if not player.actionUsed:
                player.actionUsed = data
            else:
                print("Player: {} sent action twice".format(player.username))

    # Send an updated battleJSON if no end condition has been met
    # If all players have submitted an action
    if all(player.actionUsed is not False for player in r.players):
        teams = []
        actions = []
        for player in r.players:
            teams.append(player.team)

            action_dict = {
                'player': player.username,
                'action': player.actionUsed['action']
            }
            actions.append(action_dict)

        r.battle = bt.performTurn(r.battle, actions, teams)

        # Through the main battle function check if the player lost or won
        end_condition = False
        if r.battle['loser'] != 'none':
            end_condition = True

        calling_room = connection()['room_num']  # the client who called the action function's room
        if end_condition:
            print("Battle Ended Successfully (By end_condition = True)")
        else:
            print("Should be printed when 2 players submit an action")  # Obviously when no end condition has been met
            print('Updated Battle JSON sent to all players in the room #{}'.format(connection()['room_num']))

            #  temporary output for demonstration
            for player in r.battle['players']:
                print(player['active_pokemon'])

            emit('json', {'battleState': r.battle}, room=calling_room)  # Sending BattleJSON
            for player in r.players:
                player.actionUsed = False


# Run the server.
socketio.run(app, port=80, debug=DEBUG)
