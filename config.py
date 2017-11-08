import os
from flaskext.mysql import MySQL
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
# Случайный ключ, которые будет исползоваться для подписи
# данных, например cookies.
SECRET_KEY = 'YOUR_RANDOM_SECRET_KEY'

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
#должен быть настроен mysql и быть база equipment
SQLALCHEMY_DATABASE_URI = 'mysql://fo_store:fo_store@localhost:3306/fo_store' 
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#парамерты для загрузки изображений
UPLOAD_FOLDER_IMG = os.path.join(basedir,'app/static/images')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'bmp', 'JPG', 'JPEG', 'BMP', 'PNG'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

#директория для загрузки файлов
UPLOAD_FOLDER_FILES = os.path.join(basedir,'app/static/files')

