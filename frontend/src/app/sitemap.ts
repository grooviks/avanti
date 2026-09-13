import type { MetadataRoute } from "next";

import { getCategories, getCategoryProducts, type CategoryTree } from "@/lib/api";
import { getSiteUrl } from "@/lib/site-url";

export const dynamic = "force-dynamic";

function flattenCategories(categories: CategoryTree[]): CategoryTree[] {
  return categories.flatMap((category) => [category, ...flattenCategories(category.children)]);
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const siteUrl = getSiteUrl();
  const staticPages: MetadataRoute.Sitemap = ["/", "/contacts"].map((path) => ({
    url: new URL(path, siteUrl).toString(),
    changeFrequency: "weekly",
    priority: path === "/" ? 1 : 0.7,
  }));

  try {
    const categories = flattenCategories(await getCategories());
    const categoryPages: MetadataRoute.Sitemap = categories.map((category) => ({
      url: new URL(`/category/${category.id}`, siteUrl).toString(),
      changeFrequency: "weekly",
      priority: 0.8,
    }));
    const productsByCategory = await Promise.all(
      categories.map(async (category) => getCategoryProducts(String(category.id))),
    );
    const productIds = new Set(productsByCategory.flat().map((product) => product.id));
    const productPages: MetadataRoute.Sitemap = [...productIds].map((id) => ({
      url: new URL(`/product/${id}`, siteUrl).toString(),
      changeFrequency: "weekly",
      priority: 0.6,
    }));

    return [...staticPages, ...categoryPages, ...productPages];
  } catch {
    // A transient catalogue API error must not make robots discover an error page.
    return staticPages;
  }
}
