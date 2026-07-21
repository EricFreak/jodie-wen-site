import { defaultLocale, locales, type Locale } from './ui';

export function getLocaleFromPath(pathname: string): Locale {
  for (const loc of locales) {
    if (loc === defaultLocale) continue;
    if (pathname === `/${loc}` || pathname.startsWith(`/${loc}/`)) return loc;
  }
  return defaultLocale;
}

/** 剥离路径中的语言前缀，得到中性路径（/ar/about/ → /about/，/zh/ → /，/about/ 原样） */
export function stripLocalePrefix(pathname: string): string {
  for (const loc of locales) {
    if (loc === defaultLocale) continue;
    if (pathname === `/${loc}` || pathname.startsWith(`/${loc}/`)) {
      return pathname.replace(new RegExp(`^/${loc}`), '') || '/';
    }
  }
  return pathname;
}

/** 把中性路径转换为指定 locale 的路由路径（'/' → '/ar/'，'/about' → '/ar/about'） */
export function localizePath(path: string, locale: Locale): string {
  return locale === defaultLocale ? path : path === '/' ? `/${locale}/` : `/${locale}${path}`;
}
