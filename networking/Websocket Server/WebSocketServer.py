from flask import Flask
from flask_socketio import SocketIO, send
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

""" #TEMPLATE 
@socketio.on('specifyRoute')
def someFunction(ObjGivenByEmit):
    print(ObjGivenByEmit)
    send(ObjectGivenByEmit, broadcast=True)
"""

@socketio.on('message')
def messageHandler(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True) #send msg to everyone


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

if __name__=='__main__':
    socketio.run(app)