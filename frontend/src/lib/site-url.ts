const fallbackSiteUrl = "https://avantistyle.ru";

export function getSiteUrl(): URL {
  return new URL((process.env.AVANTI_SITE_URL ?? fallbackSiteUrl).replace(/\/$/, ""));
}
