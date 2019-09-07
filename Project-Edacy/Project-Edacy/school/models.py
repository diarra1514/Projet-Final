#EDACY
#Fichier de gestion de la base de donnees (donnees à y mettre)
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from school import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#La table de l'utilisateur
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

#La table d'un article
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

#La table d'une classe
class Classe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_classe = db.Column(db.String(100), nullable=False)
    serie = db.Column(db.String(100), nullable=False)
    students = db.relationship('Student', backref='classezer', lazy=True)

    def __repr__(self):
        return f"Classe('{self.nom_classe}', '{self.serie}' )"

#La table d'un eleve
class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Prenom = db.Column(db.String(20), unique=False, nullable=False)
    Nom = db.Column(db.String(20), unique=False, nullable=False)
    Date_Naissance = db.Column(db.String(100), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)

    def __repr__(self):
        return f"Student('{self.Prenom}', '{self.Nom}', '{self.Date_Naissance}')"
    


