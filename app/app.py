from flask import request, session, render_template, send_from_directory, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from models import User, Persona, Data, Message
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from config import app, db, flashes
from flask_wtf import FlaskForm
import os


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'xslx', 'tsv'}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/test', methods=['GET', 'POST'])
def test():
    # Test code here
    return render_template('admin.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            session['name'] = user.name
            session['email'] = user.email
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password', category=flashes.get('error'))
            print("Invalid email or password")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        exist_user = User.query.filter_by(email=email).first()
        if exist_user:
            flash('User already exists!', category=flashes.get('warning'))
            print('User already exists!')
            return redirect(url_for('register'))

        user = User(name=name, username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully', category=flashes.get('success'))
        print('User registered successfully')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        if user:
            if 'update-profile' in request.form:
                new_name = request.form.get('fullname')
                new_email = request.form.get('email')
                new_pass = request.form.get('password')

                user.name = new_name
                user.email = new_email
                user.set_password(new_pass)

                db.session.commit()

            elif 'delete-profile' in request.form:
                db.session.delete(user)
                db.session.commit()
                return redirect(url_for('index'))
        else:
            flash("Error: User not found", category=flashes.get('error'))

    return render_template('profile.html', 
        flashes=flashes, 
        fullname=session['name'], 
        email=session['email']
    )


@app.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                      app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            data = Data(
                datatype=file.filename.rsplit('.', 1)[1].lower(),
                filepath='/static/uploads/' + secure_filename(file.filename),
                user_id=session['_user_id']
            )
            db.session.add(data)
            db.session.commit()
            flash('File uploaded successfully', category=flashes.get('success'))
    return render_template('data.html', form=form)


@app.route('/personas')
@login_required
def personas():
    return render_template('personas.html')


@app.route('/chats')
def chats():
    return render_template('chats.html')


@app.route("/preline.js")
@login_required
def serve_preline_js():
    return send_from_directory("node_modules/preline/dist", "preline.js")


if __name__ == '__main__':
    app.run(debug=True)
