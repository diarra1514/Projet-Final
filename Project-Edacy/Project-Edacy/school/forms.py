#EDACY
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from school.models import User, Post, Student, Classe 

#Formualaire pour s'inscrire sur le systeme
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom dutilisateur est déja choisi . Choisissez en un autre.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet adresse email est déja choisi . Choisissez en un autre.')

#Formulaire de connexion
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Se Souvenir de moi')
    submit = SubmitField('Se connecter')

#Formulaire de mis à jour  des infos de son compte
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Mettre ) jour')
    
    #Fonction de validation du nom d'utilisateur entré
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ce nom dutilsateur a été déja choisi . Veuillez en choisir un autre!.')
    
    #Fonction de validation de l'email entré
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cet adresse email a été déja choisi . Veuillez en choisir un autre!.')

#Formulaire pour créer un article
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

#Formulaire de demande de changement de mot de passe
class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Demande de changement de mot de passe')

    #Fonction de validation de l'email entré
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Cet adresse email nexiste pas dans le systeme')

#Formualaire de changement de mot de passe
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Changer de mot de passe')

#Formulaire pour ajouter une classe 
class ClasseForm(FlaskForm):
    nom_classe = StringField('nom_classe', validators=[DataRequired()])
    serie = StringField('serie', validators=[DataRequired()])
    submit = SubmitField('Créer la classe')

#Formulaire pour ajouter un eleve dans classe 
class StudentForm(FlaskForm):
    Prenom = StringField('Prenom', validators=[DataRequired()])
    Nom = StringField('Nom', validators=[DataRequired()])
    Date_Naissance = StringField('Date_Naissance', validators=[DataRequired()])
    submit = SubmitField('Enregistrer un nouvel éléve')

