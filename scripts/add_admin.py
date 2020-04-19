import bcrypt
import random
import string
import subprocess

DB_NAME='avanti'
DB_USER='avanti'
DB_PASS='password'

login = 'admin'
size = random.randint(8, 12)

chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
password = ''.join(random.choice(chars) for x in range(size))

print(f'admin login: {login}')
print(f'admin password: {password}')
hash = (bcrypt.hashpw(password.encode("utf-8"), salt=bcrypt.gensalt())).decode("utf-8")

# экранируем сиволы для bash
hash = ("").join(list(map(lambda h: h if (h != '$') else '\\'+h, hash)))

print(hash)
cmd = f'mysql -u {DB_USER} -p{DB_PASS} -D {DB_NAME} -e "INSERT INTO {DB_NAME}.users (username, email, password, role, status) VALUES (\'{login}\', \'{login}@avantistyle.ru\', \'{hash}\', 0, 2);"'

print(cmd)

returned_value = subprocess.call(cmd, shell=True)

print(f'User {login} created!') if not returned_value else print(f'Error create!')


