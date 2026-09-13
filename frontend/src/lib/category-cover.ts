import { mediaUrl, type CatalogImage } from "./api";

type CategoryWithImages = {
  name: string;
  images: CatalogImage[];
};

const generatedCovers: Record<string, string> = {
  Комоды: "/catalog-covers/komody.jpg",
  Столы: "/catalog-covers/stoly.jpg",
  "Шкаф-купе": "/catalog-covers/shkaf-kupe.jpg",
  "Шкафы детские": "/catalog-covers/shkafy-detskie.jpg",
};

export function categoryCover(category: CategoryWithImages): { src: string; alt: string } | null {
  const image = category.images[0];
  if (image) return { src: mediaUrl(image.url), alt: image.alt ?? category.name };

  const generated = generatedCovers[category.name];
  return generated ? { src: generated, alt: category.name } : null;
}
