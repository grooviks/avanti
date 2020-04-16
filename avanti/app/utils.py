import os
from PIL import Image
from avanti.config import ALLOWED_EXTENSIONS
from werkzeug import secure_filename
import bcrypt


def allowed_file(filename):
    '''проверка имени и расширения файла'''
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_image(path,file,name):
    '''загрузка изображения'''
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(path,filename)
        file.save(filepath)
        #конвертируем изображение
        im = Image.open(filepath)
        #и сохраняем с нужным именеем
        filepath = os.path.join(path,name +'.jpeg')
        im.save(filepath)
        os.remove(os.path.join(path,filename))
        return True
    return False


def delete_image(path):
    ''' удаление файла '''
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def encrypt(password, salt=None):
    ''' хэширование пароля для сохранения в базе '''
    return bcrypt.hashpw(password.encode('utf-8'), salt if salt else bcrypt.gensalt())


def decrypt(password, hashed):
    ''' сравнение хэшей двух паролей '''
    if bcrypt.hashpw(password.encode('utf-8'), hashed.encode('utf-8')) == hashed.encode('utf-8'):
        return True
    else:
        return False
