from application import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<User %r>' % self.username
