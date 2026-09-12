import Link from "next/link";

export default function NotFound() {
  return <div className="page-shell notice"><h1>Страница не найдена</h1><Link href="/">Вернуться в каталог</Link></div>;
}
