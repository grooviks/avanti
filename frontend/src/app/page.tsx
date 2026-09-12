import Link from "next/link";

import { ApiError, getCategories, mediaUrl } from "@/lib/api";

export const revalidate = 60;

export default async function HomePage() {
  try {
    const categories = await getCategories();

    return (
      <div className="page-shell">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Мебель для вашего дома</p>
            <h1>Ваша мечта<br />становится реальностью.</h1>
            <p>Коллекции для интерьера, в котором удобно жить, встречать гостей и быть собой.</p>
            <a className="hero-action" href="#catalog">Смотреть каталог <span>→</span></a>
          </div>
          <div className="hero-media" aria-label="Уютный интерьер Avantistyle">
            <img className="hero-sofa" src="/sofa-interior.png" alt="Светлый диван в уютной гостиной" />
            <img className="hero-lamp" src="/lamp-interior.png" alt="Торшер и кресло в тёплом интерьере" />
            <span className="hero-note">От классики<br />до модерна</span>
          </div>
        </section>
        <section className="catalog-heading" id="catalog">
          <div><p className="eyebrow">Выберите своё</p><h2>Коллекции мебели</h2></div>
          <p>Проверенные фабрики, продуманные решения и индивидуальный подход.</p>
        </section>
        {categories.length ? (
          <section className="category-grid" aria-label="Категории каталога">
            {categories.map((category) => (
              <Link className="category-card" href={`/category/${category.id}`} key={category.id}>
                {category.images[0] ? (
                  <img alt={category.images[0].alt ?? category.name} src={mediaUrl(category.images[0].url)} />
                ) : (
                  <div className="image-placeholder" aria-hidden="true" />
                )}
                <div>
                  <h2>{category.name}</h2>
                  <p>{category.description ?? `${category.children.length} разделов`}</p>
                </div>
              </Link>
            ))}
          </section>
        ) : (
          <div className="notice"><h2>Каталог наполняется</h2><p>Позвоните нам — подберём мебель и расскажем о доступных коллекциях.</p><a href="tel:+74955210093">Позвонить в салон</a></div>
        )}
        <section className="visit-links">
          <div className="visit-intro"><p className="eyebrow">Выбирайте не спеша</p><h2>Мебель лучше увидеть вживую</h2><p>Приезжайте в салон: покажем материалы, поможем с выбором и рассчитаем ваш проект.</p></div>
          <Link className="visit-link" href="/contacts"><span>Контакты и схема проезда</span><small>ТЦ «Светофор», Балашиха</small><b aria-hidden="true">→</b></Link>
          <a className="visit-link" href="tel:+74955210093"><span>Заказать бесплатный замер</span><small>Позвоните нам, чтобы договориться</small><b aria-hidden="true">→</b></a>
        </section>
      </div>
    );
  } catch (error) {
    const message = error instanceof ApiError ? "Каталог временно недоступен." : "Не удалось загрузить каталог.";
    return <p className="notice page-shell">{message}</p>;
  }
}
