import { defaultLocale, type Locale } from './ui';

export function getLocaleFromPath(pathname: string): Locale {
  return pathname === '/zh' || pathname.startsWith('/zh/') ? 'zh' : defaultLocale;
}

/** 当前页面对应的另一语言路径（规格 §4.1：导航语言切换指向同页另一语言） */
export function getAlternatePath(pathname: string): string {
  if (getLocaleFromPath(pathname) === 'zh') {
    return pathname.replace(/^\/zh/, '') || '/';
  }
  return pathname === '/' ? '/zh/' : `/zh${pathname}`;
}

/** 把无前缀路径转换为指定 locale 的路由路径 */
export function localizePath(path: string, locale: Locale): string {
  return locale === 'zh' ? (path === '/' ? '/zh/' : `/zh${path}`) : path;
}
