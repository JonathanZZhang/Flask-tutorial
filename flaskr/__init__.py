import os

from flask import Flask

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config=True) # create an instance
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config == None:
        app.config.from_pyfile('config.py', silent=True) # silent failure
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    @app.route('/')
    def hello():
        return 'Hello, World'
    
    return app