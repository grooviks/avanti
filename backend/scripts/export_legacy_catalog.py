"""Снимок старого MySQL-каталога и перенос его фотографий в S3.

Запускается на старой ВМ. Секреты не передаются аргументами: URL MySQL берётся
из ``AVANTI_LEGACY_DATABASE_URL``, а доступ к S3 — из стандартного профиля AWS
CLI. Результат: архивный ``legacy-mysql.sql.gz``, ``catalog.json`` и S3-объекты
с неизменными именами ``<prefix>/{categories,products}/<legacy filename>``.
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pymysql>=1.1.2",
# ]
# ///

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, unquote, urlsplit

import pymysql

LEGACY_TABLES = ("categories", "products", "category_images", "product_images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Экспорт старого каталога Avanti")
    parser.add_argument("--images-root", type=Path, required=True, help="старая app/static/images")
    parser.add_argument("--output-dir", type=Path, required=True, help="папка результата")
    parser.add_argument("--s3-bucket", required=True)
    parser.add_argument("--s3-prefix", required=True, help="например avanti-legacy/2026-09-12")
    parser.add_argument("--s3-endpoint-url", required=True, help="S3 endpoint YC")
    parser.add_argument("--upload", action="store_true", help="фактически загрузить в S3")
    return parser.parse_args()


def load_legacy_rows(database_url: str) -> dict[str, list[Mapping[str, Any]]]:
    """Read legacy MySQL directly, without SQLAlchemy/greenlet dependencies."""
    parsed = urlsplit(database_url)
    if parsed.scheme not in {"mysql", "mysql+pymysql"}:
        raise SystemExit("AVANTI_LEGACY_DATABASE_URL должен начинаться с mysql+pymysql://")
    if not parsed.hostname or not parsed.username or not parsed.path.strip("/"):
        raise SystemExit("В AVANTI_LEGACY_DATABASE_URL укажите хост, пользователя и имя базы")
    query = parse_qs(parsed.query)
    connection = pymysql.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=unquote(parsed.username),
        password=unquote(parsed.password or ""),
        database=unquote(parsed.path.lstrip("/")),
        charset=query.get("charset", ["utf8mb4"])[0],
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            result: dict[str, list[Mapping[str, Any]]] = {}
            for table_name in LEGACY_TABLES:
                cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY `id`")
                result[table_name] = list(cursor.fetchall())
            return result
    finally:
        connection.close()


def validate_image_source(
    rows: dict[str, list[Mapping[str, Any]]], images_root: Path
) -> list[Path]:
    missing: list[Path] = []
    for table_name, scope in (("category_images", "categories"), ("product_images", "products")):
        for row in rows[table_name]:
            filename = row.get("filename")
            path = images_root / scope / str(filename)
            if not filename or not path.is_file():
                missing.append(path)
    return missing


def write_snapshot(output_dir: Path, rows: dict[str, list[dict[str, Any]]], prefix: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = output_dir / "catalog.json"
    snapshot.write_text(
        json.dumps(
            {
                "format": "avanti-legacy-catalog-v1",
                "created_at": datetime.now(UTC).isoformat(),
                "s3_prefix": prefix.strip("/"),
                "tables": rows,
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    return snapshot


def upload_images(images_root: Path, bucket: str, prefix: str, endpoint_url: str) -> None:
    for scope in ("categories", "products"):
        subprocess.run(
            [
                "aws",
                "s3",
                "sync",
                str(images_root / scope),
                f"s3://{bucket}/{prefix.strip('/')}/{scope}",
                "--endpoint-url",
                endpoint_url,
                "--only-show-errors",
            ],
            check=True,
        )


def main() -> None:
    args = parse_args()
    database_url = os.environ.get("AVANTI_LEGACY_DATABASE_URL")
    if not database_url:
        raise SystemExit("Задайте AVANTI_LEGACY_DATABASE_URL в окружении старой ВМ")
    rows = load_legacy_rows(database_url)
    missing = validate_image_source(rows, args.images_root)
    image_count = len(rows["category_images"]) + len(rows["product_images"])
    if missing:
        preview = "\n".join(f"  - {path}" for path in missing[:20])
        remainder = "" if len(missing) <= 20 else f"\n  … ещё {len(missing) - 20}"
        raise SystemExit(
            f"Не найдены {len(missing)} из {image_count} файлов; экспорт отменён:\n"
            f"{preview}{remainder}"
        )
    snapshot = write_snapshot(args.output_dir, rows, args.s3_prefix)
    print(f"Snapshot: {snapshot}")
    print(f"Catalog: {len(rows['categories'])} categories, {len(rows['products'])} products")
    print(f"Images: {image_count}")
    if not args.upload:
        print("Dry-run complete. Re-run with --upload after checking the snapshot.")
        return
    upload_images(args.images_root, args.s3_bucket, args.s3_prefix, args.s3_endpoint_url)
    print("S3 upload complete. Copy catalog.json to the new VM and run migrate_legacy_catalog.py.")


if __name__ == "__main__":
    main()
