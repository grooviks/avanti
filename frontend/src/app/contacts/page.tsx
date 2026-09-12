import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Контакты — Avantistyle",
  description: "Контакты мебельного салона Avantistyle в Балашихе.",
};

const routeUrl = "https://yandex.ru/maps/?text=%D0%A2%D0%A6%20%D0%A1%D0%B2%D0%B5%D1%82%D0%BE%D1%84%D0%BE%D1%80%2C%20%D0%91%D0%B0%D0%BB%D0%B0%D1%88%D0%B8%D1%85%D0%B0%2C%20%D0%A8%D0%BE%D1%81%D1%81%D0%B5%20%D0%AD%D0%BD%D1%82%D1%83%D0%B7%D0%B8%D0%B0%D1%81%D1%82%D0%BE%D0%B2%2C%201%D0%91";

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
          <dl>
            <div><dt>Адрес</dt><dd>Московская область, Балашиха,<br />Шоссе Энтузиастов, д. 1Б, цокольный этаж</dd></div>
            <div><dt>Время работы</dt><dd>Ежедневно, 10:00–20:00</dd></div>
            <div><dt>Телефон</dt><dd><a href="tel:+74955210093">+7 (495) 521-00-93</a><br /><a href="tel:+79035018087">+7 (903) 501-80-87</a></dd></div>
          </dl>
          <a className="route-link" href={routeUrl} target="_blank" rel="noreferrer">Открыть схему проезда <span aria-hidden="true">↗</span></a>
        </article>
        <figure className="location-image">
          <img src="/svetofor.jpg" alt="Торговый центр «Светофор» в Балашихе" />
          <figcaption>Салон расположен в ТЦ «Светофор»</figcaption>
        </figure>
      </section>
    </main>
  );
}
