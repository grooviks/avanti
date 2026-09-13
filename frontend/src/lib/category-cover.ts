import { mediaUrl, type CatalogImage } from "./api";

type CategoryWithImages = {
  name: string;
  images: CatalogImage[];
};

const generatedCovers: Record<string, string> = {
  "Столы журнальные, подставки, газетницы": "/catalog-covers/coffee-tables.jpg",
  "Столы обеденные": "/catalog-covers/dining-tables.jpg",
  "Стулья и табуреты": "/catalog-covers/chairs-stools.jpg",
  "Мягкая мебель": "/catalog-covers/upholstered-furniture.jpg",
  "Кресла для дома и офиса": "/catalog-covers/home-office-chairs.jpg",
  "Банкетки и пуфики": "/catalog-covers/benches-ottomans.jpg",
  "Вешалки и зеркала": "/catalog-covers/coat-racks-mirrors.jpg",
  "Мебель для гостиной": "/catalog-covers/living-room-furniture.jpg",
  "Офисная мебель": "/catalog-covers/office-furniture.jpg",
  Комоды: "/catalog-covers/komody.jpg",
  Столы: "/catalog-covers/stoly.jpg",
  "Шкаф-купе": "/catalog-covers/shkaf-kupe.jpg",
  "Шкафы детские": "/catalog-covers/shkafy-detskie.jpg",
};

export function categoryCover(category: CategoryWithImages): { src: string; alt: string } | null {
  const generated = generatedCovers[category.name];
  if (generated) return { src: generated, alt: category.name };

  const image = category.images[0];
  return image ? { src: mediaUrl(image.url), alt: image.alt ?? category.name } : null;
}
