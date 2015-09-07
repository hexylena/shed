DEBUG = True
# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
GITHUB_SECRET = os.environ.get('GITHUB_SECRET') or 'Github Client Secret'
DATABASE_CONNECT_OPTIONS = {}
SECRET_KEY = "secret"
