import functools

from werkzeug.security import generate_password_hash, check_password_hash
from flask import g, flash, redirect, Blueprint, request, url_for, render_template, session

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form['username']
        passwd = request.form['password']
        db = get_db()
        error = None
        if not username:
            error = 'not an available username'
        elif not passwd:
            error = 'not an available password'

        if error == None:
            try:
                db.execute(
                    "INSERTE INTO user (username, password) VALUE (?, ?)",
                    (username, generate_password_hash(passwd))
                )
            except db.IntegrityError:
                error = f'user {username} is already existed'
            else:
                return redirect(url_for('auth.login'))
        flash(error)

    return render_template('auth/register.html') 


@bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form['username']
        passwd = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            "SELECT * FROM user WHERE username=?", (username,)
        ).fetchone()

        if user is None:
            error = 'user not exist'
        elif not check_password_hash(user['password'], passwd):
            error = 'incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session['user_id']

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?",
            (user_id,)
        ).fetchone()


def login_required(view):
    @functools.warps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        else:
            return view(**kwargs)
    return wrapped_view