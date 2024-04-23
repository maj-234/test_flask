from flask import Blueprint, render_template, request, flash, g, redirect, abort
from .db import get_db
from .auth import login_required
bp = Blueprint('blog', __name__, url_prefix="/blog")

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT post.id, title, body, created, author_id, username FROM post INNER JOIN user ON post.author_id = user.id ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = 'title is required'
        if not g.user['id']:
            error = 'login required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id ) VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect('/blog')

    return render_template('blog/create.html')

def get_post(id):
    db = get_db()
    post = db.execute(
        f"SELECT title, body, author_id, created, username, post.id FROM post INNER JOIN user ON post.author_id = user.id WHERE post.id=?",
        (id,)
    ).fetchone()
    if post == None:
        return abort(404)
    if post['author_id'] != g.user['id']:
        return abort(403)
    return post

@bp.route('/<int:id>/update', methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None
        if title is None:
            error = "missing title"
        if error is None:
            db = get_db()
            db.execute(
                "UPDATE post SET title=?, body=? WHERE id=?",
                (title, body, id)
            )
            db.commit()
            return redirect('/blog')
        else:
            flash(error)
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=("POST", ))
def delete(id):
    db = get_db()
    db.execute(
        "DELETE FROM post WHERE id=?",
        (id,)
    )
    db.commit()
    return redirect('/blog')