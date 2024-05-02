from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from config import db


class User(UserMixin, db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)
    
    personas = db.relationship('Persona', backref='user', lazy='dynamic')
    data = db.relationship('Data', backref='user', lazy='dynamic')
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic')
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    def __repr__(self):
        return "<User %r>" % self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Persona(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    prompt = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'))
    added_on = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return "<Persona %r>" % self.name


class Data(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    datatype = db.Column(db.String(50), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    personas = db.relationship('Persona', backref='data', lazy='dynamic')

    def __repr__(self):
        return "<Data %r>" % self.filepath


class Conversation(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    persona_id = db.Column(db.Integer, db.ForeignKey('persona.id'), nullable=False)
    
    messages = db.relationship('Message', backref='conversation', lazy='dynamic')

    def __repr__(self):
        return "<Conversation %r>" % self._id


class Message(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    is_user = db.Column(db.Boolean, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)

    def __repr__(self):
        return "<Message %r>" % self._id


db.create_all()