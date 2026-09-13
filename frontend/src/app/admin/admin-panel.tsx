"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import type { components } from "@/lib/openapi";

import styles from "./admin.module.css";
import treeStyles from "./admin-tree.module.css";

type CategoryTree = components["schemas"]["CategoryTreeOut"];
type Product = components["schemas"]["ProductOut"];
type User = components["schemas"]["UserOut"];
type ImageInput = { url: string; alt: string; position: number };
export type AdminSection = "products" | "categories";

type ProductForm = {
  id: number | null;
  categoryId: string;
  name: string;
  description: string;
  price: string;
  sku: string;
  inStock: boolean;
  images: ImageInput[];
};

const tokenKey = "avanti-admin-token";

const emptyProduct = (): ProductForm => ({
  id: null,
  categoryId: "",
  name: "",
  description: "",
  price: "",
  sku: "",
  inStock: true,
  images: [],
});

const transliteration: Record<string, string> = {
  а: "a", б: "b", в: "v", г: "g", д: "d", е: "e", ё: "e", ж: "zh", з: "z",
  и: "i", й: "y", к: "k", л: "l", м: "m", н: "n", о: "o", п: "p", р: "r",
  с: "s", т: "t", у: "u", ф: "f", х: "kh", ц: "ts", ч: "ch", ш: "sh", щ: "shch",
  ъ: "", ы: "y", ь: "", э: "e", ю: "yu", я: "ya",
};

