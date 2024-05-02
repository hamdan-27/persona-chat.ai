from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import User, Persona, Data
from config import UploadFileForm, db, base_dir, app
import os

admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates/admin')

@admin.route('/')
@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        users = User.query.filter_by(is_admin=False).all()
        personas = Persona.query.all()
        data = Data.query.all()
        return render_template(
            'dashboard.html', users=users[:5], user_count=len(users),
            persona_count=len(personas), data_count=len(data))
    else:
        abort(401)


@admin.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.is_admin:
        if request.method == 'POST':
            id = request.form.get('id')
            user = User.query.get(id)
            if user:
                if 'update-user' in request.form:
                    name = request.form.get('name')
                    email = request.form.get('email')
                    username = request.form.get('username')
                    oldpass = request.form.get('old-password')
                    newpass = request.form.get('new-password')
                
                    user.name = name
                    user.email = email
                    user.username = username

                    if oldpass and newpass:
                        if user.check_password(oldpass):
                            user.set_password(newpass)
                        else:
                            flash('Invalid current password entered', 'error')
                            return redirect(url_for('admin.users'))
                    
                    db.session.commit()
                    flash(f'User {user.id} updated successfully', 'success')
                    return redirect(url_for('admin.users'))
                
                elif 'delete-user' in request.form:
                    db.session.delete(user)
                    db.session.commit()
                    flash(f'User {user.id} deleted successfully', 'success')
                    return redirect(url_for('admin.users'))
                
            else:
                flash('User not found', 'error')
                return redirect(url_for('admin.users'))
                
        users = User.query.filter_by(is_admin=False).all()
        return render_template('users.html', users=users, count=len(users))
    else:
        abort(401)


@admin.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    if current_user.is_admin:
        form = UploadFileForm()
        form.submit.name = 'add-data'

        if request.method == 'POST':
            id = request.form.get('id')
            data = Data.query.get(id)
            if data:
                if 'update-data' in request.form:
                    filename = request.form.get('filepath')
                    new_filepath = secure_filename(filename + '.' + data.datatype)
                    os.rename(
                        os.path.join(base_dir, app.config['UPLOAD_FOLDER'], data.filepath),
                        os.path.join(base_dir, app.config['UPLOAD_FOLDER'], new_filepath)
                    )
                    data.filepath = new_filepath
                    db.session.commit()
                    flash(f'Data {data._id} updated successfully', 'success')
                    return redirect(url_for('admin.data'))
                elif 'delete-data' in request.form:
                    db.session.delete(data)
                    os.remove(os.path.join(base_dir, app.config['UPLOAD_FOLDER'], data.filepath))
                    db.session.commit()
                    flash(f'Data {data._id} deleted successfully', 'success')
                    return redirect(url_for('admin.data'))
                
        all_data = Data.query.all()
        users = User.query.filter_by(is_admin=False).all()
        return render_template('admin_data.html', files=all_data, count=len(all_data), form=form, users=users)
    else:
        abort(401)



@admin.route('/personas', methods=['GET', 'POST'])
@login_required
def personas():
    if current_user.is_admin:
        return render_template('admin_personas.html')
    else:
        abort(401)


@admin.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if current_user.is_admin:
        return render_template('account.html')
    else:
        abort(401)
