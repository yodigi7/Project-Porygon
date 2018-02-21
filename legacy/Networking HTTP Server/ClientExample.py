#Example File to send data to server
#In order for the client example to work the server.py must be running

import sys
import json
import requests

#Temporary reading json for example
data = open('examples/exampleBattle.json')
data = json.load(data)

#For http://127.0.0.1:5000/*, the * defines the function the request goes to
url = "http://127.0.0.1:5000/receiveJson/"
header = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Filename': 'exampleBattle.json'} #Storing extra data
response = requests.post(url, data=json.dumps(data), headers = header)
print(response.content.decode("utf-8")) #the return statement from the /receiveJson/

data = open('examples/87759413-5681-40eb-8546-9cc7f5874e88.json')
data = json.load(data)

url = "http://127.0.0.1:5000/receiveJson/"
header = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Trainer': 'bugcatchercindy','Filename': '87759413-5681-40eb-8546-9cc7f5874e88.json'}
response = requests.post(url, data=json.dumps(data), headers = header)
print(response.content.decode("utf-8"))


url = "http://127.0.0.1:5000/textFiles/"
with open('examples/exampleTextFile.txt', 'r') as exampleFile:
    data = exampleFile.read()
header = {'Content-type': 'text/css', 'Filename': 'BattleFileName.txt'} #different content type for just text files
response = requests.post(url, data, headers = header)
print(response.content.decode("utf-8"))