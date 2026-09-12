"""Тесты преобразования данных старого каталога без подключения к MySQL."""

from avanti.legacy_migration import prepare_categories, prepare_products, slugify


def test_slugify_transliterates_cyrillic_and_has_fallback() -> None:
    assert slugify("Диван «Осло»", "fallback") == "divan-oslo"
    assert slugify("!!!", "product-7") == "product-7"


def test_prepare_catalog_preserves_ids_and_repairs_missing_data() -> None:
    categories = prepare_categories(
        [
            {"id": 2, "name": "Диваны", "parent_id": 1},
            {"id": 1, "name": "Диваны", "parent_id": None},
        ]
    )
    assert [(item.id, item.slug) for item in categories] == [(1, "divany"), (2, "divany-2")]

    products, skipped = prepare_products(
        [
            {"id": 10, "name": "Осло", "category_id": 2, "price": "12.5", "is_avail": 1},
            {"id": 11, "name": "Без категории", "category_id": 999},
        ],
        {item.id for item in categories},
    )
    assert skipped == [11]
    assert products[0].id == 10
    assert products[0].slug == "oslo"
    assert str(products[0].price) == "12.50"
    assert products[0].sku == "LEGACY-10"
