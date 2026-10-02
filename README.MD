# AvantiStyle

Русскоязычный каталог мебельного салона: категории и коллекции, карточки товаров
с фотогалереей, контакты и админка для управления каталогом и изображениями.
Корзины, заказов и оплаты нет.

Витрина и админка — Next.js 16 (App Router), React 19 и TypeScript.
API — FastAPI, Python 3.14, SQLAlchemy 2 и PostgreSQL 17; миграции — Alembic.
Админка использует JWT, пароли хешируются Argon2. Публичные страницы рендерятся
на сервере и получают каталог без кеширования: изменения из админки видны
при следующем запросе.

## Структура

```text
backend/              API, миграции PostgreSQL, тесты и служебные скрипты
frontend/             витрина, админка, SEO и прокси к API
deploy/               Dockerfile для API и web, скрипт деплоя, конфиги Nginx
compose.prod.yaml     production-сервисы API и web
docs/adr/             история архитектурных решений
```

Прежнее Flask-приложение удалено; его исходники доступны в истории Git.
Утилиты импорта старого каталога сохранены в `backend/scripts/`.

## Локальный запуск

Нужны Python 3.14, uv, Node.js 22, npm и Docker с Compose для PostgreSQL.
Команды каждого раздела выполняются от корня репозитория, если не указано иное.

### API и база данных

```sh
cd backend
cp -n .env.example .env
uv sync --frozen
docker compose up -d --wait
uv run alembic upgrade head
uv run uvicorn avanti.main:app --reload --host 127.0.0.1 --port 8000
```

Перед запуском задайте собственный `AVANTI_SECRET_KEY` в `backend/.env`.
Локальный Compose публикует PostgreSQL на порту **5433**, как в `.env.example`.
API читает `backend/.env`, если запущен из `backend/`.

- Проверка API: <http://localhost:8000/health>.
- Swagger UI: <http://localhost:8000/docs>.
- OpenAPI: <http://localhost:8000/openapi.json>.

### Администратор

Укажите `AVANTI_ADMIN_EMAIL` и `AVANTI_ADMIN_PASSWORD` в `backend/.env`, затем
в отдельном терминале выполните:

```sh
cd backend
uv run --env-file .env python scripts/create_admin.py
```

Явный `--env-file` нужен для переменных скрипта. Повторный запуск обновляет
пароль существующего пользователя и выдаёт ему права администратора.
Каталог можно заполнить через админку. Для одноразовой демонстрационной базы
есть `scripts/seed.py`: он **удаляет текущий каталог** перед заполнением.

### Витрина и админка

В отдельном терминале:

```sh
cd frontend
cp -n .env.example .env.local
npm ci
npm run dev
```

В `frontend/.env.local` задаются `AVANTI_API_URL=http://localhost:8000` и,
для локальных SEO-ссылок, `AVANTI_SITE_URL=http://localhost:3000`.

- Витрина: <http://localhost:3000>.
- Вход в админку: <http://localhost:3000/admin>.
- Товары: `/admin/products`, категории: `/admin/categories`.

Браузерные запросы админки идут через `/api/backend/*` на сервер Next.js,
который обращается к API по `AVANTI_API_URL`.
Новые изображения сохраняются в `backend/media/`; импортированные изображения
могут ссылаться на внешнее S3-хранилище.

## Проверки

```sh
cd backend
uv run ruff check .
```

Тесты используют реальный PostgreSQL и очищают таблицы каталога. Запускайте
их только на отдельной тестовой БД. Например, с работающим локальным Compose
создайте базу `avanti_test` (один раз) и запустите проверки из `backend/`:

```sh
docker compose exec postgres createdb -U avanti avanti_test
export AVANTI_DATABASE_URL=postgresql+asyncpg://avanti:password@localhost:5433/avanti_test
uv run alembic upgrade head
uv run pytest
unset AVANTI_DATABASE_URL
```

Проверка frontend из корня репозитория:

```sh
cd frontend
npm run build
```

Типы API находятся в `frontend/src/lib/openapi.d.ts`. После изменения схем
обновите их при запущенном API из `frontend/` и повторите сборку:

```sh
npx openapi-typescript http://localhost:8000/openapi.json -o src/lib/openapi.d.ts
```

## Выпуск и production

GitHub Actions проверяет backend (ruff, миграции, pytest) и сборку frontend
для PR в `master` и коммитов в `master`. После успешных проверок push в
`master` публикует образы `avanti-api` и `avanti-web` в Yandex Container Registry
с тегами SHA коммита и `latest`; ручной запуск workflow тоже публикует образы.

Production работает на одной ВМ: API и web — в Docker Compose, PostgreSQL
и Nginx — на хосте. Nginx завершает TLS и проксирует web на `127.0.0.1:3001`;
API доступен внутри Compose-сети. Загруженные изображения хранятся в volume
`avanti_media`, который нужно включить в резервное копирование.

Для выпуска используется `deploy.sh <commit-sha>` с SHA собранного образа.
Скрипт применяет миграции, запускает сервисы и проверяет доступность web.
Откат приложения — повторный деплой предыдущего SHA; откат БД планируется отдельно.

- [Настройка ВМ, секретов, CI и деплоя](deploy/README.md).
- [Nginx, DNS и TLS](deploy/nginx/README.md).
- [Импорт архивного каталога MySQL и изображений](backend/scripts/README.md).
- [Исходное архитектурное решение](docs/adr/0001-rewrite-architecture.md).

В production задайте `AVANTI_SITE_URL=https://avantistyle.ru` для sitemap,
robots и канонических ссылок. Секреты подключения и JWT передаются API через
файлы Docker secrets; их размещение описано в инструкции деплоя.
