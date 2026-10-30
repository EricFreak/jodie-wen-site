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

/** 本地化日期：en = August 13, 2026；zh = 2026年8月13日；ar = 13 أغسطس 2026（拉丁数字） */
export function formatDate(date: Date, locale: Locale): string {
  const tag = locale === 'zh' ? 'zh-CN' : locale === 'ar' ? 'ar' : 'en-US';
  return new Intl.DateTimeFormat(tag, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    numberingSystem: 'latn',
  }).format(date);
}

/** 替换 UI 字典中的 {source} / {date} 占位符 */
export function fillTemplate(template: string, values: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => values[key] ?? '');
}
