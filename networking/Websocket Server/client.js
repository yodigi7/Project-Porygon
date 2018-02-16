//Temporary Client Javascript file
$(document).ready(function() {
    var socket = io.connect('http://127.0.0.1:5000');

    socket.on('connect', function () {

        socket.send('User has connected!'); //send to socketio.on('message')

        $.getJSON('TemporaryReusedExamples/exampleBattle.json', function(data){
            var jsonData1 = {
                jsondata: data,
                filename: 'battleFile.txt'
            };
            socket.emit('jsonParse', jsonData1);
        });
        console.log("Example Battle Sent");

        $.getJSON('TemporaryReusedExamples/bugcatchercindy/87759413-5681-40eb-8546-9cc7f5874e88.json', function(data){
            var jsonData2 = {
                jsondata: data,
                filename: '87759413-5681-40eb-8546-9cc7f5874e88.json',
                trainer: 'BugCatcherCindy'
            };
            socket.emit('jsonParse', jsonData2);
        });
        console.log("Bug Catcher Cindy Sent");

        $.getJSON('TemporaryReusedExamples/bugcatchersteve/410a089a-9e6b-4a8b-bddd-c5480f02c389.json', function(data){
            var jsonData3 = {
                jsondata: data,
                filename: '410a089a-9e6b-4a8b-bddd-c5480f02c389.json',
                trainer: 'BugCatcherSteve'
            };
            socket.emit('jsonParse', jsonData3);
        });
        console.log("Bug Catcher Steve Sent");

        $.get('TemporaryReusedExamples/exampleTextFile.txt', function(data){
            var txtData1 = {
                txtdata: data,
                filename: 'TxtFile4Battle.txt',
            };
            socket.emit('textFiles', txtData1);
        });
        console.log("Example Text File Sent");

        console.log("Finished!")
    });

    /*socket.on('message', function(msg) {
        $("#messages").append('<li>'+msg+'</li>');
        console.log('Received message');
    });*/
});