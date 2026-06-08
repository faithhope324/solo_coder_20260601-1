import random
import string
from sqlalchemy.exc import IntegrityError
from models import db, Room, Vote


def generate_room_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Room.query.filter_by(code=code).first():
            return code


def create_room(title, options, host_session=None):
    code = generate_room_code()
    room = Room(code=code, title=title, options=options, host_session=host_session)
    db.session.add(room)
    db.session.commit()
    return room


def get_room(code):
    return Room.query.filter_by(code=code).first()


def end_room(code):
    room = get_room(code)
    if room:
        room.is_active = False
        db.session.commit()
    return room


def has_voted(room_id, voter_ip, voter_session):
    return Vote.query.filter(
        (Vote.room_id == room_id) &
        ((Vote.voter_ip == voter_ip) | (Vote.voter_session == voter_session))
    ).first() is not None


def add_vote(room_id, option, voter_ip, voter_session):
    if has_voted(room_id, voter_ip, voter_session):
        return None
    vote = Vote(room_id=room_id, option=option, voter_ip=voter_ip, voter_session=voter_session)
    db.session.add(vote)
    try:
        db.session.commit()
        return vote
    except IntegrityError:
        db.session.rollback()
        return None


def get_vote_results(room_id):
    room = Room.query.get(room_id)
    if not room:
        return {}
    options = room.get_options_list()
    results = {opt: 0 for opt in options}
    votes = Vote.query.filter_by(room_id=room_id).all()
    for vote in votes:
        if vote.option in results:
            results[vote.option] += 1
    return results


def get_vote_count(room_id):
    return Vote.query.filter_by(room_id=room_id).count()


def get_host_rooms(host_session):
    if not host_session:
        return []
    return Room.query.filter_by(host_session=host_session).order_by(Room.created_at.desc()).all()
