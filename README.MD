Онлайн каталог мебели
===========
Небольшое приложение на flask которое можно переиспользовать, заменив шаблоны.
Есть админка, можно добавлять категории товаров, товары, описание, фото, пользователей.
По сути простой интернет магазин. Код местами не очень хороший, так как писался несколько лет назад.

Установка на CentOS
------------
Устанавливаем зависимости:
```
cd avanti
. bin/activate
pip3 install -r requipments/base.txt
```

Переходим в MySQL

```mysql -u root -p ```

Создаем БД
```
CREATE DATABASE avanti;
CREATE USER 'avanti'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON fo_store.* TO 'avanti'@'localhost';
FLUSH PRIVILEGES;
```
Накатываем миграцию
```
./manager.py db upgrade
```

Создать учетку admin
```
TODO
```

Добавить переменные окружения
```
export DB_PASS=<пароль_БД>
export DB_ADMIN=<логин_БД>
export DB_NAME=<имя_БД>
```

Запуск
```
python3 avanti/manager.py gunicorn
```
