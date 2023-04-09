import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads
import logging
from flask_cors import CORS
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin


UPLOAD_FOLDER = os.path.abspath(os.curdir) + '/flaskblog/static/post_photo'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type', 'X-Access-Token'
app.config['SECRET_KEY'] = '146a29001879f0796b123f600c1b85c3'

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://market:marketPass7766@localhost/market"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

logging.basicConfig(filename='error.log',level=logging.DEBUG)
logging.basicConfig(filename='server.log',level=logging.INFO)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
db = SQLAlchemy(app)
migrate = Migrate(app, db) 
bcrypt = Bcrypt(app)
CORS(app, resources={r"/*": {"origins": "*"}})
login_manager = LoginManager(app)
images = UploadSet('images', IMAGES)


from flaskblog import routes
