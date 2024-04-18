from flask import Blueprint, render_template
from .db import get_db

bp = Blueprint('blog', __name__, url_prefix="/blog")

bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT post.id, title, body, created, author_id, usernaem'
        'FROM post INNER JOIN user ON post.author_id = user.id'
        'ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index/html', posts=posts)


bp.route('/create', methods=("GET", "POST"))
def create():
    return render_template('blog/create.html')