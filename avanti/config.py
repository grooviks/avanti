import binascii
import os

from avanti.app.config import parse_config

CONFIG = parse_config()

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
# Случайный ключ, которые будет исползоваться для подписи
# данных, например cookies.
SECRET_KEY = binascii.hexlify(os.urandom(24))

# должен быть настроен mysql и быть база
SQLALCHEMY_DATABASE_URI = CONFIG['db_url']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# парамерты для загрузки изображений
UPLOAD_FOLDER_IMG = os.path.join(basedir, 'app/static/images')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'bmp', 'JPG', 'JPEG', 'BMP', 'PNG'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# директория для загрузки файлов
UPLOAD_FOLDER_FILES = os.path.join(basedir, 'app/static/files')
