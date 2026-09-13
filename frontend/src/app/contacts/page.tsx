import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Контакты — Avantistyle",
  description: "Контакты мебельного салона Avantistyle в Балашихе.",
};

const organizationUrl = "https://yandex.ru/maps/org/173240493869";
const yandexAwardBadgeUrl = "https://yandex.ru/sprav/widget/rating-badge/173240493869?type=award";
const whatsappUrl = "https://wa.me/79035018087";

export default function ContactsPage() {
  return (
    <main className="contacts-page">
      <section className="contacts-hero">
        <p className="eyebrow">Будем рады знакомству</p>
        <h1>Загляните к нам в салон</h1>
        <p>Посмотрите мебель, сравните материалы и обсудите будущий интерьер с консультантом.</p>
      </section>
      <section className="contacts-layout" aria-label="Контакты салона">
        <article className="contact-details">
          <p className="contact-kicker">ТЦ «Светофор»</p>
          <h2>Салон Avantistyle в Балашихе</h2>
          <p className="contact-map-intro">Найдите нас на карте, посмотрите вход и сразу постройте удобный маршрут.</p>
          <dl>
            <div><dt>Адрес</dt><dd>Московская область, Балашиха,<br />Шоссе Энтузиастов, д. 1Б,<br />ТЦ «Светофор», цокольный этаж</dd></div>
            <div><dt>Время работы</dt><dd>Ежедневно, 10:00–20:00</dd></div>
            <div><dt>Телефон</dt><dd><a href="tel:+74955210093">+7 (495) 521-00-93</a><br /><a href="tel:+79035018087">+7 (903) 501-80-87</a></dd></div>
          </dl>
          <section className="messenger-links" aria-label="Мессенджеры салона">
            <p className="contact-kicker">Напишите нам</p>
            <div>
              <a className="messenger-icon whatsapp" href={whatsappUrl} target="_blank" rel="noreferrer" aria-label="Написать в WhatsApp"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.4a8.5 8.5 0 0 0-7.29 12.87L3.7 20.6l4.48-.98A8.5 8.5 0 1 0 12 3.4Zm0 15.57a7.04 7.04 0 0 1-3.59-.99l-.26-.15-2.66.58.57-2.58-.17-.27A7.05 7.05 0 1 1 12 18.97Zm3.87-5.28c-.21-.1-1.23-.61-1.42-.68-.19-.07-.33-.1-.47.1-.14.2-.54.67-.66.81-.12.14-.24.16-.45.06-.21-.1-.88-.32-1.68-1.03-.62-.55-1.04-1.23-1.16-1.44-.12-.2-.01-.31.09-.41.09-.09.21-.24.31-.36.1-.12.14-.2.21-.34.07-.14.04-.26-.02-.36-.05-.1-.47-1.13-.64-1.55-.17-.4-.34-.35-.47-.36h-.4c-.14 0-.36.05-.55.26-.19.2-.72.7-.72 1.72s.74 2  .84 2.14c.1.14 1.45 2.21 3.5 3.1.49.21.87.34 1.17.43.49.15.93.13 1.28.08.39-.06 1.23-.5 1.4-.98.17-.48.17-.9.12-.98-.05-.09-.19-.14-.4-.24Z" /></svg></a>
              <span className="messenger-icon unavailable telegram" aria-label="Telegram — ссылка появится позже" title="Telegram — скоро"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.6 4.2 3.9 10.6c-1.14.45-1.13 1.09-.2 1.38l4.28 1.34 1.66 5.1c.2.55.1.77.68.77.44 0 .63-.2.88-.44l2.04-1.98 4.25 3.14c.78.43 1.34.2 1.54-.72l2.85-13.42c.3-1.14-.44-1.66-1.28-1.57Zm-11.95 8.69 9.65-6.09c.48-.29.92-.13.56.19l-8.27 7.47-.32 3.4-1.62-4.97Z" /></svg></span>
              <span className="messenger-icon unavailable max" aria-label="MAX — ссылка появится позже" title="MAX — скоро">MAX</span>
            </div>
          </section>
          <div className="contact-bottom-actions">
            <a className="maps-card" href={organizationUrl} target="_blank" rel="noreferrer">
              <span className="maps-card-pin" aria-hidden="true">●</span>
              <span className="maps-card-copy"><small>Мы на</small><strong>Яндекс Картах</strong></span>
              <span className="maps-card-open" aria-hidden="true">↗</span>
            </a>
            <div className="yandex-badge" aria-label="Награда Avantistyle на Яндекс Картах">
              <iframe title="Награда Avantistyle на Яндекс Картах" src={yandexAwardBadgeUrl} width="150" height="50" />
            </div>
          </div>
        </article>
        <figure className="location-image">
          <img src="/svetofor-exterior.jpeg" alt="Современное здание торгового центра «Светофор» в Балашихе" />
          <figcaption><strong>ТЦ «Светофор»</strong><span>Шоссе Энтузиастов, 1Б</span></figcaption>
        </figure>
      </section>
    </main>
  );
}
