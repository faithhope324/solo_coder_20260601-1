import os
import uuid
from flask import Flask, render_template, request, jsonify, session, url_for, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db
from room_manager import (
    create_room, get_room, end_room, add_vote,
    has_voted, get_vote_results, get_vote_count
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vote-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'voting.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

room_connections = {}


def init_db():
    with app.app_context():
        db.create_all()


def get_or_create_session_id():
    if 'voter_id' not in session:
        session['voter_id'] = str(uuid.uuid4())
    return session['voter_id']


def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'unknown'


@app.route('/')
def index():
    return redirect(url_for('create_page'))


@app.route('/create', methods=['GET', 'POST'])
def create_page():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        options = request.form.get('options', '').strip()
        if not title or not options:
            return render_template('create.html', error='请填写标题和选项')
        options_list = [opt.strip() for opt in options.split(',') if opt.strip()]
        if len(options_list) < 2:
            return render_template('create.html', error='至少需要 2 个选项')
        room = create_room(title, options)
        return redirect(url_for('host_page', code=room.code))
    return render_template('create.html')


@app.route('/host/<code>')
def host_page(code):
    room = get_room(code)
    if not room:
        return '房间不存在', 404
    return render_template('host.html', room=room)


@app.route('/join/<code>')
def join_page(code):
    room = get_room(code)
    if not room:
        return '房间不存在', 404
    voter_id = get_or_create_session_id()
    voter_ip = get_client_ip()
    already_voted = has_voted(room.id, voter_ip, voter_id)
    return render_template('join.html', room=room, already_voted=already_voted)


@app.route('/api/room/<code>')
def api_room(code):
    room = get_room(code)
    if not room:
        return jsonify({'error': '房间不存在'}), 404
    data = room.to_dict()
    data['results'] = get_vote_results(room.id)
    data['total_votes'] = get_vote_count(room.id)
    return jsonify(data)


@socketio.on('join')
def on_join(data):
    code = data.get('code')
    room = get_room(code)
    if not room:
        emit('error', {'message': '房间不存在'})
        return
    join_room(code)
    if code not in room_connections:
        room_connections[code] = 0
    room_connections[code] += 1
    emit('room_joined', {
        'room': room.to_dict(),
        'results': get_vote_results(room.id),
        'total_votes': get_vote_count(room.id),
        'online_count': room_connections[code]
    }, to=request.sid)
    emit('user_count', {'online_count': room_connections[code]}, to=code)


@socketio.on('vote')
def on_vote(data):
    code = data.get('code')
    option = data.get('option')
    room = get_room(code)
    if not room:
        emit('vote_error', {'message': '房间不存在'})
        return
    if not room.is_active:
        emit('vote_error', {'message': '投票已结束'})
        return
    voter_id = get_or_create_session_id()
    voter_ip = get_client_ip()
    if has_voted(room.id, voter_ip, voter_id):
        emit('vote_error', {'message': '您已经投过票了'})
        return
    if option not in room.get_options_list():
        emit('vote_error', {'message': '无效的选项'})
        return
    vote = add_vote(room.id, option, voter_ip, voter_id)
    if not vote:
        emit('vote_error', {'message': '投票失败'})
        return
    results = get_vote_results(room.id)
    total = get_vote_count(room.id)
    emit('vote_success', {
        'option': option,
        'results': results,
        'total_votes': total
    }, to=request.sid)
    emit('results_updated', {
        'results': results,
        'total_votes': total
    }, to=code)


@socketio.on('end_vote')
def on_end_vote(data):
    code = data.get('code')
    room = get_room(code)
    if not room:
        emit('error', {'message': '房间不存在'})
        return
    room = end_room(code)
    results = get_vote_results(room.id)
    total = get_vote_count(room.id)
    emit('vote_ended', {
        'results': results,
        'total_votes': total
    }, to=code)


@socketio.on('disconnect')
def on_disconnect():
    for code in list(room_connections.keys()):
        if room_connections[code] > 0:
            room_connections[code] -= 1
            emit('user_count', {'online_count': room_connections[code]}, to=code)
            if room_connections[code] <= 0:
                del room_connections[code]


if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
