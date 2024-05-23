
import json

from flask import render_template, request, redirect, url_for
from flask_socketio import SocketIO, send, emit, disconnect
from application import create_app, db
from models import User

app = create_app()
socketio = SocketIO(app)


@app.route('/')
def index():
    return redirect(url_for('register'))  # Перенаправление на страницу регистрации

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверяем, существует ли уже пользователь с таким именем
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Пользователь с таким именем уже существует!'

        # Создаем нового пользователя и добавляем его в базу данных
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # После успешной регистрации перенаправляем на страницу логина
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверяем, существует ли пользователь с такими данными в базе данных
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Если пользователь существует, перенаправляем на главную страницу
            return redirect(url_for('main'))
        else:
            # Если пользователь не найден, отображаем сообщение об ошибке
            error = 'Неправильное имя пользователя или пароль'

    return render_template('login.html')

@app.route('/main')
def main():
    return render_template('main.html', clients=clients)

def init_board():
    return [None, None, None, None, None, None, None, None, None]

def is_draw():
    global board
    for cell in board:
        if not cell:
            return False
    return True

def if_won():
    global board
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] is not None:
            winner = board[combo[0]]
            return winner, combo  # Return the winner and the winning combo
    return None, None

def init_game():
    global board
    global turn
    board = init_board()
    turn = 'X'  # Start with player X

init_game()

def update_board(data):
    global board
    global turn
    ind = int(data['cell'])
    data['init'] = False

    if data['player'] != turn:
        data['message'] = "It's not your turn"
        emit('message', data, room=request.sid)
        return

    if not board[ind]:
        board[ind] = data['player']
        turn = 'O' if turn == 'X' else 'X'  # Switch turns

        data['nextTurn'] = turn  # Add nextTurn to data

        # Broadcast the move to all clients only if it's the player's turn
        data['message'] = "move"
        send(data, broadcast=True)

        winner, winning_combo = if_won()
        if winner:
            for client in clients:
                if client['player'] == winner:
                    emit('message', {'cell': ind, 'player': data['player'], 'message': 'You won!', 'gameOver': True}, room=client['sid'])
                else:
                    emit('message', {'cell': ind, 'player': data['player'], 'message': 'You lost!', 'gameOver': True}, room=client['sid'])
            emit('winning_combo', {'combo': winning_combo}, broadcast=True)
            return
        if is_draw():
            send({'message': "It's a draw!", 'gameOver': True}, broadcast=True)
            return
    else:
        data['message'] = "Cell is already taken"
        emit('message', data, room=request.sid)

clients = []

@socketio.on('move')
def handle_move(json_data):
    data = json.loads(json_data)
    update_board(data)

@socketio.on('reset')
def handle_reset():
    global clients
    init_game()  # Сброс игры
    for client in clients:
        emit('reset', room=client['sid'])  # Отправляем событие сброса игры

@socketio.on('disconnect')
def handle_disconnect():
    global clients
    clients = [client for client in clients if client['sid'] != request.sid]
    if len(clients) < 2:
        init_game()  # Reset the game if a player leaves

@socketio.on('connect')
def handle_connect():
    global clients
    if len(clients) < 2:
        player = 'X' if not any(client['player'] == 'X' for client in clients) else 'O'
        clients.append({'sid': request.sid, 'player': player, 'username': None})
        emit('init', {'player': player})
    else:
        emit('message', {'message': 'Server is full'})
        disconnect()

if __name__ == '__main__':
    socketio.run(app, debug=True)
