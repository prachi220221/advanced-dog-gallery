from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()


def create_app():
    app = Flask(__name__)

    # Configure MySQL
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Prachi@0221'
    app.config['MYSQL_DB'] = 'dog_gallery'

    mysql.init_app(app)

    # Register blueprint
    from .view import main
    app.register_blueprint(main)

    return app




