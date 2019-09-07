#EDACY
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from school import app, db, bcrypt, mail
from school.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm, ClasseForm, StudentForm)
from school.models import User, Post, Student, Classe
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

#Le route de la page d'acceuil ou tous les articles sont postés par soit le blogger ou l'admin(Diarra fall)
@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

#le route ou il ya tout ce qui a un lien avec le lycée
@app.route("/about")
def about():
    return render_template('about.html', title='About')

#Permet à un utilisateur de s'inscire dans le systeme mais cet option n'est pas encore disponible surement dans une prochaine version
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ton compte a été créé! Vous pouvez maintenant vous connecter', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#Permet aux deux utilisateurs(pour l'instant le blogger et Diarra fall) de se connecter 
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Vos informations sont erronéese . Veuillez mettre votre mot de passe et adresse email', 'danger')
    return render_template('login.html', title='Login', form=form)

#Permet à un utilisateur de se deconnecter
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

#enregistrer une photo de profil
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

#Permet à l'utilisateur (deja connecté) d'acceder aux details de son compte
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

#Permet à l'utilisateur (deja connecté) de mettre un article dans la page d'acceuil
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Votre poste a été créé avec succés!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')

#Permet à l'utilisateur (deja connecté) de visionner un article en single
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

#Permet à l'utilisateur (deja connecté et createur de l'article) de modifier l'article posté
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Votre poste a été mis à jour avec succés!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

#Permet à l'utilisateur (deja connecté et createur de l'article) de supprimer l'article posté
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Votre poste a été supprimé!', 'success')
    return redirect(url_for('home'))

#Permet à l'utilisateur (deja connecté) de visionner les articles postées par un utilisateur bien donné
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

#Permet de faire une demande de changement de mot de passe
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Un email a été senvoyé avec des instructions pour changer votre mot de passe .', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

#Modifier le mot de passe apres demande
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Ce lien est expiré ou invalide', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Votre mot de passe a été mis à jour avec succés! Vous pouvez maintenant vous connecter', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


                        #Seul l'admin peut acceder à ces fonctions

#afficher toutes les classes ajoutées pour l'admin
@app.route("/all_classe")
@login_required
def all_classe():
    page = request.args.get('page', 1, type=int)
    classes = Classe.query.paginate(page=page, per_page=5)
    return render_template('all_classe.html', classes=classes)

#Creer une nouvelle classe
@app.route('/classe/new', methods=['GET', 'POST'])
@login_required
def create_classe():
    form = ClasseForm()
    if form.validate_on_submit():
        classe = Classe(nom_classe=form.nom_classe.data, serie=form.serie.data)
        db.session.add(classe)
        db.session.commit()
        flash('La classe   a été créé avec succés!', 'success')
        return redirect(url_for('all_classe'))
    return render_template('create_classe.html', title='New classe',
                            form=form, legend='Enregistrer Une Classe')

#Afficher une classe en single 
@app.route("/classe/<int:classe_id>")
def classe(classe_id):
    classe = Classe.query.get_or_404(classe_id)
    return render_template('classe.html', title=classe.nom_classe, classe=classe)

#Modifier les attributs de la classe
@app.route("/classe/<int:classe_id>/update", methods=['GET', 'POST'])
@login_required
def update_classe(classe_id):
    classe = Classe.query.get_or_404(classe_id)
    if current_user.username != 'Diarra fall':
        abort(403)
    form = ClasseForm()
    if form.validate_on_submit():
        classe.nom_classe = form.nom_classe.data
        classe.serie = form.serie.data
        db.session.commit()
        flash('Votre classe a été mis à jour avec succés!', 'success')
        return redirect(url_for('classe', classe_id=classe.id))
    elif request.method == 'GET':
        form.nom_classe.data = classe.nom_classe
        form.serie.data = classe.serie
    return render_template('create_classe.html', title='Update classe',
                           form=form, legend='Update classe')

                #Supprimer une classe
@app.route("/classe/<int:classe_id>/delete", methods=['POST'])
@login_required
def delete_classe(classe_id):
    classe = Classe.query.get_or_404(classe_id)
    if current_user.username != 'Diarra fall':
        abort(403)
    db.session.delete(classe)
    db.session.commit()
    flash('la classe a été supprimé!', 'success')
    return redirect(url_for('all_classe'))



                #Ajouter un eleve dans une classe
@app.route('/classe/<int:classe_id>/student/new', methods=['GET', 'POST'])
@login_required
def create_student(classe_id):
    form = StudentForm()
    if form.validate_on_submit():
        classe = Classe.query.get_or_404(classe_id)
        student = Student(Prenom=form.Prenom.data, Nom=form.Nom.data, Date_Naissance=form.Date_Naissance.data, classezer=classe)
        db.session.add(student)
        db.session.commit()
        flash('Vous avez ajouter un nouvel eleve dans cette classe!', 'success')
        return redirect(url_for('classe_students', nom_classe=classe.nom_classe))
    return render_template('create_student.html', title='New student',
                            form=form, legend='Enregistrer Un nouvel éléve')

                #Afficher un eleve en single
@app.route("/classe/student/<int:student_id>")
def student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student.html', title=student.Prenom, student=student)

                #Mettre à jour les infos d'un eleve
@app.route("/classe/student/<int:student_id>/update", methods=['GET', 'POST'])
@login_required
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    if current_user.username != 'Diarra fall':
        abort(403)
    form = StudentForm()
    if form.validate_on_submit():
        student.Prenom = form.Prenom.data
        student.Nom = form.Nom.data
        student.Date_Naissance = form.Date_Naissance.data
        db.session.commit()
        flash('Les infos de cet eleve ont été mis à jour avec succés!', 'success')
        return redirect(url_for('student', student_id=student.id))
    elif request.method == 'GET':
        form.Prenom.data = student.Prenom
        form.Nom.data = student.Nom
        form.Date_Naissance.data = Date_Naissance.Nom
    return render_template('create_student.html', title='Update Student',
                           form=form, legend="Mettre à jour les infos de l'eleve")

                #Supprimer une eleve
@app.route("/classe/student/<int:student_id>/delete", methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    if current_user.username != 'Diarra fall':
        abort(403)
    db.session.delete(student)
    db.session.commit()
    flash('Cet eleve a été supprimé!', 'success')
    return redirect(url_for('classe_students'))

                #Affiche tous les eleves d'une classe donnée
@app.route("/classe/<string:nom_classe>")
def classe_students(nom_classe):
    page = request.args.get('page', 1, type=int)
    classe = Classe.query.filter_by(nom_classe=nom_classe).first_or_404()
    students = Student.query.filter_by(classezer=classe).paginate(page=page, per_page=5)
    return render_template('classe_students.html', students=students, classe=classe)