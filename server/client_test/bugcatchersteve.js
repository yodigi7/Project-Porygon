//Temporary Client Javascript file
$(document).ready(function() {
    var key = "a364f34bcbe84c7eb2002f1418c3d8f3";
    var socket = io.connect('http://127.0.0.1:5000');

    socket.on('connect', function () {
        console.log("Connected successfully. Logging in.")
        socket.emit('json', {login: key});
    });

    socket.on('message', function(msg) {
        // $("#messages").append('<li>'+msg+'</li>');
        console.log('Received message: ' + msg);
    });

    socket.on('json', function(obj) {
        console.log('Received json: ' + JSON.stringify(obj));
		
        if('success' in obj) {
            switch(obj.success) {
                case 'logged in':
                    console.log('Logged in. Selecting room and team.')
                    socket.emit('json', {room: -1, team: 'coolest bugs'})
                    break;
                case 'room joined':
                    console.log('Room joined. Awaiting battle start.')
                    socket.emit('json', {message: 'Hello, Room!'})
                    break;
            }
        }
        if('failure' in obj) {
        }
        if('disconnect' in obj) {
        }
        if('battleState' in obj) {
            socket.emit('action', {action: 'attack 0'}) //example
        }
        if('end' in obj) {
            switch(obj.end) {
                case 'Winner':
                    console.log('Winner. Game Ended.')
                    break;
                case 'Loser':
                    console.log('Loser. Game Ended.')
                    break;
            }
        }
    });
});
