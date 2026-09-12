import type { components } from "./openapi";

// Эти типы генерируются из backend /openapi.json через openapi-typescript.
export type CatalogImage = components["schemas"]["ImageOut"];
export type Category = components["schemas"]["CategoryOut"];
export type CategoryTree = components["schemas"]["CategoryTreeOut"];
export type Product = components["schemas"]["ProductOut"];

const apiBaseUrl = (process.env.AVANTI_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {}

async function get<T>(path: string): Promise<T> {
  // API address is supplied by Docker at runtime (`http://api:8000`), not at
  // image-build time. Dynamic rendering also makes catalogue updates visible
  // immediately after an admin saves them.
  const response = await fetch(`${apiBaseUrl}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new ApiError(`API returned ${response.status} for ${path}`);
  }
  return response.json() as Promise<T>;
}

export function getCategories(): Promise<CategoryTree[]> {
  return get<CategoryTree[]>("/catalog/categories");
}

export function getCategory(id: string): Promise<Category> {
  return get<Category>(`/catalog/categories/${id}`);
}

export function getCategoryProducts(id: string): Promise<Product[]> {
  return get<Product[]>(`/catalog/categories/${id}/products`);
}

export function getProduct(id: string): Promise<Product> {
  return get<Product>(`/catalog/products/${id}`);
}

export function mediaUrl(url: string): string {
  return url.startsWith("http") ? url : `${apiBaseUrl}${url}`;
}
