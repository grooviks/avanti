import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiError, getProduct, mediaUrl } from "@/lib/api";

import { ProductGallery } from "../product-gallery";

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
          <ProductGallery
            images={product.images.map((image) => ({
              id: image.id,
              url: mediaUrl(image.url),
              alt: image.alt ?? null,
            }))}
            productName={product.name}
          />
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
