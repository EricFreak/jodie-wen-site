import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const publications = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/publications' }),
  schema: z.object({
    titleEn: z.string(),
    titleZh: z.string(),
    outlet: z.string(),
    date: z.coerce.date(),
    url: z.string().url(),
    lang: z.enum(['en', 'zh']),
  }),
});

const media = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/media' }),
  schema: z.object({
    titleEn: z.string(),
    titleZh: z.string(),
    type: z.enum(['video', 'interview', 'mention']),
    outlet: z.string(),
    date: z.coerce.date(),
    url: z.string().url(),
    embedUrl: z.string().url().optional(),
    platform: z.enum(['youtube', 'bilibili', 'cgtv', 'other']),
  }),
});

const activities = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/activities' }),
  schema: z.object({
    titleEn: z.string(),
    titleZh: z.string(),
    event: z.string(),
    location: z.string(),
    eventZh: z.string(),
    locationZh: z.string(),
    date: z.coerce.date(),
    url: z.string().url().optional(),
  }),
});

export const collections = { publications, media, activities };
