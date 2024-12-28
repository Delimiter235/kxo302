$(document).ready(function() {
    var socket = io()
    socket.on('connect', function() {
        socket.send("User has connected!")
    });

    $('form#joinRoom').submit(function(event) {
        socket.emit('joinRoom', {
            room:$('#roomNum').val()
        });
        return false
    });

    socket.on('roomJoined', function(msg, cb) {
        $('#chatContent').append('<li>' + msg.user + " has joined the " + msg.room + '</li>')
    });

    socket.on('roomLeft', function(msg, cb) {
        $('#chatContent').append('<li>' + msg.user + " has left the " + msg.room + '</li>')
    });

    socket.on('roomLeftPersonal', function(msg, cb) {
        $('#chatContent').append('<li>' + " You have already left the " + msg.room + '</li>')
    });

    $('#leaveRoom').on('click', function() {
        socket.emit('leaveRoom', {
            room:$('#roomNum').val()
        });
    });

    $('form#submitForm').submit(function() {
        socket.emit('sendMsg', {
            msg:$('#chatMsg').val(),
            room:$('#roomNum').val()
        });
        $('#chatMsg').val('');
        return false
    });

    socket.on('sendToAll', function(msg, cb) {
        $('#chatContent').append('<li>' + msg.user + ": " + msg.msg + '</li>')
    });
})
