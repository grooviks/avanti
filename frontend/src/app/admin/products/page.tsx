import type { Metadata } from "next";

import { AdminPanel } from "../admin-panel";

export const metadata: Metadata = {
  title: "Товары — админка Avantistyle",
};

export default function AdminProductsPage() {
  return <AdminPanel section="products" />;
}
