from flask import Flask, make_response
from . import auth, db
import os

def create_app(test_config=None):
    
    app = Flask(__name__ , instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'notetake.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
        print("instance directory created")
    except OSError:
        print("instance directory existed")

    @app.route('/')
    def index():
        res = make_response("index")
        res.status_code = 200
        return res

    @app.route('/a')
    def a():
        res = make_response("a page")
        res.status_code = 200
        return res
    
    db.init_app(app)
    app.register_blueprint(auth.bp)
    
    return app