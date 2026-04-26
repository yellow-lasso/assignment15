from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    trades = db.relationship("Trade", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    representative = db.Column(db.String(100), nullable=False)
    trade_date = db.Column(db.String(20), nullable=False)
    disclosure_date = db.Column(db.String(20), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    amount_min = db.Column(db.String(20), nullable=False)
    amount_max = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(200), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)