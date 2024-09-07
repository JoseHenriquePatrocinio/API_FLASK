from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
from models import db, User

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db.init_app(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [user.to_dict() for user in users]
    return jsonify(users_list), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'message': 'Invalid input'}), 400

    new_user = User(name=data['name'], email=data['email'])

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

    return jsonify(new_user.to_dict()), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'message': 'Invalid input'}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404

    user.name = data['name']
    user.email = data['email']

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

    return jsonify(user.to_dict()), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

    return jsonify({'message': 'User deleted successfully'}), 200

def create_initial_data():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            users = [
                User(name='Alice', email='alice@example.com'),
                User(name='Bob', email='bob@example.com'),
                User(name='Charlie', email='charlie@example.com')
            ]
            db.session.bulk_save_objects(users)
            db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        create_initial_data()
    app.run(debug=True)