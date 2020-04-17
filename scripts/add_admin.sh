DB_NAME='avanti'
DB_USER='avanti'
DB_PASS='dthbabrfwbz2'

admin_password=`LC_ALL=C tr -dc 'A-Za-z0-9!"#$%&' </dev/urandom | head -c 13`
# $2b$12$A5UujFPQPR2INJygzBHxjewY215AjW4EUKTXGCEMWiVeTAQHTYIRG
# aVyCJQVAVBWxg
echo $admin_password
mysql -u $DB_USER -p$DB_PASS -D $DB_NAME -e 'INSERT INTO avanti.users VALUES(100,'Andrey','Sales',5000);'