function categorySlug(name: string): string {
  return [...name.toLowerCase()]
    .map((character) => transliteration[character] ?? character)
    .join("")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function flattenCategories(items: CategoryTree[]): CategoryTree[] {
  return items.flatMap((item) => [item, ...flattenCategories(item.children)]);
}

function apiUrl(path: string): string {
  return path.startsWith("http://") || path.startsWith("https://")
    ? path
    : `/api/backend/${path.replace(/^\//, "")}`;
}

async function api<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(apiUrl(path), { ...options, headers, cache: "no-store" });
  if (!response.ok) {
    const data = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(data?.detail || "Не удалось выполнить запрос.");
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

function productToForm(product: Product): ProductForm {
  return {
    id: product.id,
    categoryId: String(product.category_id),
    name: product.name,
    description: product.description ?? "",
    price: product.price,
    sku: product.sku ?? "",
    inStock: product.in_stock,
    images: product.images.map((image) => ({
      url: image.url,
      alt: image.alt ?? "",
      position: image.position,
    })),
  };
}

export function AdminPanel({ section }: { section: AdminSection }) {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [categories, setCategories] = useState<CategoryTree[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [form, setForm] = useState<ProductForm>(emptyProduct);
  const [query, setQuery] = useState("");
  const [expandedCategories, setExpandedCategories] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [categoryName, setCategoryName] = useState("");
  const [categoryDescription, setCategoryDescription] = useState("");
  const [categoryParentId, setCategoryParentId] = useState("");
  const [editingCategoryId, setEditingCategoryId] = useState<number | null>(null);
  const [editingCategoryDescription, setEditingCategoryDescription] = useState("");
  const [categoryImage, setCategoryImage] = useState<File | null>(null);
  const [categoryUploadingId, setCategoryUploadingId] = useState<number | null>(null);

  const flatCategories = useMemo(() => flattenCategories(categories), [categories]);
  const categoryGroups = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return flatCategories.map((category) => {
      const categoryProducts = products.filter((product) => product.category_id === category.id);
      const matchingProducts = normalizedQuery
        ? categoryProducts.filter((product) => product.name.toLowerCase().includes(normalizedQuery))
        : categoryProducts;
      const matchesCategory = category.name.toLowerCase().includes(normalizedQuery);
      return { category, products: normalizedQuery && matchesCategory ? categoryProducts : matchingProducts };
    }).filter(({ category, products: groupedProducts }) => !normalizedQuery || category.name.toLowerCase().includes(normalizedQuery) || groupedProducts.length > 0);
  }, [flatCategories, products, query]);

  async function loadCatalog(accessToken: string) {
    setLoading(true);
    setError(null);
    try {
      const tree = await api<CategoryTree[]>("catalog/categories", {}, accessToken);
      const flattened = flattenCategories(tree);
      const groups = await Promise.all(
        flattened.map((category) => api<Product[]>(`catalog/categories/${category.id}/products`, {}, accessToken)),
      );
      setCategories(tree);
      setProducts(groups.flat().sort((a, b) => a.name.localeCompare(b.name, "ru")));
      setExpandedCategories((current) => current.length ? current : flattened.slice(0, 2).map((category) => category.id));
      setForm((current) => current.categoryId ? current : { ...current, categoryId: String(flattened[0]?.id ?? "") });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось загрузить каталог.");
    } finally {
      setLoading(false);
    }
  }

  async function restoreSession(accessToken: string) {
    try {
      const currentUser = await api<User>("auth/me", {}, accessToken);
      if (!currentUser.is_superuser) throw new Error("У этой учётной записи нет прав администратора.");
      setToken(accessToken);
      setUser(currentUser);
      await loadCatalog(accessToken);
    } catch {
      sessionStorage.removeItem(tokenKey);
    }
  }

  useEffect(() => {
    const savedToken = sessionStorage.getItem(tokenKey);
    if (savedToken) void restoreSession(savedToken);
  }, []);

  async function login(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const body = new URLSearchParams({ username: email, password });
      const auth = await api<{ access_token: string }>("auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      const currentUser = await api<User>("auth/me", {}, auth.access_token);
      if (!currentUser.is_superuser) throw new Error("У этой учётной записи нет прав администратора.");
      sessionStorage.setItem(tokenKey, auth.access_token);
      setToken(auth.access_token);
      setUser(currentUser);
      setPassword("");
      await loadCatalog(auth.access_token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось войти.");
    } finally {
      setSaving(false);
    }
  }

  function logout() {
    sessionStorage.removeItem(tokenKey);
    setToken(null);
    setUser(null);
    setProducts([]);
    setCategories([]);
    setExpandedCategories([]);
    setForm(emptyProduct());
  }

  async function uploadImages(files: FileList | null) {
    if (!files || !token) return;
    setUploading(true);
    setError(null);
    try {
      const uploaded = await Promise.all(Array.from(files).map(async (file, index) => {
        const data = new FormData();
        data.append("file", file);
        const media = await api<{ url: string }>("admin/media/products", { method: "POST", body: data }, token);
        return { url: media.url, alt: form.name, position: form.images.length + index };
      }));
      setForm((current) => ({ ...current, images: [...current.images, ...uploaded] }));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось загрузить изображения.");
    } finally {
      setUploading(false);
    }
  }

  async function saveProduct(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    const slug = categorySlug(form.name);
    if (!slug) {
      setSaving(false);
      setError("Введите название товара буквами или цифрами.");
      return;
    }
    const payload = {
      category_id: Number(form.categoryId),
      name: form.name.trim(),
      slug,
      description: form.description.trim() || null,
      price: form.price,
      sku: form.sku.trim() || null,
      in_stock: form.inStock,
      images: form.images.map((image, position) => ({ ...image, position })),
    };
    try {
      if (form.id) {
        await api<Product>(`admin/products/${form.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }, token);
        setMessage("Товар сохранён.");
      } else {
        await api<Product>("admin/products", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }, token);
        setMessage("Товар добавлен в каталог.");
      }
      setForm(emptyProduct());
      await loadCatalog(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось сохранить товар.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteProduct(product: Product) {
    if (!token || !window.confirm(`Удалить «${product.name}»?`)) return;
    setError(null);
    try {
      await api<void>(`admin/products/${product.id}`, { method: "DELETE" }, token);
      if (form.id === product.id) setForm(emptyProduct());
      setMessage("Товар удалён.");
      await loadCatalog(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось удалить товар.");
    }
  }

  async function deleteCategory(category: CategoryTree, productCount: number) {
    if (!token) return;
    if (productCount > 0 || category.children.length > 0) {
      setError("Сначала удалите товары и вложенные категории — затем категорию можно будет удалить.");
      return;
    }
    if (!window.confirm(`Удалить пустую категорию «${category.name}»?`)) return;
    setError(null);
    setMessage(null);
    try {
      await api<void>(`admin/categories/${category.id}`, { method: "DELETE" }, token);
      setExpandedCategories((current) => current.filter((id) => id !== category.id));
      if (form.categoryId === String(category.id)) setForm(emptyProduct());
      setMessage(`Категория «${category.name}» удалена.`);
      await loadCatalog(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось удалить категорию.");
    }
  }

  function toggleCategory(categoryId: number) {
    setExpandedCategories((current) => current.includes(categoryId)
      ? current.filter((id) => id !== categoryId)
      : [...current, categoryId]);
  }

  async function createCategory(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    setSaving(true);
    setError(null);
    try {
      const slug = categorySlug(categoryName);
      if (!slug) throw new Error("Введите название категории буквами или цифрами.");
      let images: ImageInput[] = [];
      if (categoryImage) {
        const data = new FormData();
        data.append("file", categoryImage);
        const media = await api<{ url: string }>("admin/media/categories", { method: "POST", body: data }, token);
        images = [{ url: media.url, alt: categoryName.trim(), position: 0 }];
      }
      await api("admin/categories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: categoryName.trim(),
          slug,
          description: categoryDescription.trim() || null,
          position: flatCategories.length,
          parent_id: categoryParentId ? Number(categoryParentId) : null,
          images,
        }),
      }, token);
      setCategoryName("");
      setCategoryDescription("");
      setCategoryParentId("");
      setCategoryImage(null);
      setMessage("Категория создана.");
      await loadCatalog(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось создать категорию.");
    } finally {
      setSaving(false);
    }
  }

  async function replaceCategoryImage(category: CategoryTree, files: FileList | null) {
    const file = files?.[0];
    if (!token || !file) return;
    setCategoryUploadingId(category.id);
    setError(null);
    setMessage(null);
    try {
      const data = new FormData();
      data.append("file", file);
      const media = await api<{ url: string }>("admin/media/categories", { method: "POST", body: data }, token);
      await api(`admin/categories/${category.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ images: [{ url: media.url, alt: category.name, position: 0 }] }),
      }, token);
      setMessage(`Фото категории «${category.name}» обновлено.`);
      await loadCatalog(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось обновить фото категории.");
    } finally {
      setCategoryUploadingId(null);
    }
  }

  function editCategoryDescription(category: CategoryTree) {
    setEditingCategoryId(category.id);
    setEditingCategoryDescription(category.description ?? "");
    setError(null);
    setMessage(null);
  }

  async function saveCategoryDescription(event: React.FormEvent<HTMLFormElement>, category: CategoryTree) {
    event.preventDefault();
    if (!token) return;
    setSaving(true);
    setError(null);
    try {
      await api(`admin/categories/${category.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: editingCategoryDescription.trim() || null }),
      }, token);
      setEditingCategoryId(null);
      setMessage(`Подпись категории «${category.name}» сохранена.`);
      await loadCatalog(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Не удалось сохранить подпись категории.");
    } finally {
      setSaving(false);
    }
  }

  if (!token || !user) {
    return (
      <main className={styles.loginPage}>
        <section className={styles.loginCard}>
          <p className={styles.eyebrow}>Avantistyle · служебный доступ</p>
          <h1>Управление каталогом</h1>
          <p>Добавляйте товары, изображения и категории. Доступ есть только у администратора.</p>
          <form onSubmit={login} className={styles.form}>
            <label>Электронная почта<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
            <label>Пароль<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
            {error && <p className={styles.error} role="alert">{error}</p>}
            <button className={styles.primaryButton} disabled={saving}>{saving ? "Входим…" : "Войти в админку"}</button>
          </form>
        </section>
      </main>
    );
  }

  const isProducts = section === "products";
  const catalogPanel = (
    <aside className={styles.catalogPanel}>
      <div className={styles.panelHeading}>
        <div>
          <p className={styles.eyebrow}>{isProducts ? "Товары по категориям" : "Структура каталога"}</p>
          <h2>{isProducts ? "Товары" : "Категории"} <span className={treeStyles.catalogTitleCount}>{isProducts ? products.length : flatCategories.length}</span></h2>
        </div>
        <button onClick={() => token && void loadCatalog(token)} className={styles.textButton} disabled={loading}>{loading ? "Обновляем…" : "Обновить"}</button>
      </div>
      <input className={styles.search} value={query} onChange={(event) => setQuery(event.target.value)} placeholder={isProducts ? "Поиск категории или товара" : "Поиск категории"} />
      <div className={treeStyles.categoryList}>{categoryGroups.map(({ category, products: groupedProducts }) => {
        const isOpen = isProducts && (expandedCategories.includes(category.id) || Boolean(query));
        return <section key={category.id} className={treeStyles.categoryGroup}>
          <div className={treeStyles.categoryHeader}>
            <button type="button" className={treeStyles.categoryToggle} onClick={isProducts ? () => toggleCategory(category.id) : undefined} aria-expanded={isProducts ? isOpen : undefined}>
              <span className={treeStyles.categoryLabel}>{category.images[0] ? <img src={apiUrl(category.images[0].url)} alt="" /> : <i aria-hidden="true" />}<span><strong>{category.parent_id ? "— " : ""}{category.name}</strong><small>{isProducts ? `${groupedProducts.length} ${groupedProducts.length === 1 ? "товар" : "товаров"}` : category.description || "Подпись не добавлена"}</small></span></span>
              {isProducts && <b aria-hidden="true">{isOpen ? "−" : "+"}</b>}
            </button>
            {!isProducts && <>
              <button type="button" className={treeStyles.categoryText} onClick={() => editCategoryDescription(category)} title="Редактировать подпись категории">Текст</button>
              <label className={treeStyles.categoryPhoto} title={category.images[0] ? "Заменить фото категории" : "Добавить фото категории"}>{categoryUploadingId === category.id ? "…" : "Фото"}<input type="file" accept="image/*" onChange={(event) => void replaceCategoryImage(category, event.target.files)} disabled={categoryUploadingId === category.id} /></label>
              <button type="button" className={treeStyles.categoryDelete} onClick={() => void deleteCategory(category, groupedProducts.length)} title="Удалить категорию" aria-label={`Удалить категорию ${category.name}`}>×</button>
            </>}
          </div>
          {!isProducts && editingCategoryId === category.id && <form className={treeStyles.categoryDescriptionEditor} onSubmit={(event) => void saveCategoryDescription(event, category)}><label>Подпись в каталоге<textarea value={editingCategoryDescription} onChange={(event) => setEditingCategoryDescription(event.target.value)} placeholder="Коротко опишите категорию" rows={2} /></label><span><button type="button" onClick={() => setEditingCategoryId(null)}>Отмена</button><button type="submit" disabled={saving}>{saving ? "Сохраняем…" : "Сохранить"}</button></span></form>}
          {isProducts && isOpen && <div className={`${styles.productList} ${treeStyles.groupProducts}`}>{groupedProducts.map((product) => <article key={product.id} className={styles.productRow}><button type="button" className={styles.editProduct} onClick={() => { setForm(productToForm(product)); setMessage(null); }}><span className={styles.productThumb}>{product.images[0] && <img src={apiUrl(product.images[0].url)} alt="" />}</span><span><strong>{product.name}</strong><small>{product.price} ₽ · {product.in_stock ? "в наличии" : "нет в наличии"}</small></span></button><button type="button" className={styles.deleteButton} onClick={() => void deleteProduct(product)} aria-label={`Удалить ${product.name}`}>×</button></article>)}</div>}
        </section>;
      })}</div>
      {categoryGroups.length === 0 && <p className={styles.empty}>{isProducts ? "Подходящих категорий или товаров нет." : "Подходящих категорий нет."}</p>}
    </aside>
  );

  const productEditor = (
    <form className={styles.productEditor} onSubmit={saveProduct}>
          <div className={styles.editorHeading}>
            <div><p className={styles.eyebrow}>{form.id ? "Редактирование" : "Новый товар"}</p><h2>{form.id ? form.name || "Товар" : "Добавить товар"}</h2></div>
            {form.id && <button type="button" className={styles.textButton} onClick={() => setForm(emptyProduct())}>Новый товар</button>}
          </div>
          <div className={styles.fieldGrid}>
            <label className={styles.wide}>Название<input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required /></label>
            <label>Категория<select value={form.categoryId} onChange={(event) => setForm({ ...form, categoryId: event.target.value })} required><option value="">Выберите категорию</option>{flatCategories.map((category) => <option value={category.id} key={category.id}>{category.parent_id ? "— " : ""}{category.name}</option>)}</select></label>
            <label>Цена, ₽<input type="number" min="0" step="0.01" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} required /></label>
            <label>Артикул<input value={form.sku} onChange={(event) => setForm({ ...form, sku: event.target.value })} /></label>
            <label className={`${styles.wide} ${styles.checkbox}`}><input type="checkbox" checked={form.inStock} onChange={(event) => setForm({ ...form, inStock: event.target.checked })} /> В наличии</label>
            <label className={styles.wide}>Описание<textarea rows={4} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label>
          </div>
          <div className={styles.imagesBlock}>
            <div><h3>Фотографии</h3><p>Первая фотография станет обложкой товара.</p></div>
            <label className={styles.uploadButton}> {uploading ? "Загрузка…" : "Добавить фотографии"}<input type="file" accept="image/*" multiple onChange={(event) => void uploadImages(event.target.files)} disabled={uploading} /></label>
            {form.images.length > 0 && <div className={styles.imageList}>{form.images.map((image, index) => <figure key={`${image.url}-${index}`}><img src={apiUrl(image.url)} alt={image.alt || form.name || "Фотография товара"} /><button type="button" aria-label="Убрать фотографию" onClick={() => setForm({ ...form, images: form.images.filter((_, imageIndex) => imageIndex !== index) })}>×</button></figure>)}</div>}
          </div>
          <button className={styles.primaryButton} disabled={saving || uploading || flatCategories.length === 0}>{saving ? "Сохраняем…" : form.id ? "Сохранить изменения" : "Опубликовать товар"}</button>
    </form>
  );

  const categoryCreator = (
    <section className={styles.categorySection}>
        <div><p className={styles.eyebrow}>Структура каталога</p><h2>Категории</h2><p>{flatCategories.length ? flatCategories.map((category) => category.name).join(" · ") : "Создайте первую категорию — затем в неё можно добавлять товары."}</p></div>
        <form className={styles.categoryForm} onSubmit={createCategory}><input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} placeholder="Название категории" required /><label>Родительская категория<select value={categoryParentId} onChange={(event) => setCategoryParentId(event.target.value)}><option value="">Корневая категория</option>{flatCategories.map((category) => <option key={category.id} value={category.id}>{category.parent_id ? "— " : ""}{category.name}</option>)}</select></label><label className={styles.categoryImageUpload}>Фото категории <input type="file" accept="image/*" onChange={(event) => setCategoryImage(event.target.files?.[0] ?? null)} />{categoryImage && <small>{categoryImage.name}</small>}</label><label className={styles.categoryDescription}>Подпись в каталоге<textarea value={categoryDescription} onChange={(event) => setCategoryDescription(event.target.value)} placeholder="Например: мягкая мебель для гостиной" rows={2} /></label><button className={styles.secondaryButton} disabled={saving}>{saving ? "Создаём…" : "Создать категорию"}</button></form>
    </section>
  );

  return (
    <main className={styles.adminPage}>
      <header className={styles.adminHeader}>
        <div><p className={styles.eyebrow}>Avantistyle · админка</p><h1>Каталог мебели</h1></div>
        <div className={styles.headerActions}><span>{user.email}</span><button onClick={logout} className={styles.textButton}>Выйти</button></div>
      </header>
      <nav className={styles.adminNav} aria-label="Разделы админки">
        <Link className={isProducts ? styles.activeNavLink : undefined} href="/admin/products">Товары</Link>
        <Link className={!isProducts ? styles.activeNavLink : undefined} href="/admin/categories">Категории</Link>
      </nav>

      {(error || message) && <p className={error ? styles.error : styles.success} role="status">{error ?? message}</p>}

      {isProducts ? <section className={styles.workspace}>{productEditor}{catalogPanel}</section> : <section className={styles.categoryWorkspace}>{catalogPanel}{categoryCreator}</section>}
    </main>
  );
}
