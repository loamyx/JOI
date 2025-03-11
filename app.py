from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import bcrypt
from models import db, User, Meditation, Achievement, Streak, Friendship, LeaderboardEntry
from sqlalchemy import desc, func, and_
import random
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///joi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        email=data['email'],
        password=hashed_password,
        username=data['username']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# Daily meditation routes
@app.route('/api/meditation/daily', methods=['GET'])
def get_daily_meditation():
    prompts = [
        "Focus on your breath for 5 minutes. Notice the rise and fall of your chest.",
        "Scan your body from head to toe, releasing tension in each part.",
        "Practice loving-kindness meditation by sending good wishes to yourself and others.",
        "Observe your thoughts like clouds passing in the sky, without judgment.",
        "Count your breaths from 1 to 10, then start over."
    ]
    return jsonify({
        'instruction': random.choice(prompts),
        'duration': 300  # 5 minutes in seconds
    })

@app.route('/api/meditation/complete', methods=['POST'])
def complete_meditation():
    data = request.json
    user_id = get_user_from_token(request.headers.get('Authorization'))
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    duration = data.get('duration')
    if not duration:
        return jsonify({'error': 'Duration is required'}), 400

    meditation = Meditation(
        user_id=user_id,
        duration=duration,
        completed_at=datetime.utcnow()
    )
    db.session.add(meditation)

    user = User.query.get(user_id)
    user.total_meditation_minutes += duration // 60
    
    # Update streak
    update_streak(user_id)
    check_achievements(user_id)

    # Update leaderboard entry
    entry = LeaderboardEntry.query.filter_by(user_id=user_id).first()
    if not entry:
        entry = LeaderboardEntry(user_id=user_id)
        db.session.add(entry)

    entry.streak_count = user.current_streak
    entry.total_minutes = user.total_meditation_minutes

    # Update ranks for all users
    rank_subquery = db.session.query(
        LeaderboardEntry.id,
        func.row_number().over(
            order_by=(desc(LeaderboardEntry.streak_count), desc(LeaderboardEntry.total_minutes))
        ).label('rank')
    ).subquery()

    db.session.query(LeaderboardEntry).update(
        {LeaderboardEntry.rank: rank_subquery.c.rank},
        synchronize_session=False
    )
    
    db.session.commit()
    return jsonify({'message': 'Meditation recorded successfully'})

def get_user_from_token(auth_header):
    if not auth_header:
        return None
    try:
        token = auth_header.split(' ')[1]
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return data['user_id']
    except:
        return None

def update_streak(user_id):
    from streak_manager import StreakManager
    streak_count, achievement_earned = StreakManager.calculate_streak(user_id)
    return {'streak': streak_count, 'achievement_earned': achievement_earned}

def check_achievements(user_id):
    user = User.query.get(user_id)
    meditation_count = Meditation.query.filter_by(user_id=user_id).count()
    
    achievements = [
        (1, "First Step", "Complete your first meditation"),
        (7, "Week Warrior", "Complete 7 meditations"),
        (30, "Monthly Master", "Complete 30 meditations"),
        (100, "Zen Master", "Complete 100 meditations")
    ]
    
    for count, title, description in achievements:
        if meditation_count >= count and not Achievement.query.filter_by(user_id=user_id, title=title).first():
            new_achievement = Achievement(user_id=user_id, title=title, description=description)
            db.session.add(new_achievement)

# Social features routes
@app.route('/api/friends', methods=['GET'])
def get_friends():
    user_id = get_user_from_token(request.headers.get('Authorization'))
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        friends = user.friends.all()
        pending_requests = Friendship.query.filter(
            Friendship.friend_id == user_id,
            Friendship.status == 'pending'
        ).join(User, User.id == Friendship.user_id).all()
        
        return jsonify({
            'friends': [{
                'id': friend.id,
                'username': friend.username,
                'currentStreak': friend.current_streak,
                'totalMinutes': friend.total_meditation_minutes
            } for friend in friends],
            'pendingRequests': [{
                'id': fr.user_id,
                'username': fr.user.username,
                'requestId': fr.id
            } for fr in pending_requests]
        })
    except Exception as e:
        app.logger.error(f'Error in get_friends: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/friends/request', methods=['POST'])
