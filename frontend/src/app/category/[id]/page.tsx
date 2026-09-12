import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiError, getCategory, getCategoryProducts, mediaUrl } from "@/lib/api";

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
    const [category, products] = await Promise.all([getCategory(id), getCategoryProducts(id)]);
    return (
      <div className="page-shell">
        <Link className="back-link" href="/">← Все категории</Link>
        <section className="intro compact">
          <p className="eyebrow">Категория</p>
          <h1>{category.name}</h1>
          {category.description && <p>{category.description}</p>}
        </section>
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
        ) : <p className="notice">В этой категории пока нет товаров.</p>}
      </div>
    );
  } catch (error) {
    if (error instanceof ApiError && error.message.includes("404")) notFound();
    throw error;
  }
}

function formatPrice(price: string): string {
  return new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(Number(price));
}
