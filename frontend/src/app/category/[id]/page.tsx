import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import {
  ApiError,
  type CategoryTree,
  getCategories,
  getCategory,
  getCategoryProducts,
  mediaUrl,
} from "@/lib/api";

export const revalidate = 60;

type PageProps = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  try {
    const category = await getCategory((await params).id);
    return { title: `${category.name} — Avantistyle`, description: category.description ?? "Мебель Avantistyle" };
  } catch {
    return { title: "Категория — Avantistyle" };
  }
}

export default async function CategoryPage({ params }: PageProps) {
  const { id } = await params;
  try {
    const [category, products, categoryTree] = await Promise.all([
      getCategory(id),
      getCategoryProducts(id),
      getCategories(),
    ]);
    const children = findCategory(categoryTree, Number(id))?.children ?? [];
    return (
      <div className="page-shell">
        <Link className="back-link" href="/">← Все категории</Link>
        <section className="intro compact">
          <p className="eyebrow">Категория</p>
          <h1>{category.name}</h1>
          {category.description && <p>{category.description}</p>}
        </section>
        {children.length > 0 && (
          <section className="subcategories" aria-label={`Разделы категории ${category.name}`}>
            <p className="eyebrow">Выберите раздел</p>
            <h2>Подкатегории</h2>
            <div className="category-grid">
              {children.map((child) => (
                <Link className="category-card" href={`/category/${child.id}`} key={child.id}>
                  {child.images[0] ? (
                    <img alt={child.images[0].alt ?? child.name} src={mediaUrl(child.images[0].url)} />
                  ) : (
                    <div className="image-placeholder" aria-hidden="true" />
                  )}
                  <div>
                    <h2>{child.name}</h2>
                    <p>{child.description ?? `${child.children.length} разделов`}</p>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}
        {products.length ? (
          <section className="product-grid" aria-label={`Товары категории ${category.name}`}>
            {products.map((product) => (
              <Link className="product-card" href={`/product/${product.id}`} key={product.id}>
                {product.images[0] ? (
                  <img alt={product.images[0].alt ?? product.name} src={mediaUrl(product.images[0].url)} />
                ) : (
                  <div className="image-placeholder" aria-hidden="true" />
                )}
                <div><h2>{product.name}</h2><p>{formatPrice(product.price)}</p></div>
              </Link>
            ))}
          </section>
        ) : children.length === 0 && <p className="notice">В этой категории пока нет товаров.</p>}
      </div>
    );
  } catch (error) {
    if (error instanceof ApiError && error.message.includes("404")) notFound();
    throw error;
  }
}

function findCategory(categories: CategoryTree[], id: number): CategoryTree | undefined {
  for (const category of categories) {
    if (category.id === id) return category;
    const found = findCategory(category.children, id);
    if (found) return found;
  }
  return undefined;
}

function formatPrice(price: string): string {
  return new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(Number(price));
}