def send_friend_request():
    user_id = get_user_from_token(request.headers.get('Authorization'))
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        friend_id = request.json.get('friendId')
        if not friend_id:
            return jsonify({'error': 'Friend ID is required'}), 400
            
        if friend_id == user_id:
            return jsonify({'error': 'Cannot send friend request to yourself'}), 400

        # Check if target user exists
        friend = User.query.get(friend_id)
        if not friend:
            return jsonify({'error': 'User not found'}), 404
            
        existing = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                and_(Friendship.friend_id == user_id, Friendship.user_id == friend_id)
            )
        ).first()
        
        if existing:
            if existing.status == 'pending':
                return jsonify({'error': 'Friend request already pending'}), 400
            elif existing.status == 'accepted':
                return jsonify({'error': 'Already friends'}), 400
            
        friendship = Friendship(user_id=user_id, friend_id=friend_id)
        db.session.add(friendship)
        db.session.commit()
        
        return jsonify({'message': 'Friend request sent successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error in send_friend_request: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/friends/respond', methods=['POST'])
def respond_to_friend_request():
    user_id = get_user_from_token(request.headers.get('Authorization'))
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        request_id = request.json.get('requestId')
        accept = request.json.get('accept', False)
        
        if not request_id:
            return jsonify({'error': 'Request ID is required'}), 400
            
        friendship = Friendship.query.filter_by(id=request_id, friend_id=user_id, status='pending').first()
        if not friendship:
            return jsonify({'error': 'Friend request not found or already processed'}), 404
            
        if accept:
            friendship.status = 'accepted'
            friendship.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({
                'message': 'Friend request accepted',
                'friend': {
                    'id': friendship.user_id,
                    'username': User.query.get(friendship.user_id).username
                }
            })
        else:
            db.session.delete(friendship)
            db.session.commit()
            return jsonify({'message': 'Friend request rejected'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error in respond_to_friend_request: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    user_id = get_user_from_token(request.headers.get('Authorization'))
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Get top 10 users
        leaderboard = LeaderboardEntry.query.join(User).order_by(
            desc(LeaderboardEntry.streak_count),
            desc(LeaderboardEntry.total_minutes)
        ).limit(10).all()

        # Get current user's rank
        user_entry = LeaderboardEntry.query.filter_by(user_id=user_id).first()
        user_rank = None
        if user_entry:
            user_rank = db.session.query(func.count()).filter(
                or_(
                    and_(LeaderboardEntry.streak_count > user_entry.streak_count),
                    and_(LeaderboardEntry.streak_count == user_entry.streak_count,
                         LeaderboardEntry.total_minutes > user_entry.total_minutes)
                )
            ).scalar() + 1
        
        return jsonify({
            'leaderboard': [{
                'rank': entry.rank,
                'username': entry.user.username,
                'streakCount': entry.streak_count,
                'totalMinutes': entry.total_minutes,
                'isCurrentUser': entry.user_id == user_id
            } for entry in leaderboard],
            'userRank': user_rank
        })
    except Exception as e:
        app.logger.error(f'Error in get_leaderboard: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/search/users', methods=['GET'])
def search_users():
    user_id = get_user_from_token(request.headers.get('Authorization'))
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        query = request.args.get('q', '')
        if len(query) < 3:
            return jsonify({'users': []})
            
        # Get users matching search query
        users = User.query.filter(
            User.username.ilike(f'%{query}%'),
            User.id != user_id
        ).limit(10).all()

        # Get existing friendship statuses
        friendships = {}
        if users:
            existing = Friendship.query.filter(
                or_(
                    and_(Friendship.user_id == user_id, Friendship.friend_id.in_([u.id for u in users])),
                    and_(Friendship.friend_id == user_id, Friendship.user_id.in_([u.id for u in users]))
                )
            ).all()
            
            for f in existing:
                if f.user_id == user_id:
                    friendships[f.friend_id] = f.status
                else:
                    friendships[f.user_id] = 'incoming' if f.status == 'pending' else f.status
        
        return jsonify({
            'users': [{
                'id': user.id,
                'username': user.username,
                'currentStreak': user.current_streak,
                'friendshipStatus': friendships.get(user.id)
            } for user in users]
        })
    except Exception as e:
        app.logger.error(f'Error in search_users: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
