#Server: Receiving Requests and Handling Them Accordingly + Testing Server Showing Webpage
import flask, flask.views
import json
import os

app = flask.Flask(__name__)

#Function used to store and receive JSON files
@app.route('/receiveJson/', methods = ['GET','POST'])
def JsonHandler():
    content = flask.request.get_json()
    #print(content)

    #Depending on the first key (very left key) it determines different types of json
    if 'pokemon' in content: #Trainer Json
        Trainer = flask.request.headers.get('Trainer') #Trainer is specified by the client

        if not os.path.exists('Trainers/'+Trainer):
            os.makedirs('Trainers/'+Trainer)
        # else the trainer directory already exists

        with open('Trainers/'+Trainer+'/'+flask.request.headers.get('Filename'), 'w') as F:
            F.write(json.dumps(content, indent=2))

        print('Player JSON Received')
        return 'Player JSON Received'

    elif 'players' in content: #exampleBattle.json
        print('Battle JSON Received') #Do something with Battle JSON
        return 'Battle JSON Received'

    else:
        #print("JSON had trouble parsing")
        return 'Error reading in JSON'


#Function used to store and receive text
@app.route('/textFiles/', methods = ['GET','POST'])
def battleFiles():
    content = flask.request.data.decode("utf-8")
    #print(content)

    #reading in the filename from the header specified from the request header
    filename = flask.request.headers.get('Filename')

    if not os.path.exists('text/'): #making sure text directory is created
        os.makedirs('text')

    with open ('text/' + filename, 'w') as f:
        f.write(content) #writing text contents in text directory with file specified in header

    return 'Received Battle File for visualization'


#Testing Flask by going to http://127.0.0.1:5000/
class View(flask.views.MethodView):
    def get(self):
        return "Hello world!"
app.add_url_rule('/', view_func=View.as_view('main'))

app.run()