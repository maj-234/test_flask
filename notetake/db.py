import sqlite3
import click

from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db
    
def close_db(e=None):
        db = g.pop("db", None)
        if db is not None:
             db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
         db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo("Initialized the database")
    d = get_db().execute("PRAGMA table_info(user)").fetchall()
    click.echo(f"table user column: {[name[1] for name in d]}")
    d = get_db().execute("PRAGMA table_info(post)").fetchall()
    click.echo(f"table post column: {[name[1] for name in d]}")

@click.command('get-post')
def get_post_command():
    posts = get_db().execute("SELECT * FROM post").fetchall()
    for post in posts:
        click.echo(str(post))

def init_app(app):
     app.teardown_appcontext(close_db)
     app.cli.add_command(init_db_command)
     app.cli.add_command(get_post_command)
