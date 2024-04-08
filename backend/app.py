from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def json(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}


class UserLeaveOvertime(db.Model):
    __tablename__ = 'user_leave_overtime'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='leave_overtime')
    name = db.Column(db.String(50), nullable=False)
    leave_or_overtime = db.Column(db.Enum('leave', 'overtime', name='leave_or_overtime_enum'), nullable=False)
    leave_or_overtime_type = db.Column(db.Enum('weekday_overtime', 'weekend_overtime', 'holiday_overtime',
                                           'personal_leave', 'sick_leave', 'marriage_leave', 'compensation_leave',
                                           name='leave_or_overtime_type_enum'), nullable=False)

    reason = db.Column(db.String(100))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    leave_duration = db.Column(db.Numeric(5, 2), nullable=False)
    additional_info = db.Column(db.String(255))

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'leave_or_overtime': self.leave_or_overtime,
            'leave_or_overtime_type': self.leave_or_overtime_type,
            'reason': self.reason,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'leave_duration': float(self.leave_duration),
            'additional_info': self.additional_info
        }


db.create_all()

# create a test route


@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'The server is running'})

# create a user


@app.route('/api/flask/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        new_user = User(name=data['name'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email
        }), 201

    except Exception as e:
        return make_response(jsonify({'message': 'error creating user', 'error': str(e)}), 500)

# get all users


@app.route('/api/flask/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        users_data = [{'id': user.id, 'name': user.name,
                       'email': user.email} for user in users]
        return jsonify(users_data), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error getting users', 'error': str(e)}), 500)

# get a user by id


@app.route('/api/flask/users/<id>', methods=['GET'])
def get_user(id):
    try:
        # get the first user with the id
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({'user': user.json()}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting user', 'error': str(e)}), 500)

# update a user by id


@app.route('/api/flask/users/<id>', methods=['POST'])
def update_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            user.name = data['name']
            user.email = data['email']
            db.session.commit()
            return make_response(jsonify({'message': 'user updated'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error updating user', 'error': str(e)}), 500)

# delete a user by id


@app.route('/api/flask/users/<id>', methods=['POST'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error deleting user', 'error': str(e)}), 500)


@app.route('/api/user_leave_overtime/add', methods=['POST'])
def insert_leave_overtime():
    try:
        data = request.json
        user_id = data.get('user_id')
        
        user = User.query.get(user_id)
        if user is None:
            return jsonify({'message': 'User not found', 'error': 'user_id does not exist'}), 404
        
        new_record = UserLeaveOvertime(
            user_id=user.id,
            name=user.name,
            leave_or_overtime=data['leave_or_overtime'],
            leave_or_overtime_type=data['leave_or_overtime_type'],
            reason=data['reason'],
            start_time=datetime.strptime(
                data['start_time'], '%Y-%m-%dT%H:%M:%S'),
            end_time=datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M:%S'),
            leave_duration=data['leave_duration']
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify(new_record.json()), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error adding record', 'error': str(e)}), 500)


@app.route('/api/user_leave_overtime/delete/<int:id>', methods=['POST'])
def delete_leave_overtime(id):
    try:
        record = UserLeaveOvertime.query.get(id)
        if record:
            db.session.delete(record)
            db.session.commit()
            return jsonify({'message': 'Record deleted successfully'}), 200
        else:
            return jsonify({'message': 'Record not found'}), 404
    except Exception as e:
        return make_response(jsonify({'message': 'error deleting record', 'error': str(e)}), 500)


@app.route('/api/user_leave_overtime/update/<int:id>', methods=['POST'])
def update_leave_overtime(id):
    try:
        data = request.json
        record = UserLeaveOvertime.query.get(id)
        if record:
            record.user_id = record.user_id
            record.name = record.name
            record.leave_or_overtime = data.get(
                'leave_or_overtime', record.leave_or_overtime)
            record.leave_or_overtime_type = data.get(
                'leave_or_overtime_type', record.leave_or_overtime_type)
            record.reason = data.get('reason', record.reason)
            record.start_time = datetime.strptime(
                data.get('start_time', record.start_time), '%Y-%m-%dT%H:%M:%S')
            record.end_time = datetime.strptime(
                data.get('end_time', record.end_time), '%Y-%m-%dT%H:%M:%S')
            record.leave_duration = data.get(
                'leave_duration', record.leave_duration)
            record.additional_info = data.get(
                'additional_info', record.additional_info)
            db.session.commit()
            return jsonify(record.json()), 200
        else:
            return jsonify({'message': 'Record not found'}), 404
    except Exception as e:
        return make_response(jsonify({'message': 'error updating record', 'error': str(e)}), 500)


@app.route('/api/user_leave_overtime/list', methods=['GET'])
def get_user_leave_overtime():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        name_filter = request.args.get('name', None)
        leave_or_overtime_filter = request.args.get('leave_or_overtime', None)
        leave_or_overtime_type_filter = request.args.get(
            'leave_or_overtime_type', None)

        query = UserLeaveOvertime.query
        if name_filter:
            query = query.filter(UserLeaveOvertime.user.has(name=name_filter))
        if leave_or_overtime_filter:
            query = query.filter(
                UserLeaveOvertime.leave_or_overtime == leave_or_overtime_filter)
        if leave_or_overtime_type_filter:
            query = query.filter(
                UserLeaveOvertime.leave_or_overtime_type == leave_or_overtime_type_filter)

        records = query.paginate(page, per_page, error_out=False)
        result = {
            'total': records.total,
            'pages': records.pages,
            'page': records.page,
            'per_page': records.per_page,
            'data': [record.json() for record in records.items]
        }
        return jsonify(result), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error getting records', 'error': str(e)}), 500)
