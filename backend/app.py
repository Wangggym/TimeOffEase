from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from os import environ

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # 修改为您自己的密钥
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def json(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}


class UserLeaveOvertime(db.Model):
    __tablename__ = 'user_leave_overtime'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='leave_overtime')
    name = db.Column(db.String(50), nullable=False)
    leave_or_overtime = db.Column(
        db.Enum('leave', 'overtime', name='leave_or_overtime_enum'), nullable=False)
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


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        name = data.get('name')
        password = data.get('password')
        email = data.get('email')

        if not name or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        hashed_password = bcrypt.generate_password_hash(
            password=password).decode('utf-8')
        new_user = User(name=name, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=new_user.id)

        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error registering user', 'error': str(e)}), 500)


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid username or password'}), 401

        access_token = create_access_token(identity=user.id)

        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error logging in', 'error': str(e)}), 500)


@app.route('/api/me', methods=['GET'])
@jwt_required()
def me():
    try:
        user_id = get_jwt_identity()
        user: User | None = User.query.get(user_id)
        if user is None:
            return jsonify({'message': 'User not found', 'error': 'user_id does not exist'}), 404
        return jsonify(user.json()), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error adding record', 'error': str(e)}), 500)


@app.route('/api/user_leave_overtime/add', methods=['POST'])
@jwt_required()
def insert_leave_overtime():
    try:
        data = request.json
        user_id = get_jwt_identity()

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
                data['start_time'], '%Y-%m-%dT%H:%M'),
            end_time=datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M'),
            leave_duration=data['leave_duration']
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify(new_record.json()), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error adding record', 'error': str(e)}), 500)


@app.route('/api/user_leave_overtime/delete/<int:id>', methods=['POST'])
@jwt_required()
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
@jwt_required()
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
                data.get('start_time', record.start_time), '%Y-%m-%dT%H:%M')
            record.end_time = datetime.strptime(
                data.get('end_time', record.end_time), '%Y-%m-%dT%H:%M')
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
@jwt_required()
def get_user_leave_overtime():
        user_id = get_jwt_identity()

        user: User | None = User.query.get(user_id)
        if user is None:
            return jsonify({'message': 'User not found', 'error': 'user_id does not exist'}), 404
        
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            leave_or_overtime_filter = request.args.get('leave_or_overtime', None)
            leave_or_overtime_type_filter = request.args.get(
                'leave_or_overtime_type', None)

            query = UserLeaveOvertime.query
            query = query.filter(UserLeaveOvertime.user.has(name=user.name))
            if leave_or_overtime_filter:
                query = query.filter(
                    UserLeaveOvertime.leave_or_overtime == leave_or_overtime_filter)
            if leave_or_overtime_type_filter:
                query = query.filter(
                    UserLeaveOvertime.leave_or_overtime_type == leave_or_overtime_type_filter)
                
            query = query.order_by(UserLeaveOvertime.id.desc())
            
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
