# Перенос старого каталога

Перенос идёт в два независимых шага. SQL-дамп MySQL нужен как резервная копия;
для импорта в PostgreSQL используется JSON-снимок, потому что MySQL SQL нельзя
безопасно выполнить в PostgreSQL напрямую.

## На старой ВМ

Нужны `mysqldump`, AWS CLI и настроенный S3-совместимый профиль с правом записи
в выделенный бакет. Пароль MySQL держите в файле `MYSQL_DEFAULTS_FILE` с правами
`600`, а URL подключения для Python задайте через `AVANTI_LEGACY_DATABASE_URL`.

```bash
cd /path/to/avanti/backend
export MYSQL_DEFAULTS_FILE=/root/.my.cnf
export LEGACY_MYSQL_DATABASE=avanti
export EXPORT_DIR=/var/backups/avanti-2026-09-12
./scripts/export_legacy_mysql.sh

export AVANTI_LEGACY_DATABASE_URL='mysql+pymysql://…'
# Экспортёр автономный: на старой CentOS не нужно выполнять `uv sync` всего
# backend (он попытался бы собрать greenlet). uv скачает Python 3.12 и только
# два необходимых чистых Python-пакета из метаданных скрипта.
uv run --no-project --python 3.12 scripts/export_legacy_catalog.py \
  --images-root /path/to/avanti/app/static/images \
  --output-dir "$EXPORT_DIR" \
  --s3-bucket avanti-media \
  --s3-prefix legacy/2026-09-12 \
  --s3-endpoint-url https://storage.yandexcloud.net
```

Последняя команда — dry-run: проверяет все записи БД и наличие каждого
связанного файла. Если всё в порядке, повторите ту же команду с `--upload`. Не меняйте
префикс между экспортом и импортом: имена файлов и порядок фотографий сохранятся.

Если старый сайт уже содержит ссылки на удалённые файлы, dry-run выведет их и
остановится. После проверки повторите команду с `--skip-missing-images`: товары
и категории сохранятся, а только битые ссылки на фото не попадут в снимок.

Скопируйте на новую ВМ как минимум `catalog.json` и SQL-архив. Перед переносом
сверьте количество объектов в `s3://avanti-media/legacy/2026-09-12/` с числом,
которое вывел экспортёр.

## На новой ВМ

После `alembic upgrade head` и только в пустой базе:

```bash
python scripts/migrate_legacy_catalog.py \
  --legacy-snapshot /secure-transfer/catalog.json \
  --s3-public-base-url https://storage.yandexcloud.net/avanti-media \
  --s3-prefix legacy/2026-09-12

python scripts/migrate_legacy_catalog.py \
  --legacy-snapshot /secure-transfer/catalog.json \
  --s3-public-base-url https://storage.yandexcloud.net/avanti-media \
  --s3-prefix legacy/2026-09-12 \
  --apply
```

Первая команда ничего не меняет. Вторая переносит категории, товары и ссылки на
S3; `basic_image` старого товара всегда получает позицию `0` и остаётся обложкой.
Скрипт останавливается, если новая БД не пуста.
