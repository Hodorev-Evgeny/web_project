let token = $('#token').data('token');
let target = $('#target').data('to');
console.log(`Target: ${target}`, target);
var socket = io();
function addMessage(text, from_id) {
    if (from_id != $('#target').data('to')) {
        $('#messages').append(`<p class="text-end">${text}</p>`);
    } else {
        $('#messages').append(`<p>${text}</p>`);
    }
}
function sendMessage(){
    let text = $('#messageBar').val();
    if (text == '') return;
    socket.emit('msg_send', {token: token, text: text, to: target});
    $('#messageBar').val('');
    addMessage(text, 0);
}
$('#sendButton').click(function () {
    sendMessage();
});
$('#messageBar').on('keypress', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
})
socket.on('connect', function () {
    $('#messages').empty();
    if (target != null) {
        socket.emit('auth', {token: token, target: target});
    }else{
        socket.emit('auth', {token: token});
    }
    socket.emit('get_user', {id: target});
});
socket.on('user', function (data) {
    console.log(data);
    $('#chatName').text(data.name);
})
socket.on('msg_recv', function (data) {
    console.log(data);
    addMessage(data.text, data.from_id);
});
socket.on('msg_init', function (data) {
    data.messages.forEach(element => {
        addMessage(element.text, element.from_id);
    });
});