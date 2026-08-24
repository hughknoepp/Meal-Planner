from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date as date_type

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class MealLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=date_type.today, nullable=False)
    items = db.Relationship('MealItem', backref='meal_log', cascade='all, delete-orphan')

class MealItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_log_id = db.Column(db.Integer, db.ForeignKey('meal_log.id'), nullable=False)
    food_name = db.Column(db.String(200), nullable=False)
    fdc_id = db.Column(db.Integer, nullable=False)
    quantity_g = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float)
    protein_g = db.Column(db.Float)
    carbs_g = db.Column(db.Float)
    fat_g = db.Column(db.Float)