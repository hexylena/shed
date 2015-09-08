DEBUG = True
# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
GITHUB_SECRET = os.environ.get('GITHUB_SECRET') or 'Github Client Secret'
DATABASE_CONNECT_OPTIONS = {}
# Expire in two weeks (not great... will need to handle rotation of tickets at some point)
# https://github.com/sahat/satellizer/issues/58
JWT_EXPIRATION_DELTA = 3600 * 24 * 14
SECRET_KEY = "secret"
UPLOAD_PATH = 'uploads'
