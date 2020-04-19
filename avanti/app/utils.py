import bcrypt
import logging
import os

from PIL import Image
from avanti.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER_IMG
from werkzeug import secure_filename


_logger_ = logging.getLogger('default')


def allowed_file(filename):
    """проверка имени и расширения файла"""
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_image(path, file, name):
    """загрузка изображения"""
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(path, filename)
        file.save(filepath)
        # конвертируем изображение
        im = Image.open(filepath)
        # и сохраняем с нужным именеем
        filepath = os.path.join(path, name + '.jpeg')
        im.save(filepath)
        os.remove(os.path.join(path, filename))
        return True
    return False


def delete_image(path):
    """  удаление файла """
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def encrypt(password, salt=None):
    """  хэширование пароля для сохранения в базе """
    return bcrypt.hashpw(password.encode('utf-8'), salt if salt else bcrypt.gensalt())


def decrypt(password, hashed):
    """ сравнение хэшей двух паролей """
    if bcrypt.hashpw(password.encode('utf-8'), hashed.encode('utf-8')) == hashed.encode('utf-8'):
        return True
    else:
        return False


def checks_directories():
    """ создание директорий для хранения изображений """
    directories = ['categories', 'products']

    for dir in directories:
        full_path = os.path.join(UPLOAD_FOLDER_IMG, dir)
        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
            except OSError as e:
                _logger_.error(f'Cannot create directory {full_path}! {e}')
