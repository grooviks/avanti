import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiError, getProduct, mediaUrl } from "@/lib/api";

export const revalidate = 60;

type PageProps = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  try {
    const product = await getProduct((await params).id);
    return { title: `${product.name} — Avantistyle`, description: product.description ?? product.name };
  } catch {
    return { title: "Товар — Avantistyle" };
  }
}

export default async function ProductPage({ params }: PageProps) {
  try {
    const product = await getProduct((await params).id);
    return (
      <div className="page-shell product-page">
        <Link className="back-link" href={`/category/${product.category_id}`}>← К категории</Link>
        <div className="product-layout">
          <section className="gallery" aria-label={`Фотографии: ${product.name}`}>
            {product.images.length ? <>
              <figure className="gallery-main">
                <img alt={product.images[0].alt ?? product.name} src={mediaUrl(product.images[0].url)} />
                <figcaption>{product.images.length} {product.images.length === 1 ? "фото" : "фото в галерее"}</figcaption>
              </figure>
              {product.images.length > 1 && <div className="gallery-secondary">{product.images.slice(1).map((image) => (
                <img alt={image.alt ?? product.name} key={image.id} src={mediaUrl(image.url)} />
              ))}</div>}
            </> : <div className="image-placeholder large" aria-hidden="true" />}
          </section>
          <section className="product-details">
            <p className="eyebrow">Avantistyle · мебель для дома</p>
            <h1>{product.name}</h1>
            <div className="purchase-card">
              <p className="price">{formatPrice(product.price)}</p>
            </div>
            <ProductDescription text={product.description ?? "Описание появится совсем скоро."} />
            <div className="product-benefits"><span>Подбор материалов в салоне</span><span>Помощь с проектом и замером</span><a className="product-action" href="tel:+74955210093">Уточнить наличие <span>→</span></a></div>
            {product.sku && <p className="sku">Артикул: {product.sku}</p>}
          </section>
        </div>
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

function ProductDescription({ text }: { text: string }) {
  const paragraphs = text.split(/\n\s*\n/).filter(Boolean);

  return (
    <div className="product-description">
      {paragraphs.map((paragraph, index) => <p key={index}>{paragraph.trim()}</p>)}
    </div>
  );
}
