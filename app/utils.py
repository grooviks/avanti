import os
from PIL import Image
from config import ALLOWED_EXTENSIONS
from werkzeug import secure_filename


def allowed_file(filename):
    '''проверка имени и расширения файла'''
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_image(path,file,name):
    '''загрузка изображения, возвращает путь к файлу'''
    print(name)
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