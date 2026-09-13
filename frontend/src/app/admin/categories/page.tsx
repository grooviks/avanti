import type { Metadata } from "next";

import { AdminPanel } from "../admin-panel";

export const metadata: Metadata = {
  title: "Категории — админка Avantistyle",
};

export default function AdminCategoriesPage() {
  return <AdminPanel section="categories" />;
}
