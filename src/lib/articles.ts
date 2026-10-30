import { getCollection, type CollectionEntry } from 'astro:content';
import type { Locale } from '../i18n/ui';

export type ArticleSection = 'publications' | 'media' | 'activities';

/**
 * 为某个 section 生成站内详情页的静态路径。
 * 只有带 `detail: true` 且当前语言存在正文的条目才会生成页面。
 */
export async function getArticlePaths<S extends ArticleSection>(section: S, locale: Locale) {
  const entries = await getCollection(section);
  const bodies = await getCollection('articleBodies');
  return entries.flatMap((entry) => {
    const detail = (entry.data as { detail?: boolean }).detail;
    if (!detail) return [];
    const body = bodies.find(
      (b) =>
        b.data.sourceCollection === section &&
        b.data.sourceId === entry.id &&
        b.data.locale === locale,
    );
    if (!body) return [];
    return [{ params: { slug: entry.id }, props: { entry, body } }];
  });
}

export type ArticleEntry =
  | CollectionEntry<'publications'>
  | CollectionEntry<'media'>
  | CollectionEntry<'activities'>;
