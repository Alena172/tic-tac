var socket = io();
var player;
var opponent;
var turn = 'X';
var gameOver = false; // Переменная для отслеживания состояния игры

socket.on('init', function(data) {
    player = data.player;
    highlightCurrentPlayer();
    if (data.message) {
        displayMessage(data.message);
    }
});

socket.on('message', function(data) {
    if (data.init !== undefined && data.init === false) {
        document.getElementById('cell-' + data.cell).innerText = data.player;
        turn = data.nextTurn;
        highlightCurrentPlayer();
    }
    if (data.message && data.message !== 'move') {
        displayMessage(data.message); // Вывод сообщения о победе
    }
    if (data.gameOver) {
        gameOver = true;
        document.getElementById('reset-button').style.display = 'block';
    }
});

socket.on('players', function(data) {
    player = data.player;
    opponent = data.opponent;
    updatePlayerNames();
});

socket.on('winning_combo', function(data) {
    const combo = data.combo;
    const cells = document.querySelectorAll('#board > div');
    combo.forEach(index => {
        cells[index].style.border = '2px solid red';
    });
});

function makeMove(cell) {
    if (gameOver) return; // Запрещаем ходы после окончания игры
    socket.emit('move', JSON.stringify({cell: cell, player: player}));
}

function displayMessage(message) {
    var messagesDiv = document.getElementById('messages');
    var messageElement = document.createElement('div');
    messageElement.textContent = message;
    messagesDiv.appendChild(messageElement);
}

function openModal() {
    var modal = document.getElementById('rules-modal');
    modal.style.display = 'block';
}

function closeModal() {
    var modal = document.getElementById('rules-modal');
    modal.style.display = 'none';
}

function resetGame() {
    socket.emit('reset');
}

socket.on('reset', function() {
    const cells = document.querySelectorAll('#board > div');
    cells.forEach(cell => {
        cell.innerText = '';
        cell.style.border = '1px solid #f0f0f0';
    });
    gameOver = false; // Сбрасываем состояние игры
    document.getElementById('messages').innerHTML = '';
});

function updatePlayerNames() {
    var player1Element = document.getElementById('player1');
    var player2Element = document.getElementById('player2');
    player1Element.textContent = player;
    player2Element.textContent = opponent;
}

function highlightCurrentPlayer() {
    var player1 = document.getElementById('player1');
    var player2 = document.getElementById('player2');

    if (turn === 'X') {
        player1.style.fontWeight = 'bold';
        player2.style.fontWeight = 'normal';
    } else {
        player1.style.fontWeight = 'normal';
        player2.style.fontWeight = 'bold';
    }
}