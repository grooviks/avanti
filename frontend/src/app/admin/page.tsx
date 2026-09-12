import type { Metadata } from "next";

import { AdminPanel } from "./admin-panel";

export const metadata: Metadata = {
  title: "Админка — Avantistyle",
  description: "Управление каталогом Avantistyle.",
};

export default function AdminPage() {
  return <AdminPanel />;
}
