import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const publications = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/publications' }),
  schema: z.object({
    titleEn: z.string(),
    titleZh: z.string(),
    titleAr: z.string().optional(),
    outlet: z.string(),
    date: z.coerce.date(),
    url: z.string().url(),
    lang: z.enum(['en', 'zh']),
    cover: z.string().optional(),
    detail: z.boolean().optional(),
  }),
});

const media = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/media' }),
  schema: z.object({
    titleEn: z.string(),
    titleZh: z.string(),
    titleAr: z.string().optional(),
    type: z.enum(['video', 'interview', 'mention']),
    outlet: z.string(),
    date: z.coerce.date(),
    url: z.string().url(),
    embedUrl: z.string().url().optional(),
    platform: z.enum(['youtube', 'bilibili', 'cgtv', 'other']),
    featured: z.boolean().optional(),
    cover: z.string().optional(),
    summaryEn: z.string().optional(),
    summaryZh: z.string().optional(),
    detail: z.boolean().optional(),
  }),
});

const activities = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/activities' }),
  schema: z.object({
    titleEn: z.string(),
    titleZh: z.string(),
    titleAr: z.string().optional(),
    event: z.string(),
    location: z.string(),
    eventZh: z.string(),
    locationZh: z.string(),
    eventAr: z.string().optional(),
    locationAr: z.string().optional(),
    date: z.coerce.date(),
    url: z.union([z.string().url(), z.string().startsWith('/')]).optional(),
    cover: z.string().optional(),
    detail: z.boolean().optional(),
  }),
});

const gallery = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/gallery' }),
  schema: z.object({
    image: z.string(),
    captionEn: z.string(),
    captionZh: z.string(),
    captionAr: z.string(),
    date: z.coerce.date().optional(),
  }),
});

// 站内全文：一篇原文按语言拆成多个 Markdown 文件，正文为 Markdown，元数据仍以原条目为准。
const articleBodies = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/articleBodies' }),
  schema: z.object({
    sourceCollection: z.enum(['publications', 'media', 'activities']),
    sourceId: z.string(),
    locale: z.enum(['en', 'zh', 'ar']),
    sourceLang: z.enum(['en', 'zh', 'ar']),
    title: z.string(),
    sourceName: z.string(),
    coverCredit: z.string().optional(),
  }),
});

export const collections = { publications, media, activities, gallery, articleBodies };
