from flask import request, session, render_template, send_from_directory, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from werkzeug.utils import secure_filename
from datetime import timedelta
import os
from agents import create_rag_agent, create_pandas_agent, create_base_agent
from models import User, Persona, Data, Conversation, Message
from config import UploadFileForm, base_dir, app, db, flashes
from admin import admin

app.register_blueprint(admin, url_prefix="/admin")
app.permanent_session_lifetime = timedelta(hours=1)



ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'xlsx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
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
        if 'add-user' in request.form:
            return redirect(url_for('admin.users'))
        else:
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        user = User.query.get(session['_user_id'])
        if user:
            if 'update-profile' in request.form:
                new_name = request.form.get('fullname')
                new_email = request.form.get('email')
                old_pass = request.form.get('old-password')
                new_pass = request.form.get('new-password')

                user.name = new_name
                user.email = new_email

                session['name'] = new_name
                session['email'] = new_email

                if user.check_password(old_pass) and new_pass:
                    user.set_password(new_pass)
                    return redirect(url_for('logout'))

                db.session.commit()
                flash('Profile updated successfully', 'success')
                return redirect(url_for('profile'))

            elif 'delete-profile' in request.form:
                db.session.delete(user)
                db.session.commit()
                logout_user()
                return redirect(url_for('index'))
        else:
            flash("Error: User not found", 'error')

    return render_template(
        'profile.html',
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
            assigned_user = request.form.get('assign-user-id')
            if file and allowed_file(file.filename):
                file.save(os.path.join(base_dir, app.config['UPLOAD_FOLDER'],
                                       secure_filename(file.filename)))
                
                data = Data(
                    datatype=file.filename.rsplit('.', 1)[1].lower(),
                    filepath=secure_filename(file.filename),
                    user_id=assigned_user if assigned_user else session['_user_id']
                )
                db.session.add(data)
                db.session.commit()
                flash('File uploaded successfully',
                      'success')
                if 'add-data' in request.form:
                    return redirect(url_for('admin.data'))
                else:
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
    # persona_list = Persona.query.filter_by(user_id=session['_user_id']).all()
    persona_list = current_user.personas.all()
    data_list = current_user.data.all()
    # data_list = Data.query.filter_by(user_id=session['_user_id']).all()

    if request.method == 'POST':
        if 'add-persona' in request.form:  # if new data source is added
            name = request.form.get('name')
            data = request.form.get('data')
            prompt = request.form.get('prompt')

            persona = Persona(name=name, data_id=data,
                              prompt=prompt, user_id=session['_user_id'])
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

    return render_template('personas.html', personas=persona_list, data_list=data_list)


@app.route('/chats', methods=['GET', 'POST'])
@login_required
def chats():
    # personas = Persona.query.filter_by(user_id=session['_user_id']).all()
    # conversations = Conversation.query.filter_by(user_id=session['_user_id']).all()
    personas = current_user.personas.all()
    conversations = current_user.conversations.all()

    if request.method == 'POST':
        if 'create-convo' in request.form:
            persona_id = request.form['persona']
            title = request.form['title']
            new_convo = Conversation(
                persona_id=persona_id, title=title, user_id=session['_user_id'])
            db.session.add(new_convo)
            db.session.commit()
            return redirect(url_for('chat', conv_id=new_convo._id))

        elif 'delete-convo' in request.form:
            conv_id = request.form.get('convo_id')
            del_convo = Conversation.query.get(conv_id)
            if del_convo:
                db.session.query(Message).filter_by(
                    conversation_id=conv_id).delete()
                db.session.delete(del_convo)
                db.session.commit()
                flash('Conversation deleted successfully', 'success')
                return redirect(url_for('chats'))
            else:
                flash('Error: Conversation not found', 'error')

    return render_template('chat_base.html', personas=personas, conversations=conversations)


@app.route('/chats/<int:conv_id>', methods=['GET', 'POST'])
@login_required
def chat(conv_id):
    personas = current_user.personas.all()
    conversations = current_user.conversations.all()
    conversation = Conversation.query.get(conv_id)
    persona_in_use = Persona.query.get(conversation.persona_id)
    data = None
    agent = None

    if persona_in_use is not None:
        if persona_in_use.data_id:
            data = Data.query.get(Persona.query.get(
                conversation.persona_id).data_id)
            if data.datatype in ["pdf", "txt"]:
                agent = create_rag_agent(
                    user_prompt=persona_in_use.prompt,
                    datatype=data.datatype,
                    filepath=data.filepath
                )
            elif data.datatype in ["csv", "pdf"]:
                agent = create_pandas_agent(
                    user_prompt=persona_in_use.prompt,
                    datatype=data.datatype,
                    filepath=data.filepath
                )
        else:
            agent = create_base_agent(persona_in_use.prompt)
    else:
        flash(
            'Error: The persona associated with this conversation does not exist.', 'error')
        db.session.query(Message).filter_by(conversation_id=conv_id).delete()
        db.session.delete(conversation)
        db.session.commit()
        return redirect(url_for('chats'))

    if request.method == 'POST':
        content = request.form.get('message')
        message = Message(is_user=True, content=content,
                          user_id=session['_user_id'], conversation_id=conv_id)
        db.session.add(message)

        resp = agent.invoke(
            {"input": content}, 
            {"configurable": {"session_id": "unused"}}
        )["output"]
        bot_msg = Message(is_user=False, content=resp,
                          user_id=session['_user_id'], conversation_id=conv_id)
        db.session.add(bot_msg)
        db.session.commit()

    messages = conversation.messages.order_by(Message.timestamp.asc()).all()
    return render_template('chats.html', personas=personas, persona_in_use=persona_in_use, data=data,
                           conversations=conversations, conversation=conversation,
                           messages=messages)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors.html', code=404, message='Page not found'), 404


@app.errorhandler(401)
def page_not_found(e):
    return render_template('errors.html', code=401, message='Unauthorised'), 401


@app.route("/preline.js")
@login_required
def serve_preline_js():
    return send_from_directory("node_modules/preline/dist", "preline.js")


if __name__ == '__main__':
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True)
