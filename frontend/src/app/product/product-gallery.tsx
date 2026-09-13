"use client";

import { useState } from "react";

type GalleryImage = {
  id: number;
  url: string;
  alt: string | null;
};

export function ProductGallery({ images, productName }: { images: GalleryImage[]; productName: string }) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const selected = images[selectedIndex];

  if (!selected) return <div className="image-placeholder large" aria-hidden="true" />;

  function selectNext(direction: -1 | 1) {
    setSelectedIndex((index) => (index + direction + images.length) % images.length);
  }

  return (
    <section className="gallery" aria-label={`Фотографии: ${productName}`}>
      <figure className="gallery-main">
        <img alt={selected.alt ?? productName} src={selected.url} />
        <figcaption>{selectedIndex + 1} из {images.length}</figcaption>
        {images.length > 1 && (
          <div className="gallery-controls">
            <button aria-label="Предыдущее фото" onClick={() => selectNext(-1)} type="button">←</button>
            <button aria-label="Следующее фото" onClick={() => selectNext(1)} type="button">→</button>
          </div>
        )}
      </figure>
      {images.length > 1 && (
        <div className="gallery-secondary" aria-label="Выбрать фотографию">
          {images.map((image, index) => (
            <button
              aria-label={`Показать фото ${index + 1}`}
              aria-pressed={index === selectedIndex}
              className={index === selectedIndex ? "is-selected" : undefined}
              key={image.id}
              onClick={() => setSelectedIndex(index)}
              type="button"
            >
              <img alt={image.alt ?? productName} src={image.url} />
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
