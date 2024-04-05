from flask import request, session, render_template, send_from_directory, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from models import User, Persona, Data, Message
from config import base_dir, app, db, flashes
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
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
    form = UploadFileForm()
    return render_template('test.html', form=form)
    # return render_template('admin.html')


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
            flash('Invalid email or password', 'error')
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
            flash('User already exists!', 'warning')
            print('User already exists!')
            return redirect(url_for('register'))

        user = User(name=name, username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully', 'success')
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
        user = User.query.get(session['_user_id'])
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
                logout_user()
                return redirect(url_for('index'))
        else:
            flash("Error: User not found", 'error')

    return render_template('profile.html',
                           flashes=flashes,
                           fullname=session['name'],
                           email=session['email']
                           )


@app.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    files_list = Data.query.filter_by(user_id=session['_user_id']).all()

    form = UploadFileForm()
    if request.method == 'POST':
        if form.validate_on_submit():  # if new data source is added
            file = form.file.data
            if file and allowed_file(file.filename):
                file.save(os.path.join(base_dir, app.config['UPLOAD_FOLDER'],
                                       secure_filename(file.filename)))
                data = Data(
                    datatype=file.filename.rsplit('.', 1)[1].lower(),
                    filepath='/static/uploads/' +
                    secure_filename(file.filename),
                    user_id=session['_user_id']
                )
                db.session.add(data)
                db.session.commit()
                flash('File uploaded successfully',
                      'success')
                return redirect(url_for('data'))
            else:
                flash('Error: Invalid file type', 'error')

        elif 'delete-data' in request.form:  # if data row is deleted
            file_id = request.form.get('file_id')
            del_file = Data.query.get(file_id)
            if del_file:
                os.remove(del_file.filepath[1:])
                db.session.delete(del_file)
                db.session.commit()
                flash('File deleted successfully', 'success')
                return redirect(url_for('data'))
            else:
                flash('Error: File not found', 'error')

    return render_template('data.html', form=form, files=files_list)


@app.route('/personas', methods=['GET', 'POST'])
@login_required
def personas():
    persona_list = Persona.query.filter_by(user_id=session['_user_id']).all()

    if request.method == 'POST':
        if 'add-persona' in request.form:  # if new data source is added
            name = request.form.get('name')
            prompt = request.form.get('prompt')

            persona = Persona(name=name, prompt=prompt, user_id=session['_user_id'])
            db.session.add(persona)
            db.session.commit()

            flash('Persona created successfully', 'success')
            return redirect(url_for('personas'))
        
        elif 'delete-persona' in request.form:  # if data row is deleted
            persona_id = request.form.get('persona_id')
            del_persona = Persona.query.get(persona_id)
            if del_persona:
                db.session.delete(del_persona)
                db.session.commit()
                flash('Persona deleted successfully', 'success')
                return redirect(url_for('personas'))
            else:
                flash('Error: Persona not found', 'error')

    return render_template('personas.html', personas=persona_list)


@app.route('/chats')
def chats():
    return render_template('chats.html')


@app.route("/preline.js")
@login_required
def serve_preline_js():
    return send_from_directory("node_modules/preline/dist", "preline.js")


if __name__ == '__main__':
    app.run(debug=True)
