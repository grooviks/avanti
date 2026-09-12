import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import "./brand-overrides.css";

export const metadata: Metadata = {
  title: "Avantistyle — мебельный салон",
  description: "Мебель для дома, кухни и офиса. Салон Avantistyle в Балашихе.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>
        <div className="topline">
          <span>Мебельный салон · Балашиха</span>
          <a href="tel:+74955210093">+7 (495) 521-00-93</a>
        </div>
        <header className="header">
          <Link className="brand" href="/" aria-label="Avantistyle — главная">
            <span className="brand-overline">Мебельный салон</span>
            <span className="brand-name">Avanti<span>Style</span></span>
          </Link>
          <nav aria-label="Основная навигация">
            <Link href="/#catalog">Каталог</Link>
            <Link href="/contacts">Контакты</Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer>
          <div className="footer-brand">
            <p>Мебельный салон</p>
            <strong>Avanti<span>Style</span></strong>
            <span>Мебель для вашего дома</span>
          </div>
          <nav className="footer-nav" aria-label="Навигация в подвале">
            <Link href="/#catalog">Каталог</Link>
            <Link href="/contacts">Контакты</Link>
          </nav>
          <div className="footer-contacts">
            <span>Балашиха · ежедневно 10:00–20:00</span>
            <a href="tel:+74955210093">+7 (495) 521-00-93</a>
          </div>
          <div className="footer-photo">
            <img src="/footer-interior.png" alt="Журнальный столик в уютном интерьере" />
          </div>
        </footer>
      </body>
    </html>
  );
}
