# 运营投递后台实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Astro 静态站增加 `/admin` 投递页 + GitHub Actions 自动入库管线，运营投素材、系统开 PR、审核人合并即发布。

**Architecture:** Vercel 侧只做门卫（鉴权、写 `.intake/request.json`、workflow_dispatch）；全部计算（抓取、LLM 分类翻译、查重、生成条目、开 PR、视频截帧封面）在 GitHub Actions 完成。PR 用 PAT 创建以触发后续封面工作流。设计与判定规则以 `docs/superpowers/specs/2026-08-09-admin-intake-pipeline-design.md` 为准。

**Tech Stack:** Astro 5（`output: 'static'` + `@astrojs/vercel`，仅 admin/api 路由 `prerender = false`）、原生 fetch（LLM/GitHub API，无 SDK）、zod 3、Node 22（`node:test` 单测）、GitHub Actions（yt-dlp + ffmpeg）。

## Global Constraints

- 不引入前端框架；admin 页只用少量原生 JS。
- 新依赖仅 `@astrojs/vercel` 与 `zod`（显式声明）；LLM/GitHub 调用一律原生 fetch。
- 现有 24 个前台路由与内容条目零改动；封面路径沿用 `/images/media/<slug>.jpg` 约定。
- 中文界面与文档；提交信息用英文 conventional commits。
- 测试框架：`node --test tests/`（Node 内置，不加测试依赖）。
- 每 Task 结束 `npm run build && npx astro check` 必须绿（纯 scripts 任务跑 `npm test`）。

---

### Task 1: 依赖、adapter 与共享 schema 抽取

**Files:**
- Modify: `package.json`
- Modify: `astro.config.mjs`
- Create: `src/lib/schemas.js`
- Modify: `src/content.config.ts`

**Interfaces:**
- Produces: `src/lib/schemas.js` 导出 `publicationSchema` / `mediaSchema` / `activitySchema` / `gallerySchema`（zod ZodObject，供 `content.config.ts` 与 Task 2 的 entry-writer 共用）。

- [ ] **Step 1: 安装依赖**

```bash
npm install @astrojs/vercel zod@^3.25.76
```

- [ ] **Step 2: astro.config.mjs 加 adapter**

完整文件：

```js
// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';

export default defineConfig({
  output: 'static',
  adapter: vercel(),
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh', 'ar'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
```

- [ ] **Step 3: 创建 src/lib/schemas.js**（纯 JS，Astro 侧与 Action 侧 Node 脚本都能直接 import）

```js
import { z } from 'zod';

export const publicationSchema = z.object({
  titleEn: z.string(),
  titleZh: z.string(),
  outlet: z.string(),
  date: z.coerce.date(),
  url: z.string().url(),
  lang: z.enum(['en', 'zh']),
});

export const mediaSchema = z.object({
  titleEn: z.string(),
  titleZh: z.string(),
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
});

export const activitySchema = z.object({
  titleEn: z.string(),
  titleZh: z.string(),
  event: z.string(),
  location: z.string(),
  eventZh: z.string(),
  locationZh: z.string(),
  date: z.coerce.date(),
  url: z.string().url().optional(),
});

export const gallerySchema = z.object({
  image: z.string(),
  captionEn: z.string(),
  captionZh: z.string(),
  captionAr: z.string(),
  date: z.coerce.date().optional(),
});
```

- [ ] **Step 4: 重写 src/content.config.ts**

```ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import {
  publicationSchema,
  mediaSchema,
  activitySchema,
  gallerySchema,
} from './lib/schemas.js';

const publications = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/publications' }),
  schema: publicationSchema,
});

const media = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/media' }),
  schema: mediaSchema,
});

const activities = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/activities' }),
  schema: activitySchema,
});

const gallery = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/gallery' }),
  schema: gallerySchema,
});

export const collections = { publications, media, activities, gallery };
```

- [ ] **Step 5: package.json 加 test 脚本**

在 `"scripts"` 中加一行：

```json
"test": "node --test tests/"
```

- [ ] **Step 6: 验证**

```bash
npm run build && npx astro check
```

Expected: 构建成功、0 errors；`dist/` 24 个前台路由仍为静态 HTML（adapter 额外产出 `.vercel/output` 属正常）。

- [ ] **Step 7: Commit**

```bash
git add package.json package-lock.json astro.config.mjs src/lib/schemas.js src/content.config.ts
git commit -m "feat: add vercel adapter and extract shared content schemas"
```

---

### Task 2: entry-writer（条目 Markdown 生成 + zod 校验）

**Files:**
- Create: `scripts/lib/entry-writer.mjs`
- Test: `tests/entry-writer.test.mjs`

**Interfaces:**
- Consumes: `src/lib/schemas.js` 的四个 schema。
- Produces:
  - `serializeEntry(collection: string, data: object): string` — zod 校验并序列化为 frontmatter Markdown；校验失败抛 ZodError。
  - `entryFileName(date: string|Date, titleEn: string): string` — `YYYY-MM-DD-slug.md`。
  - `toSlug(titleEn: string): string`。

- [ ] **Step 1: 写失败测试**

```js
// tests/entry-writer.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { serializeEntry, entryFileName, toSlug } from '../scripts/lib/entry-writer.mjs';

test('serializeEntry media minimal', () => {
  const md = serializeEntry('media', {
    titleEn: 'The Point: US-Iran deal',
    titleZh: '《欣视点》：美伊协议',
    type: 'video',
    outlet: 'CGTN',
    date: '2026-06-22',
    url: 'https://www.cgtn.com/tv/replay?id=DACeGIA',
    platform: 'cgtv',
  });
  assert.ok(md.startsWith('---\n'));
  assert.match(md, /titleEn: "The Point: US-Iran deal"/);
  assert.match(md, /date: 2026-06-22/);
  assert.match(md, /platform: "cgtv"/);
  assert.ok(!md.includes('cover'), 'optional 缺省字段不出现');
});

test('serializeEntry 转义双引号', () => {
  const md = serializeEntry('publications', {
    titleEn: 'He said "hi"',
    titleZh: '标题',
    outlet: 'X',
    date: '2026-01-01',
    url: 'https://example.com/a',
    lang: 'en',
  });
  assert.match(md, /titleEn: "He said \\"hi\\""/);
});

test('serializeEntry 缺必填字段抛错', () => {
  assert.throws(() =>
    serializeEntry('media', {
      titleEn: 'x',
      type: 'video',
      outlet: 'CGTN',
      date: '2026-06-22',
      url: 'https://example.com',
      platform: 'cgtv',
    }),
  );
});

test('toSlug', () => {
  assert.equal(toSlug('The Point: US-Iran deal!'), 'the-point-us-iran-deal');
  assert.equal(toSlug(''), 'untitled');
});

test('entryFileName', () => {
  assert.equal(entryFileName('2026-06-22', 'The Point'), '2026-06-22-the-point.md');
});
```

- [ ] **Step 2: 跑测试确认失败**

```bash
node --test tests/entry-writer.test.mjs
```

Expected: FAIL（Cannot find module '../scripts/lib/entry-writer.mjs'）。

- [ ] **Step 3: 实现 scripts/lib/entry-writer.mjs**

```js
import {
  publicationSchema,
  mediaSchema,
  activitySchema,
  gallerySchema,
} from '../../src/lib/schemas.js';

const schemas = {
  publications: publicationSchema,
  media: mediaSchema,
  activities: activitySchema,
  gallery: gallerySchema,
};

export function toSlug(titleEn) {
  const slug = String(titleEn)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60);
  return slug || 'untitled';
}

function formatDate(d) {
  return d.toISOString().slice(0, 10);
}

function yamlString(s) {
  return `"${String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
}

export function entryFileName(date, titleEn) {
  return `${formatDate(new Date(date))}-${toSlug(titleEn)}.md`;
}

export function serializeEntry(collection, data) {
  const schema = schemas[collection];
  if (!schema) throw new Error(`unknown collection: ${collection}`);
  const parsed = schema.parse(data);
  const lines = [];
  for (const key of Object.keys(schema.shape)) {
    const v = parsed[key];
    if (v === undefined) continue;
    if (v instanceof Date) lines.push(`${key}: ${formatDate(v)}`);
    else if (typeof v === 'boolean') lines.push(`${key}: ${v}`);
    else lines.push(`${key}: ${yamlString(v)}`);
  }
  return `---\n${lines.join('\n')}\n---\n`;
}
```

- [ ] **Step 4: 跑测试确认通过**

```bash
npm test
```

Expected: 5 个测试全 PASS。

- [ ] **Step 5: Commit**

```bash
git add scripts/lib/entry-writer.mjs tests/entry-writer.test.mjs
git commit -m "feat: add entry writer with schema validation"
```

---

### Task 3: dedupe（双源查重）

**Files:**
- Create: `scripts/lib/dedupe.mjs`
- Test: `tests/dedupe.test.mjs`

**Interfaces:**
- Produces:
  - `extractUrls(text: string): Set<string>` — 从 Markdown frontmatter 文本提取 `url: "..."`。
  - `collectContentUrls(contentDir: string): Set<string>` — 扫描目录下所有 `.md`。

- [ ] **Step 1: 写失败测试**

```js
// tests/dedupe.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { extractUrls, collectContentUrls } from '../scripts/lib/dedupe.mjs';

test('extractUrls', () => {
  const text = '---\nurl: "https://a.com/1"\n---\n---\nurl: "https://b.com/2"\nx: 1\n---\n';
  assert.deepEqual([...extractUrls(text)], ['https://a.com/1', 'https://b.com/2']);
});

test('collectContentUrls 扫描嵌套目录', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'dedupe-'));
  fs.mkdirSync(path.join(dir, 'media'));
  fs.mkdirSync(path.join(dir, 'publications'));
  fs.writeFileSync(path.join(dir, 'media', 'a.md'), '---\nurl: "https://a.com/1"\n---\n');
  fs.writeFileSync(path.join(dir, 'publications', 'b.md'), '---\nurl: "https://b.com/2"\n---\n');
  fs.writeFileSync(path.join(dir, 'publications', 'c.txt'), 'url: "https://ignore.me"');
  const urls = collectContentUrls(dir);
  assert.ok(urls.has('https://a.com/1'));
  assert.ok(urls.has('https://b.com/2'));
  assert.ok(!urls.has('https://ignore.me'));
});
```

- [ ] **Step 2: 跑测试确认失败**

```bash
node --test tests/dedupe.test.mjs
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 scripts/lib/dedupe.mjs**

```js
import fs from 'node:fs';
import path from 'node:path';

export function extractUrls(text) {
  const urls = new Set();
  for (const m of String(text).matchAll(/^url:\s*"([^"]+)"/gm)) {
    urls.add(m[1]);
  }
  return urls;
}

export function collectContentUrls(contentDir) {
  const urls = new Set();
  for (const col of fs.readdirSync(contentDir)) {
    const dir = path.join(contentDir, col);
    if (!fs.statSync(dir).isDirectory()) continue;
    for (const f of fs.readdirSync(dir)) {
      if (!f.endsWith('.md')) continue;
      for (const u of extractUrls(fs.readFileSync(path.join(dir, f), 'utf8'))) {
        urls.add(u);
      }
    }
  }
  return urls;
}
```

- [ ] **Step 4: 跑测试确认通过**

```bash
npm test
```

Expected: 全 PASS。

- [ ] **Step 5: Commit**

```bash
git add scripts/lib/dedupe.mjs tests/dedupe.test.mjs
git commit -m "feat: add content url dedupe scanner"
```

---

### Task 4: LLM 客户端与分类/翻译提示词

**Files:**
- Create: `scripts/lib/llm.mjs`
- Create: `scripts/lib/classify-prompt.mjs`
- Test: `tests/llm.test.mjs`

**Interfaces:**
- Produces:
  - `chatJson({ baseUrl, apiKey, model, system, user, fetchImpl? }): Promise<object>` — OpenAI 兼容 chat/completions，`response_format: json_object`，返回解析后的 JSON；非 200 抛错。
  - `CLASSIFY_SYSTEM: string`（分类判定清单）、`buildClassifyUser({ url, meta, typeOverride }): string`。
  - `CAPTION_SYSTEM: string`、`buildCaptionUser(caption: string): string`（gallery 三语图注）。

- [ ] **Step 1: 写失败测试**

```js
// tests/llm.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { chatJson } from '../scripts/lib/llm.mjs';
import { buildClassifyUser } from '../scripts/lib/classify-prompt.mjs';

test('chatJson 成功返回解析后 JSON', async () => {
  const fakeFetch = async (url, opts) => {
    assert.equal(url, 'https://api.example.com/v1/chat/completions');
    const body = JSON.parse(opts.body);
    assert.equal(body.model, 'test-model');
    assert.equal(body.response_format.type, 'json_object');
    return {
      ok: true,
      json: async () => ({ choices: [{ message: { content: '{"collection":"media"}' } }] }),
    };
  };
  const out = await chatJson({
    baseUrl: 'https://api.example.com/v1',
    apiKey: 'k', model: 'test-model', system: 's', user: 'u', fetchImpl: fakeFetch,
  });
  assert.equal(out.collection, 'media');
});

test('chatJson 非 200 抛错', async () => {
  const fakeFetch = async () => ({ ok: false, status: 500, text: async () => 'boom' });
  await assert.rejects(
    chatJson({ baseUrl: 'https://x', apiKey: 'k', model: 'm', system: 's', user: 'u', fetchImpl: fakeFetch }),
    /LLM 500/,
  );
});

test('buildClassifyUser 含 url 与人工指定类型', () => {
  const u = buildClassifyUser({ url: 'https://a.com', meta: { title: 'T' }, typeOverride: 'interview' });
  assert.match(u, /https:\/\/a\.com/);
  assert.match(u, /interview/);
});
```

- [ ] **Step 2: 跑测试确认失败**

```bash
node --test tests/llm.test.mjs
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 scripts/lib/llm.mjs**

```js
export async function chatJson({ baseUrl, apiKey, model, system, user, fetchImpl = fetch }) {
  const res = await fetchImpl(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: user },
      ],
      response_format: { type: 'json_object' },
      temperature: 0.2,
    }),
  });
  if (!res.ok) throw new Error(`LLM ${res.status}: ${await res.text()}`);
  const data = await res.json();
  return JSON.parse(data.choices[0].message.content);
}
```

- [ ] **Step 4: 实现 scripts/lib/classify-prompt.mjs**

```js
export const CLASSIFY_SYSTEM = `你是网站内容编辑助手。根据用户给的链接与页面元数据，判定内容应入哪个集合并生成双语字段。只输出 JSON，不要输出其他文字。

判定规则（严格按序适用）：
1. 用户指定了类型时，以用户指定为准。
2. 署名文章/专栏 → collection="publications"，lang 为文章主体语言（"en" 或 "zh"）。
3. 页面含真实视频播放器/嵌入（YouTube、Bilibili、CGTN 视频页特征）→ collection="media"，type="video"。
4. 音频、录音、播客、电台节目（如 radio.cgtn.com/podcast）→ collection="media"，type="interview"。严禁仅因"多媒体页面"归为 video。
5. 采访、对话、发言报道 → collection="media"，type="interview"；人物仅被提及 → type="mention"。
6. 论坛、对话、会议等活动 → collection="activities"。
7. 拿不准时向保守分类降级：video 与 interview 之争选 interview；拿不准也先收录并在 reason 中标注"请审核人确认"。

platform 判定：youtube.com/youtu.be → "youtube"；bilibili.com → "bilibili"；cgtn.com → "cgtv"；其他 → "other"。

输出 JSON 字段（按 collection 区分）：
- publications: {"collection","titleEn","titleZh","outlet","date","lang","reason"}
- media: {"collection","type","titleEn","titleZh","outlet","date","platform","summaryEn","summaryZh","reason"}
- activities: {"collection","titleEn","titleZh","event","location","eventZh","locationZh","date","reason"}
date 格式 YYYY-MM-DD，取内容发布日期；无法确定时用今天。titleEn/titleZh 互为翻译。summaryEn/summaryZh 各 2-4 句（media 必填，其他集合不需要）。`;

export function buildClassifyUser({ url, meta, typeOverride }) {
  return JSON.stringify({
    url,
    typeOverride: typeOverride ?? null,
    pageMeta: {
      title: meta?.title ?? '',
      description: meta?.description ?? '',
      siteName: meta?.siteName ?? '',
      publishedAt: meta?.publishedAt ?? '',
      hasVideo: meta?.hasVideo ?? false,
      hasAudio: meta?.hasAudio ?? false,
      fetchOk: meta?.ok ?? false,
    },
    today: new Date().toISOString().slice(0, 10),
  });
}

export const CAPTION_SYSTEM = `你是翻译助手。用户给一句人物照片图注（中文或英文），输出 JSON：
{"captionZh":"...","captionEn":"...","captionAr":"..."}
captionZh/captionEn 为忠实互译，captionAr 为阿拉伯语翻译（AI 初稿，会由人工校对）。只输出 JSON。`;

export function buildCaptionUser(caption) {
  return String(caption);
}
```

- [ ] **Step 5: 跑测试确认通过**

```bash
npm test
```

Expected: 全 PASS。

- [ ] **Step 6: Commit**

```bash
git add scripts/lib/llm.mjs scripts/lib/classify-prompt.mjs tests/llm.test.mjs
git commit -m "feat: add llm client and classification prompts"
```

---

### Task 5: fetch-meta（页面元数据抓取）

**Files:**
- Create: `scripts/lib/fetch-meta.mjs`
- Test: `tests/fetch-meta.test.mjs`

**Interfaces:**
- Produces:
  - `parseMeta(html: string): { title, description, siteName, publishedAt, hasVideo, hasAudio }`（纯函数，正则为 best-effort，抓取不全由 LLM 补偿）。
  - `fetchPageMeta(url: string, fetchImpl?): Promise<{ ok: boolean, error?: string, ...parseMeta 字段 }>`，15s 超时。

- [ ] **Step 1: 写失败测试**

```js
// tests/fetch-meta.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseMeta, fetchPageMeta } from '../scripts/lib/fetch-meta.mjs';

test('parseMeta 提取 og 标签', () => {
  const html = `<html><head>
    <title>Fallback Title</title>
    <meta property="og:title" content="OG Title">
    <meta property="og:site_name" content="CGTN">
    <meta property="article:published_time" content="2026-06-22T10:00:00Z">
    <meta property="og:type" content="video.other">
  </head></html>`;
  const m = parseMeta(html);
  assert.equal(m.title, 'OG Title');
  assert.equal(m.siteName, 'CGTN');
  assert.equal(m.publishedAt, '2026-06-22T10:00:00Z');
  assert.equal(m.hasVideo, true);
  assert.equal(m.hasAudio, false);
});

test('parseMeta 无 og 时回退 title 标签，识别播客音频', () => {
  const m = parseMeta('<title>Radio Show</title><audio src="x.mp3">');
  assert.equal(m.title, 'Radio Show');
  assert.equal(m.hasAudio, true);
});

test('fetchPageMeta 失败时返回 ok:false', async () => {
  const fakeFetch = async () => ({ ok: false, status: 403 });
  const m = await fetchPageMeta('https://x.com', fakeFetch);
  assert.equal(m.ok, false);
  assert.match(m.error, /403/);
});
```

- [ ] **Step 2: 跑测试确认失败**

```bash
node --test tests/fetch-meta.test.mjs
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 scripts/lib/fetch-meta.mjs**

```js
function pick(html, re) {
  return html.match(re)?.[1]?.trim() ?? '';
}

export function parseMeta(html) {
  return {
    title:
      pick(html, /<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']+)/i) ||
      pick(html, /<title[^>]*>([^<]+)<\/title>/i),
    description: pick(html, /<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']+)/i),
    siteName: pick(html, /<meta[^>]+property=["']og:site_name["'][^>]+content=["']([^"']+)/i),
    publishedAt: pick(
      html,
      /<meta[^>]+(?:property|name)=["'](?:article:published_time|publishdate|date)["'][^>]+content=["']([^"']+)/i,
    ),
    hasVideo: /og:type["'][^>]+content=["']video|<video[\s>]|youtube\.com\/embed|player\.bilibili\.com/i.test(html),
    hasAudio: /podcast|<audio[\s>]|radio\.cgtn\.com/i.test(html),
  };
}

export async function fetchPageMeta(url, fetchImpl = fetch) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 15000);
  try {
    const res = await fetchImpl(url, {
      signal: ctrl.signal,
      redirect: 'follow',
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; jodie-site-intake)' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const html = await res.text();
    return { ok: true, ...parseMeta(html) };
  } catch (err) {
    return { ok: false, error: String(err), ...parseMeta('') };
  } finally {
    clearTimeout(timer);
  }
}
```

- [ ] **Step 4: 跑测试确认通过**

```bash
npm test
```

Expected: 全 PASS。

- [ ] **Step 5: Commit**

```bash
git add scripts/lib/fetch-meta.mjs tests/fetch-meta.test.mjs
git commit -m "feat: add page metadata fetcher"
```

---

### Task 6: intake-pipeline 主脚本与 workflow A

**Files:**
- Create: `scripts/intake-pipeline.mjs`
- Create: `.github/workflows/intake-pipeline.yml`

**Interfaces:**
- Consumes: `fetchPageMeta`（Task 5）、`chatJson` + `CLASSIFY_SYSTEM`/`buildClassifyUser`/`CAPTION_SYSTEM`/`buildCaptionUser`（Task 4）、`serializeEntry`/`entryFileName`（Task 2）、`collectContentUrls`/`extractUrls`（Task 3）。
- Produces: 在 `intake/<ts>` 分支上提交条目并开 PR；供 Task 11 识别的约定：video 条目无 `cover` 字段且位于 `src/content/media/`。

- [ ] **Step 1: 实现 scripts/intake-pipeline.mjs**

环境变量：`GITHUB_TOKEN`、`INTAKE_PAT`（开 PR 专用）、`GITHUB_REPOSITORY`（owner/name，Actions 自动注入）、`INTAKE_BRANCH`、`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`。

```js
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fetchPageMeta } from './lib/fetch-meta.mjs';
import { chatJson } from './lib/llm.mjs';
import {
  CLASSIFY_SYSTEM,
  buildClassifyUser,
  CAPTION_SYSTEM,
  buildCaptionUser,
} from './lib/classify-prompt.mjs';
import { serializeEntry, entryFileName } from './lib/entry-writer.mjs';
import { collectContentUrls, extractUrls } from './lib/dedupe.mjs';

const repo = process.env.GITHUB_REPOSITORY;
const branch = process.env.INTAKE_BRANCH;
const llm = {
  baseUrl: process.env.LLM_BASE_URL,
  apiKey: process.env.LLM_API_KEY,
  model: process.env.LLM_MODEL,
};

async function ghApi(token, apiPath, { method = 'GET', body } = {}) {
  const res = await fetch(`https://api.github.com${apiPath}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`GitHub ${method} ${apiPath} → ${res.status}: ${await res.text()}`);
  return res.status === 204 ? null : res.json();
}

async function collectOpenPrUrls() {
  const prs = await ghApi(process.env.GITHUB_TOKEN, `/repos/${repo}/pulls?state=open&per_page=50`);
  const map = new Map(); // url → pr number
  for (const pr of prs) {
    if (!pr.head.ref.startsWith('intake/') || pr.head.ref === branch) continue;
    const files = await ghApi(process.env.GITHUB_TOKEN, `/repos/${repo}/pulls/${pr.number}/files?per_page=100`);
    for (const f of files) {
      if (!f.filename.startsWith('src/content/') || !f.filename.endsWith('.md') || f.status === 'removed') continue;
      const res = await fetch(f.raw_url, {
        headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` },
      });
      if (!res.ok) continue;
      for (const u of extractUrls(await res.text())) map.set(u, pr.number);
    }
  }
  return map;
}

function git(...args) {
  return execFileSync('git', args, { encoding: 'utf8' }).trim();
}

async function classify(url, typeOverride) {
  const meta = await fetchPageMeta(url);
  const out = await chatJson({
    ...llm,
    system: CLASSIFY_SYSTEM,
    user: buildClassifyUser({ url, meta, typeOverride }),
  });
  return { out, meta };
}

function writeEntry(collection, data) {
  const fileName = entryFileName(data.date, data.titleEn);
  const filePath = path.join('src/content', collection, fileName);
  fs.writeFileSync(filePath, serializeEntry(collection, data));
  return filePath;
}

const request = JSON.parse(fs.readFileSync('.intake/request.json', 'utf8'));
const results = [];
const newFiles = [];

const localUrls = collectContentUrls('src/content');
const openPrUrls = await collectOpenPrUrls();

if (request.kind === 'photo') {
  try {
    const captions = await chatJson({
      ...llm,
      system: CAPTION_SYSTEM,
      user: buildCaptionUser(request.caption),
    });
    const date = request.date || new Date().toISOString().slice(0, 10);
    const imageName = `${date}-${Date.now()}.jpg`;
    fs.mkdirSync('public/images/gallery', { recursive: true });
    fs.renameSync('.intake/photo.jpg', `public/images/gallery/${imageName}`);
    const filePath = writeEntry('gallery', {
      image: `/images/gallery/${imageName}`,
      captionEn: captions.captionEn,
      captionZh: captions.captionZh,
      captionAr: captions.captionAr,
      date,
    });
    newFiles.push(filePath, `public/images/gallery/${imageName}`);
    results.push({ title: captions.captionZh, url: '', verdict: 'gallery', reason: '照片投递', status: '成功' });
  } catch (err) {
    results.push({ title: request.caption ?? '照片', url: '', verdict: '-', reason: String(err), status: '失败' });
  }
} else {
  for (const url of request.urls) {
    if (localUrls.has(url)) {
      results.push({ title: '-', url, verdict: '-', reason: '已发布内容中存在', status: '跳过（重复）' });
      continue;
    }
    if (openPrUrls.has(url)) {
      results.push({ title: '-', url, verdict: '-', reason: `在 PR #${openPrUrls.get(url)} 待审`, status: '跳过（重复）' });
      continue;
    }
    try {
      const { out } = await classify(url, request.typeOverride);
      const collection = out.collection;
      if (!['publications', 'media', 'activities'].includes(collection)) {
        throw new Error(`LLM 返回未知集合: ${collection}`);
      }
      const data = { ...out, url };
      delete data.collection;
      delete data.reason;
      const filePath = writeEntry(collection, data);
      newFiles.push(filePath);
      results.push({ title: out.titleZh, url, verdict: `${collection}${out.type ? '/' + out.type : ''}`, reason: out.reason ?? '', status: '成功' });
    } catch (err) {
      results.push({ title: '-', url, verdict: '-', reason: String(err).slice(0, 200), status: '失败' });
    }
  }
}

fs.rmSync('.intake', { recursive: true, force: true });

const okCount = results.filter((r) => r.status === '成功').length;

if (newFiles.length > 0) {
  git('config', 'user.name', 'jodie-site-bot');
  git('config', 'user.email', 'bot@users.noreply.github.com');
  git('add', '-A');
  git('commit', '-m', `intake: ${okCount} new entr${okCount === 1 ? 'y' : 'ies'}`);
  git('push', 'origin', branch);
}

const rows = results
  .map(
    (r, i) =>
      `| ${i + 1} | ${String(r.title).replaceAll('|', '\\|')} | ${r.url ? `[链接](${r.url})` : '-'} | ${r.verdict} | ${String(r.reason).replaceAll('|', '\\|')} | ${r.status} |`,
  )
  .join('\n');

const body = `## 内容入库审核清单

| # | 标题 | 链接 | 判定 | 依据 | 状态 |
|---|------|------|------|------|------|
${rows}

${request.note ? `运营备注：${request.note}\n\n` : ''}---
审核守则（详见 docs/content-operations-sop.md）：
- 只在 Vercel 预览构建绿色时合并
- 小错直接在网页编辑文件；整条不该收的删除该文件
- 视频封面：等候选封面评论出现后，回复「封面 N」选定或「换一批」重截`;

if (newFiles.length > 0) {
  const pr = await ghApi(process.env.INTAKE_PAT, `/repos/${repo}/pulls`, {
    method: 'POST',
    body: {
      title: `内容入库 ${new Date().toISOString().slice(0, 16).replace('T', ' ')}（${okCount} 成功 / ${results.length} 条）`,
      head: branch,
      base: 'main',
      body,
    },
  });
  console.log(`PR created: ${pr.html_url}`);
} else {
  // 全部失败/跳过：仍留痕——把报告写进 step summary，分支保留 request.json 已被清理前的状态不可用时仅为空分支
  console.log('No entries created; skipping PR.');
}

if (process.env.GITHUB_STEP_SUMMARY) {
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, body);
}
```

注意：开 PR 用 `INTAKE_PAT`（PAT 触发的 pull_request 事件才会继续触发 cover-candidates 工作流；`GITHUB_TOKEN` 不会）。

- [ ] **Step 2: 创建 .github/workflows/intake-pipeline.yml**

```yaml
name: intake-pipeline
on:
  workflow_dispatch:
    inputs:
      branch:
        description: 'intake 分支名（intake/<ts>）'
        required: true
permissions:
  contents: write
  pull-requests: write
jobs:
  pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.branch }}
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - name: Run intake pipeline
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          INTAKE_PAT: ${{ secrets.INTAKE_PAT }}
          LLM_BASE_URL: ${{ secrets.LLM_BASE_URL }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          LLM_MODEL: ${{ secrets.LLM_MODEL }}
          INTAKE_BRANCH: ${{ inputs.branch }}
        run: node scripts/intake-pipeline.mjs
```

- [ ] **Step 3: 本地冒烟（不真实调 LLM/GitHub）**

```bash
node --check scripts/intake-pipeline.mjs && npm test
```

Expected: 语法检查通过、既有测试全 PASS（主脚本为集成胶水，单测覆盖其依赖的 lib；端到端验证在 Task 13）。

- [ ] **Step 4: Commit**

```bash
git add scripts/intake-pipeline.mjs .github/workflows/intake-pipeline.yml
git commit -m "feat: add intake pipeline script and workflow"
```

---

### Task 7: 鉴权（cookie 签发与校验）

**Files:**
- Create: `src/lib/admin/auth.mjs`
- Test: `tests/auth.test.mjs`

**Interfaces:**
- Produces:
  - `makeSessionCookie(secret: string, maxAgeSec?: number): string` — `<exp>.<hmac>`。
  - `verifySessionCookie(value: string|null, secret: string): boolean`。
  - `getCookie(request: Request, name: string): string|null`。
  - `isAuthed(request: Request, secret?: string): boolean`（默认读 `process.env.ADMIN_COOKIE_SECRET`）。

- [ ] **Step 1: 写失败测试**

```js
// tests/auth.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  makeSessionCookie,
  verifySessionCookie,
  getCookie,
  isAuthed,
} from '../src/lib/admin/auth.mjs';

const secret = 'test-secret';

test('签发后可校验通过', () => {
  const c = makeSessionCookie(secret);
  assert.equal(verifySessionCookie(c, secret), true);
});

test('篡改签名或 secret 错误不通过', () => {
  const c = makeSessionCookie(secret);
  assert.equal(verifySessionCookie(c.slice(0, -2) + 'xx', secret), false);
  assert.equal(verifySessionCookie(c, 'wrong'), false);
  assert.equal(verifySessionCookie(null, secret), false);
  assert.equal(verifySessionCookie('garbage', secret), false);
});

test('过期 cookie 不通过', () => {
  const c = makeSessionCookie(secret, -10);
  assert.equal(verifySessionCookie(c, secret), false);
});

test('getCookie 解析与 isAuthed', () => {
  const c = makeSessionCookie(secret);
  const req = new Request('https://x/admin', { headers: { cookie: `a=1; admin_session=${c}` } });
  assert.equal(getCookie(req, 'admin_session'), c);
  assert.equal(isAuthed(req, secret), true);
  const anon = new Request('https://x/admin');
  assert.equal(isAuthed(anon, secret), false);
});
```

- [ ] **Step 2: 跑测试确认失败**

```bash
node --test tests/auth.test.mjs
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 src/lib/admin/auth.mjs**

```js
import crypto from 'node:crypto';

function sign(value, secret) {
  return crypto.createHmac('sha256', secret).update(value).digest('hex');
}

export function makeSessionCookie(secret, maxAgeSec = 7 * 24 * 3600) {
  const exp = Math.floor(Date.now() / 1000) + maxAgeSec;
  return `${exp}.${sign(String(exp), secret)}`;
}

export function verifySessionCookie(value, secret) {
  if (!value || !secret) return false;
  const dot = value.indexOf('.');
  if (dot < 1) return false;
  const exp = value.slice(0, dot);
  const sig = value.slice(dot + 1);
  const expected = sign(exp, secret);
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return false;
  return Number(exp) > Date.now() / 1000;
}

export function getCookie(request, name) {
  const header = request.headers.get('cookie') ?? '';
  for (const part of header.split(';')) {
    const eq = part.indexOf('=');
    if (eq < 0) continue;
    if (part.slice(0, eq).trim() === name) return part.slice(eq + 1).trim();
  }
  return null;
}

export function isAuthed(request, secret = process.env.ADMIN_COOKIE_SECRET) {
  return verifySessionCookie(getCookie(request, 'admin_session'), secret);
}
```

- [ ] **Step 4: 跑测试确认通过**

```bash
npm test
```

Expected: 全 PASS。

- [ ] **Step 5: Commit**

```bash
git add src/lib/admin/auth.mjs tests/auth.test.mjs
git commit -m "feat: add admin session cookie auth"
```

---

### Task 8: GitHub 门卫客户端（Vercel 侧）

**Files:**
- Create: `src/lib/admin/github.mjs`
- Test: `tests/github-client.test.mjs`

**Interfaces:**
- Consumes: env `GH_INTAKE_TOKEN`、`GH_REPO`。
- Produces（均可注入 `fetchImpl` 便于测试）:
  - `createBranch({ token, repo, branch, from?, fetchImpl? }): Promise<void>`
  - `putFile({ token, repo, branch, path, content, message, encoding?, fetchImpl? }): Promise<void>`（`encoding: 'base64'` 时 content 视为已编码，用于照片二进制）
  - `dispatchWorkflow({ token, repo, workflow, ref, inputs, fetchImpl? }): Promise<void>`
  - `getIntakeStatus({ token, repo, fetchImpl? }): Promise<{ runs: Array, prs: Array }>`

- [ ] **Step 1: 写失败测试**

```js
// tests/github-client.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createBranch, putFile, dispatchWorkflow, getIntakeStatus } from '../src/lib/admin/github.mjs';

function recorder(handlers) {
  const calls = [];
  const fetchImpl = async (url, opts = {}) => {
    calls.push({ url, opts });
    const key = `${opts.method ?? 'GET'} ${url}`;
    for (const [pattern, responder] of handlers) {
      if (key.includes(pattern)) return responder();
    }
    return { ok: true, status: 200, json: async () => ({}), text: async () => '' };
  };
  return { calls, fetchImpl };
}

test('createBranch 先取 main 的 sha 再建 ref', async () => {
  const { calls, fetchImpl } = recorder([
    ['GET https://api.github.com/repos/o/r/git/ref/heads/main', async () => ({
      ok: true, status: 200, json: async () => ({ object: { sha: 'abc123' } }),
    })],
    ['POST https://api.github.com/repos/o/r/git/refs', async () => ({ ok: true, status: 201, json: async () => ({}) })],
  ]);
  await createBranch({ token: 't', repo: 'o/r', branch: 'intake/1', fetchImpl });
  assert.equal(calls.length, 2);
  assert.equal(JSON.parse(calls[1].opts.body).sha, 'abc123');
  assert.equal(JSON.parse(calls[1].opts.body).ref, 'refs/heads/intake/1');
});

test('putFile 将 utf8 内容转 base64', async () => {
  const { calls, fetchImpl } = recorder([]);
  await putFile({ token: 't', repo: 'o/r', branch: 'b', path: '.intake/request.json', content: '{"a":1}', message: 'm', fetchImpl });
  const body = JSON.parse(calls[0].opts.body);
  assert.equal(Buffer.from(body.content, 'base64').toString('utf8'), '{"a":1}');
  assert.equal(body.branch, 'b');
});

test('dispatchWorkflow 带 inputs', async () => {
  const { calls, fetchImpl } = recorder([]);
  await dispatchWorkflow({ token: 't', repo: 'o/r', workflow: 'intake-pipeline.yml', ref: 'intake/1', inputs: { branch: 'intake/1' }, fetchImpl });
  assert.match(calls[0].url, /actions\/workflows\/intake-pipeline\.yml\/dispatches/);
  assert.equal(JSON.parse(calls[0].opts.body).ref, 'intake/1');
});

test('getIntakeStatus 过滤 intake PR 并映射运行状态', async () => {
  const { fetchImpl } = recorder([
    ['workflows/intake-pipeline.yml/runs', async () => ({
      ok: true, status: 200,
      json: async () => ({ workflow_runs: [{ head_branch: 'intake/1', status: 'completed', conclusion: 'success', html_url: 'https://run', created_at: '2026-08-09' }] }),
    })],
    ['GET https://api.github.com/repos/o/r/pulls', async () => ({
      ok: true, status: 200,
      json: async () => ([
        { number: 5, head: { ref: 'intake/1' }, title: 'PR5', state: 'open', merged_at: null, html_url: 'https://pr5' },
        { number: 4, head: { ref: 'feature/x' }, title: 'other', state: 'open', merged_at: null, html_url: 'https://pr4' },
      ]),
    })],
  ]);
  const s = await getIntakeStatus({ token: 't', repo: 'o/r', fetchImpl });
  assert.equal(s.runs[0].conclusion, 'success');
  assert.equal(s.prs.length, 1);
  assert.equal(s.prs[0].number, 5);
});

test('GitHub 报错时抛出带状态码的错误', async () => {
  const fetchImpl = async () => ({ ok: false, status: 422, text: async () => 'Validation Failed' });
  await assert.rejects(
    putFile({ token: 't', repo: 'o/r', branch: 'b', path: 'p', content: 'c', message: 'm', fetchImpl }),
    /422/,
  );
});
```

- [ ] **Step 2: 跑测试确认失败**

```bash
node --test tests/github-client.test.mjs
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 src/lib/admin/github.mjs**

```js
const API = 'https://api.github.com';

async function ghApi(token, path, { method = 'GET', body, fetchImpl = fetch } = {}) {
  const res = await fetchImpl(`${API}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`GitHub ${method} ${path} → ${res.status}: ${await res.text()}`);
  return res.status === 204 ? null : res.json();
}

export async function createBranch({ token, repo, branch, from = 'main', fetchImpl = fetch }) {
  const ref = await ghApi(token, `/repos/${repo}/git/ref/heads/${from}`, { fetchImpl });
  await ghApi(token, `/repos/${repo}/git/refs`, {
    method: 'POST',
    body: { ref: `refs/heads/${branch}`, sha: ref.object.sha },
    fetchImpl,
  });
}

export async function putFile({ token, repo, branch, path, content, message, encoding = 'utf8', fetchImpl = fetch }) {
  const b64 = encoding === 'base64' ? content : Buffer.from(content, 'utf8').toString('base64');
  await ghApi(token, `/repos/${repo}/contents/${path}`, {
    method: 'PUT',
    body: { message, content: b64, branch },
    fetchImpl,
  });
}

export async function dispatchWorkflow({ token, repo, workflow, ref, inputs, fetchImpl = fetch }) {
  await ghApi(token, `/repos/${repo}/actions/workflows/${workflow}/dispatches`, {
    method: 'POST',
    body: { ref, inputs },
    fetchImpl,
  });
}

export async function getIntakeStatus({ token, repo, fetchImpl = fetch }) {
  const runs = await ghApi(token, `/repos/${repo}/actions/workflows/intake-pipeline.yml/runs?per_page=10`, { fetchImpl });
  const prs = await ghApi(token, `/repos/${repo}/pulls?state=all&per_page=20&sort=updated&direction=desc`, { fetchImpl });
  return {
    runs: runs.workflow_runs.map((r) => ({
      branch: r.head_branch,
      status: r.status,
      conclusion: r.conclusion,
      url: r.html_url,
      createdAt: r.created_at,
    })),
    prs: prs
      .filter((p) => p.head.ref.startsWith('intake/'))
      .map((p) => ({
        number: p.number,
        branch: p.head.ref,
        title: p.title,
        state: p.state,
        merged: Boolean(p.merged_at),
        url: p.html_url,
      })),
  };
}
```

- [ ] **Step 4: 跑测试确认通过**

```bash
npm test
```

Expected: 全 PASS。

- [ ] **Step 5: Commit**

```bash
git add src/lib/admin/github.mjs tests/github-client.test.mjs
git commit -m "feat: add github gatekeeper client"
```

---

### Task 9: API 端点（login / intake links / intake photo / status）

**Files:**
- Create: `src/pages/api/login.ts`
- Create: `src/pages/api/intake/links.ts`
- Create: `src/pages/api/intake/photo.ts`
- Create: `src/pages/api/status.ts`

**Interfaces:**
- Consumes: `isAuthed`/`makeSessionCookie`（Task 7）、`createBranch`/`putFile`/`dispatchWorkflow`/`getIntakeStatus`（Task 8）。
- Produces（供 Task 10 前端调用）:
  - `POST /api/login`（form: `password`）→ 303 回 `/admin`（失败带 `?error=1`）
  - `POST /api/intake/links`（JSON: `{ urls: string[], typeOverride?: string|null, note?: string }`）→ `{ ok: true, branch }`；401/400 见代码
  - `POST /api/intake/photo`（multipart: `photo`、`caption`、`date?`）→ `{ ok: true, branch }`
  - `GET /api/status` → `{ runs, prs }`

- [ ] **Step 1: src/pages/api/login.ts**

```ts
import type { APIRoute } from 'astro';
import crypto from 'node:crypto';
import { makeSessionCookie } from '../../lib/admin/auth.mjs';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  const form = await request.formData();
  const password = String(form.get('password') ?? '');
  const expected = process.env.ADMIN_PASSWORD ?? '';
  const ok =
    expected.length > 0 &&
    password.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(password), Buffer.from(expected));
  if (!ok) {
    return new Response(null, { status: 303, headers: { Location: '/admin?error=1' } });
  }
  const cookie = makeSessionCookie(process.env.ADMIN_COOKIE_SECRET ?? '');
  return new Response(null, {
    status: 303,
    headers: {
      Location: '/admin',
      'Set-Cookie': `admin_session=${cookie}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${7 * 24 * 3600}`,
    },
  });
};
```

- [ ] **Step 2: src/pages/api/intake/links.ts**

```ts
import type { APIRoute } from 'astro';
import { isAuthed } from '../../../lib/admin/auth.mjs';
import { createBranch, putFile, dispatchWorkflow } from '../../../lib/admin/github.mjs';

export const prerender = false;

const TYPE_OVERRIDES = new Set(['article', 'video', 'interview', 'activity']);

export const POST: APIRoute = async ({ request }) => {
  if (!isAuthed(request)) return new Response('Unauthorized', { status: 401 });

  let body;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: '请求体须为 JSON' }, { status: 400 });
  }
  const urls = (Array.isArray(body?.urls) ? body.urls : [])
    .map((u: unknown) => String(u).trim())
    .filter((u: string) => /^https?:\/\//.test(u));
  if (urls.length === 0) return Response.json({ error: '没有有效 URL' }, { status: 400 });
  if (urls.length > 10) return Response.json({ error: '单次最多 10 条' }, { status: 400 });

  const branch = `intake/${Date.now()}`;
  const gh = { token: process.env.GH_INTAKE_TOKEN ?? '', repo: process.env.GH_REPO ?? '' };
  const typeOverride = TYPE_OVERRIDES.has(body?.typeOverride) ? body.typeOverride : null;
  const note = String(body?.note ?? '').slice(0, 500);

  await createBranch({ ...gh, branch });
  await putFile({
    ...gh,
    branch,
    path: '.intake/request.json',
    content: JSON.stringify(
      { kind: 'links', urls, typeOverride, note, submittedAt: new Date().toISOString() },
      null,
      2,
    ),
    message: `intake: ${urls.length} link(s)`,
  });
  await dispatchWorkflow({ ...gh, workflow: 'intake-pipeline.yml', ref: branch, inputs: { branch } });
  return Response.json({ ok: true, branch });
};
```

- [ ] **Step 3: src/pages/api/intake/photo.ts**

```ts
import type { APIRoute } from 'astro';
import { isAuthed } from '../../../lib/admin/auth.mjs';
import { createBranch, putFile, dispatchWorkflow } from '../../../lib/admin/github.mjs';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  if (!isAuthed(request)) return new Response('Unauthorized', { status: 401 });

  const form = await request.formData();
  const photo = form.get('photo');
  const caption = String(form.get('caption') ?? '').trim();
  const date = String(form.get('date') ?? '').trim();
  if (!(photo instanceof File) || photo.size === 0) {
    return Response.json({ error: '缺少照片文件' }, { status: 400 });
  }
  if (!caption) return Response.json({ error: '缺少图注' }, { status: 400 });
  if (photo.size > 4 * 1024 * 1024) {
    return Response.json({ error: '照片超过 4MB，请压缩后重试' }, { status: 400 });
  }

  const branch = `intake/${Date.now()}`;
  const gh = { token: process.env.GH_INTAKE_TOKEN ?? '', repo: process.env.GH_REPO ?? '' };
  const b64 = Buffer.from(await photo.arrayBuffer()).toString('base64');

  await createBranch({ ...gh, branch });
  await putFile({
    ...gh, branch, path: '.intake/photo.jpg', content: b64, encoding: 'base64', message: 'intake: photo',
  });
  await putFile({
    ...gh,
    branch,
    path: '.intake/request.json',
    content: JSON.stringify(
      { kind: 'photo', caption, date: /^\d{4}-\d{2}-\d{2}$/.test(date) ? date : null, submittedAt: new Date().toISOString() },
      null,
      2,
    ),
    message: 'intake: photo request',
  });
  await dispatchWorkflow({ ...gh, workflow: 'intake-pipeline.yml', ref: branch, inputs: { branch } });
  return Response.json({ ok: true, branch });
};
```

- [ ] **Step 4: src/pages/api/status.ts**

```ts
import type { APIRoute } from 'astro';
import { isAuthed } from '../../lib/admin/auth.mjs';
import { getIntakeStatus } from '../../lib/admin/github.mjs';

export const prerender = false;

export const GET: APIRoute = async ({ request }) => {
  if (!isAuthed(request)) return new Response('Unauthorized', { status: 401 });
  const data = await getIntakeStatus({
    token: process.env.GH_INTAKE_TOKEN ?? '',
    repo: process.env.GH_REPO ?? '',
  });
  return Response.json(data);
};
```

- [ ] **Step 5: 验证构建与类型**

```bash
npm run build && npx astro check && npm test
```

Expected: 全绿。

- [ ] **Step 6: Commit**

```bash
git add src/pages/api/
git commit -m "feat: add admin api endpoints"
```

---

### Task 10: /admin 页面（登录 + 两个表单 + 最近投递状态区）

**Files:**
- Create: `src/pages/admin.astro`

**Interfaces:**
- Consumes: `isAuthed`（Task 7）、`/api/login`、`/api/intake/links`、`/api/intake/photo`、`/api/status`（Task 9）。
- Produces: 运营唯一入口页面；`noindex`；不加导航链接。

- [ ] **Step 1: 实现 src/pages/admin.astro**

```astro
---
import '../styles/global.css';
import { isAuthed } from '../lib/admin/auth.mjs';

export const prerender = false;

const authed = isAuthed(Astro.request);
const loginError = Astro.url.searchParams.get('error') === '1';
---

<!doctype html>
<html lang="zh" dir="ltr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="noindex, nofollow" />
    <title>内容投递后台</title>
  </head>
  <body class="bg-neutral-50 text-neutral-900 antialiased">
    <main class="mx-auto max-w-2xl px-4 py-10">
      <h1 class="font-serif text-2xl font-bold">内容投递后台</h1>

      {!authed && (
        <form method="post" action="/api/login" class="mt-8 space-y-4">
          {loginError && <p class="text-sm text-red-700">密码错误，请重试。</p>}
          <label class="block text-sm font-medium">
            密码
            <input
              type="password"
              name="password"
              required
              class="mt-1 block w-full rounded border border-neutral-300 px-3 py-2"
            />
          </label>
          <button type="submit" class="rounded bg-teal-700 px-4 py-2 text-white">登录</button>
        </form>
      )}

      {authed && (
        <div class="mt-8 space-y-10">
          <section>
            <h2 class="font-serif text-lg font-bold">投递链接</h2>
            <p class="mt-1 text-sm text-neutral-600">一行一个 URL，单次最多 10 条。提交后系统自动解析、翻译并生成审核 PR。</p>
            <form id="links-form" class="mt-3 space-y-3">
              <textarea
                id="urls"
                rows="5"
                required
                placeholder="https://..."
                class="block w-full rounded border border-neutral-300 px-3 py-2 text-sm"
              ></textarea>
              <label class="block text-sm font-medium">
                类型（不确定就保持「自动判断」）
                <select id="type-override" class="mt-1 block w-full rounded border border-neutral-300 px-3 py-2 text-sm">
                  <option value="">自动判断</option>
                  <option value="article">文章</option>
                  <option value="video">视频</option>
                  <option value="interview">采访（含音频）</option>
                  <option value="activity">活动</option>
                </select>
              </label>
              <label class="block text-sm font-medium">
                备注（可选，会给审核人看）
                <input id="note" type="text" class="mt-1 block w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
              </label>
              <button type="submit" class="rounded bg-teal-700 px-4 py-2 text-white">提交链接</button>
              <p id="links-result" class="text-sm"></p>
            </form>
          </section>

          <section>
            <h2 class="font-serif text-lg font-bold">投递照片（More about Jodie）</h2>
            <p class="mt-1 text-sm text-neutral-600">照片会自动压缩；图注填中文或英文均可，其余语言自动补译。</p>
            <form id="photo-form" class="mt-3 space-y-3">
              <input id="photo" type="file" accept="image/*" required class="block w-full text-sm" />
              <label class="block text-sm font-medium">
                图注
                <input id="caption" type="text" required class="mt-1 block w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
              </label>
              <label class="block text-sm font-medium">
                日期（可选）
                <input id="photo-date" type="date" class="mt-1 block w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
              </label>
              <button type="submit" class="rounded bg-teal-700 px-4 py-2 text-white">提交照片</button>
              <p id="photo-result" class="text-sm"></p>
            </form>
          </section>

          <section>
            <h2 class="font-serif text-lg font-bold">最近投递</h2>
            <div id="status-list" class="mt-3 text-sm text-neutral-600">加载中…</div>
          </section>
        </div>
      )}
    </main>

    <script>
      const $ = (id) => document.getElementById(id);

      async function compressImage(file) {
        const bitmap = await createImageBitmap(file);
        const scale = Math.min(1, 2000 / Math.max(bitmap.width, bitmap.height));
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(bitmap.width * scale);
        canvas.height = Math.round(bitmap.height * scale);
        canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height);
        return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.85));
      }

      $('links-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const result = $('links-result');
        result.textContent = '提交中…';
        result.className = 'text-sm text-neutral-600';
        const urls = $('urls').value.split('\n').map((s) => s.trim()).filter(Boolean);
        try {
          const res = await fetch('/api/intake/links', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              urls,
              typeOverride: $('type-override').value || null,
              note: $('note').value,
            }),
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
          result.textContent = `已受理（分支 ${data.branch}），处理结果见下方「最近投递」，数分钟后生成审核 PR。`;
          result.className = 'text-sm text-teal-700';
          $('urls').value = '';
          loadStatus();
        } catch (err) {
          result.textContent = `提交失败：${err.message}`;
          result.className = 'text-sm text-red-700';
        }
      });

      $('photo-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const result = $('photo-result');
        result.textContent = '压缩并上传中…';
        result.className = 'text-sm text-neutral-600';
        try {
          const file = $('photo').files[0];
          if (!file) throw new Error('请选择照片');
          const blob = await compressImage(file);
          if (blob.size > 4 * 1024 * 1024) throw new Error('压缩后仍超过 4MB，请换一张更小的图');
          const form = new FormData();
          form.append('photo', blob, 'photo.jpg');
          form.append('caption', $('caption').value);
          if ($('photo-date').value) form.append('date', $('photo-date').value);
          const res = await fetch('/api/intake/photo', { method: 'POST', body: form });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
          result.textContent = `已受理（分支 ${data.branch}），处理结果见下方「最近投递」。`;
          result.className = 'text-sm text-teal-700';
          loadStatus();
        } catch (err) {
          result.textContent = `提交失败：${err.message}`;
          result.className = 'text-sm text-red-700';
        }
      });

      function renderStatus(data) {
        const el = $('status-list');
        if (!el) return;
        const items = [];
        for (const pr of data.prs) {
          const state = pr.merged ? '已合并' : pr.state === 'open' ? '待审核' : '已关闭';
          items.push(`<li>PR <a class="text-teal-700 underline" href="${pr.url}" target="_blank" rel="noopener">#${pr.number}</a> ${pr.title} — ${state}</li>`);
        }
        for (const run of data.runs) {
          if (data.prs.some((p) => p.branch === run.branch)) continue;
          const state = run.status !== 'completed' ? '处理中' : run.conclusion === 'success' ? '已完成' : '失败';
          items.push(`<li>${run.branch} — ${state}（<a class="text-teal-700 underline" href="${run.url}" target="_blank" rel="noopener">日志</a>）</li>`);
        }
        el.innerHTML = items.length ? `<ul class="list-disc space-y-1 ps-5">${items.join('')}</ul>` : '暂无投递记录。';
      }

      async function loadStatus() {
        try {
          const res = await fetch('/api/status');
          if (res.ok) renderStatus(await res.json());
        } catch { /* 状态区失败不影响投递 */ }
      }

      loadStatus();
      setInterval(loadStatus, 30000);
    </script>
  </body>
</html>
```

- [ ] **Step 2: 验证构建与类型**

```bash
npm run build && npx astro check
```

Expected: 全绿。`dist/admin/index.html` 不存在（admin 为按需渲染路由）属正常。

- [ ] **Step 3: 本地手动验证（dev server）**

```bash
cat > .env <<'EOF'
ADMIN_PASSWORD=test-pw
ADMIN_COOKIE_SECRET=test-secret
GH_INTAKE_TOKEN=dummy
GH_REPO=owner/repo
EOF
npm run dev
```

- 打开 `http://localhost:4321/admin` → 显示密码框；错误密码 → 「密码错误」；`test-pw` → 进入后台三区块。
- 新开无痕窗口直接 POST `/api/intake/links`（无 cookie）→ 401。

验证后删除 `.env`。

- [ ] **Step 4: Commit**

```bash
git add src/pages/admin.astro
git commit -m "feat: add admin intake page"
```

---

### Task 11: 视频候选封面（截帧脚本 + workflow B）

**Files:**
- Create: `scripts/lib/cover-frames.mjs`（纯函数部分）
- Create: `scripts/extract-cover-frames.mjs`（CLI 入口）
- Create: `scripts/cover-candidates.mjs`（PR 扫描 + 汇总评论）
- Create: `.github/workflows/cover-candidates.yml`
- Test: `tests/cover-frames.test.mjs`

**Interfaces:**
- Produces:
  - `FRACTION_SETS: number[][]`、`youtubeId(url: string): string|null`、`youtubeThumbs(id: string): string[]`（Task 11/12 共用）
  - `parseVideoEntry(md: string): { url: string, hasCover: boolean } | null`（type 为 video 才返回）
  - 汇总评论标记：`<!-- cover-candidates\n{...JSON...}\n-->`，JSON 形状 `{ "items": [{ "n": 1, "slug": "...", "path": ".cover-candidates/<slug>/1.jpg", "chosen": false }], "round": 0 }`——Task 12 靠它定位候选。

- [ ] **Step 1: 写失败测试**

```js
// tests/cover-frames.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { FRACTION_SETS, youtubeId, youtubeThumbs, parseVideoEntry } from '../scripts/lib/cover-frames.mjs';

test('youtubeId 识别常见 URL 形态', () => {
  assert.equal(youtubeId('https://www.youtube.com/watch?v=abc123XYZ_-'), 'abc123XYZ_-');
  assert.equal(youtubeId('https://youtu.be/abc123XYZ_-'), 'abc123XYZ_-');
  assert.equal(youtubeId('https://example.com/x'), null);
});

test('youtubeThumbs 返回 4 张候选', () => {
  const t = youtubeThumbs('abc123XYZ_-');
  assert.equal(t.length, 4);
  assert.ok(t[0].includes('maxresdefault'));
});

test('FRACTION_SETS 三组轮换', () => {
  assert.equal(FRACTION_SETS.length, 3);
  assert.deepEqual(FRACTION_SETS[0], [0.1, 0.3, 0.5, 0.7]);
});

test('parseVideoEntry 识别 video 与 cover 状态', () => {
  const video = '---\ntype: "video"\nurl: "https://x.com/v"\n---\n';
  assert.deepEqual(parseVideoEntry(video), { url: 'https://x.com/v', hasCover: false });
  const withCover = '---\ntype: "video"\nurl: "https://x.com/v"\ncover: "/images/media/a.jpg"\n---\n';
  assert.equal(parseVideoEntry(withCover).hasCover, true);
  const interview = '---\ntype: "interview"\nurl: "https://x.com/v"\n---\n';
  assert.equal(parseVideoEntry(interview), null);
});
```

- [ ] **Step 2: 跑测试确认失败**

```bash
node --test tests/cover-frames.test.mjs
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 scripts/lib/cover-frames.mjs**

```js
export const FRACTION_SETS = [
  [0.1, 0.3, 0.5, 0.7],
  [0.05, 0.25, 0.45, 0.65],
  [0.15, 0.35, 0.55, 0.75],
];

export function youtubeId(url) {
  const m =
    String(url).match(/youtube\.com\/watch\?[^ ]*v=([\w-]{11})/) ??
    String(url).match(/youtu\.be\/([\w-]{11})/);
  return m ? m[1] : null;
}

export function youtubeThumbs(id) {
  return [
    `https://i.ytimg.com/vi/${id}/maxresdefault.jpg`,
    `https://i.ytimg.com/vi/${id}/hq1.jpg`,
    `https://i.ytimg.com/vi/${id}/hq2.jpg`,
    `https://i.ytimg.com/vi/${id}/hq3.jpg`,
  ];
}

export function parseVideoEntry(md) {
  if (!/^type:\s*"video"/m.test(md)) return null;
  const url = md.match(/^url:\s*"([^"]+)"/m)?.[1];
  if (!url) return null;
  return { url, hasCover: /^cover:/m.test(md) };
}
```

- [ ] **Step 4: 实现 scripts/extract-cover-frames.mjs**（CLI：`node scripts/extract-cover-frames.mjs <url> <outdir> [round]`）

```js
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { FRACTION_SETS, youtubeId, youtubeThumbs } from './lib/cover-frames.mjs';

const [url, outdir, roundArg] = process.argv.slice(2);
if (!url || !outdir) {
  console.error('usage: node scripts/extract-cover-frames.mjs <url> <outdir> [round]');
  process.exit(1);
}
const round = Number(roundArg ?? 0) % FRACTION_SETS.length;
fs.mkdirSync(outdir, { recursive: true });

async function download(src, dest) {
  const res = await fetch(src, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  if (!res.ok) throw new Error(`download ${src} → ${res.status}`);
  fs.writeFileSync(dest, Buffer.from(await res.arrayBuffer()));
}

const yt = youtubeId(url);
if (yt) {
  const thumbs = youtubeThumbs(yt);
  for (let i = 0; i < thumbs.length; i++) {
    await download(thumbs[i], path.join(outdir, `${i + 1}.jpg`));
  }
} else {
  const streamUrl = execFileSync('yt-dlp', ['-f', 'best[ext=mp4]/best', '-g', url], { encoding: 'utf8' }).trim().split('\n')[0];
  const probe = execFileSync('ffprobe', ['-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', streamUrl], { encoding: 'utf8' }).trim();
  const duration = Number(probe);
  if (!Number.isFinite(duration) || duration <= 0) throw new Error(`无法获取视频时长: ${url}`);
  const fractions = FRACTION_SETS[round];
  for (let i = 0; i < fractions.length; i++) {
    const t = Math.max(0, Math.floor(duration * fractions[i]));
    execFileSync('ffmpeg', ['-y', '-ss', String(t), '-i', streamUrl, '-frames:v', '1', '-q:v', '3', path.join(outdir, `${i + 1}.jpg`)], { stdio: 'pipe' });
  }
}
console.log(`candidates written to ${outdir} (round ${round})`);
```

- [ ] **Step 5: 实现 scripts/cover-candidates.mjs**

环境变量：`GITHUB_TOKEN`、`GITHUB_REPOSITORY`、`PR_NUMBER`。

```js
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { parseVideoEntry } from './lib/cover-frames.mjs';

const repo = process.env.GITHUB_REPOSITORY;
const prNumber = process.env.PR_NUMBER;
const token = process.env.GITHUB_TOKEN;
const MARKER = '<!-- cover-candidates';

async function ghApi(apiPath, { method = 'GET', body } = {}) {
  const res = await fetch(`https://api.github.com${apiPath}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`GitHub ${method} ${apiPath} → ${res.status}: ${await res.text()}`);
  return res.json();
}

function git(...args) {
  return execFileSync('git', args, { encoding: 'utf8' }).trim();
}

// 1. 找出 PR 相对 main 新增/修改的 media 条目
const base = git('merge-base', 'origin/main', 'HEAD');
const changed = git('diff', '--name-only', '--diff-filter=AM', base, 'HEAD', '--', 'src/content/media')
  .split('\n')
  .filter(Boolean);

// 2. 逐条解析，跳过已有 cover 或已有候选目录的
const pending = [];
for (const file of changed) {
  const md = fs.readFileSync(file, 'utf8');
  const info = parseVideoEntry(md);
  if (!info || info.hasCover) continue;
  const slug = path.basename(file, '.md');
  if (fs.existsSync(path.join('.cover-candidates', slug))) continue;
  pending.push({ slug, url: info.url });
}

// 3. 截帧
const failures = [];
for (const p of pending) {
  try {
    execFileSync('node', ['scripts/extract-cover-frames.mjs', p.url, path.join('.cover-candidates', p.slug), '0'], { stdio: 'inherit' });
  } catch (err) {
    failures.push({ slug: p.slug, reason: String(err).slice(0, 200) });
  }
}

// 4. 汇总所有候选目录（含历史批次的），统一编号
const items = [];
if (fs.existsSync('.cover-candidates')) {
  let n = 0;
  for (const slug of fs.readdirSync('.cover-candidates').sort()) {
    const dir = path.join('.cover-candidates', slug);
    for (const f of fs.readdirSync(dir).sort()) {
      if (!f.endsWith('.jpg')) continue;
      n += 1;
      items.push({ n, slug, path: `${dir}/${f}`, chosen: false });
    }
  }
}

if (items.length === 0 && failures.length === 0) {
  console.log('no video entries need covers');
  process.exit(0);
}

// 5. 提交候选图
git('config', 'user.name', 'jodie-site-bot');
git('config', 'user.email', 'bot@users.noreply.github.com');
git('add', '.cover-candidates');
if (git('status', '--porcelain')) {
  git('commit', '-m', 'chore: add cover candidates');
  git('push');
}

// 6. 发/更新汇总评论
const branch = git('rev-parse', '--abbrev-ref', 'HEAD');
const lines = items.map(
  (it) => `**${it.n}.** \`${it.slug}\`\n\n![候选 ${it.n}](https://github.com/${repo}/blob/${branch}/${it.path}?raw=true)`,
);
const failLines = failures.map((f) => `- \`${f.slug}\`：候选生成失败（${f.reason}），可回复「换一批」重试`);
const body = `${MARKER}\n${JSON.stringify({ items, round: 0 })}\n-->

## 视频候选封面

共 ${items.length} 张候选。回复「封面 N」选定第 N 张；回复「换一批」为未选定的视频重新截取。

${lines.join('\n\n')}
${failLines.length ? `\n### 失败\n${failLines.join('\n')}` : ''}`;

const comments = await ghApi(`/repos/${repo}/issues/${prNumber}/comments?per_page=100`);
const existing = comments.find((c) => c.body?.includes(MARKER));
if (existing) {
  await ghApi(`/repos/${repo}/issues/comments/${existing.id}`, { method: 'PATCH', body: { body } });
} else {
  await ghApi(`/repos/${repo}/issues/${prNumber}/comments`, { method: 'POST', body: { body } });
}
console.log(`candidates comment updated: ${items.length} items`);
```

- [ ] **Step 6: 创建 .github/workflows/cover-candidates.yml**

```yaml
name: cover-candidates
on:
  pull_request:
    types: [opened, synchronize]
permissions:
  contents: write
  issues: write
jobs:
  candidates:
    if: startsWith(github.head_ref, 'intake/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - name: Install yt-dlp
        run: pip install yt-dlp
      - name: Generate cover candidates
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: node scripts/cover-candidates.mjs
```

注意：ubuntu-latest 已预装 ffmpeg，无需安装。

- [ ] **Step 7: 本地验证**

```bash
node --check scripts/extract-cover-frames.mjs && node --check scripts/cover-candidates.mjs && npm test
```

Expected: 语法检查通过、测试全 PASS。

- [ ] **Step 8: Commit**

```bash
git add scripts/lib/cover-frames.mjs scripts/extract-cover-frames.mjs scripts/cover-candidates.mjs .github/workflows/cover-candidates.yml tests/cover-frames.test.mjs
git commit -m "feat: add video cover candidate generation"
```

---

### Task 12: 封面评论指令（workflow C）

**Files:**
- Create: `scripts/lib/cover-command-parse.mjs`
- Create: `scripts/cover-apply.mjs`
- Create: `.github/workflows/cover-command.yml`
- Test: `tests/cover-command-parse.test.mjs`

**Interfaces:**
- Consumes: Task 11 的汇总评论标记 JSON、`FRACTION_SETS`、`extract-cover-frames.mjs`。
- Produces: `parseCoverCommand(body: string): { action: 'select', n: number } | { action: 'regen' } | null`。

- [ ] **Step 1: 写失败测试**

```js
// tests/cover-command-parse.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseCoverCommand } from '../scripts/lib/cover-command-parse.mjs';

test('选定指令的各种写法', () => {
  assert.deepEqual(parseCoverCommand('封面 2'), { action: 'select', n: 2 });
  assert.deepEqual(parseCoverCommand('用第3张'), { action: 'select', n: 3 });
  assert.deepEqual(parseCoverCommand('封面#5'), { action: 'select', n: 5 });
});

test('重截指令', () => {
  assert.deepEqual(parseCoverCommand('换一批'), { action: 'regen' });
  assert.deepEqual(parseCoverCommand('这几张都不行，重新生成'), { action: 'regen' });
});

test('无关评论返回 null', () => {
  assert.equal(parseCoverCommand('这个标题翻译得不对'), null);
});
```

- [ ] **Step 2: 跑测试确认失败**

```bash
node --test tests/cover-command-parse.test.mjs
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 scripts/lib/cover-command-parse.mjs**

```js
export function parseCoverCommand(body) {
  const sel = String(body).match(/(?:封面|用)\s*[#第]?\s*(\d+)\s*张?/);
  if (sel) return { action: 'select', n: Number(sel[1]) };
  if (/换一批|重新生成|重来/.test(String(body))) return { action: 'regen' };
  return null;
}
```

- [ ] **Step 4: 实现 scripts/cover-apply.mjs**

环境变量：`GITHUB_TOKEN`、`GITHUB_REPOSITORY`、`ISSUE_NUMBER`、`COMMENT_BODY`。

```js
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { parseCoverCommand } from './lib/cover-command-parse.mjs';
import { parseVideoEntry } from './lib/cover-frames.mjs';

const repo = process.env.GITHUB_REPOSITORY;
const issueNumber = process.env.ISSUE_NUMBER;
const token = process.env.GITHUB_TOKEN;
const MARKER = '<!-- cover-candidates';

async function ghApi(apiPath, { method = 'GET', body } = {}) {
  const res = await fetch(`https://api.github.com${apiPath}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`GitHub ${method} ${apiPath} → ${res.status}: ${await res.text()}`);
  return res.json();
}

function git(...args) {
  return execFileSync('git', args, { encoding: 'utf8' }).trim();
}

async function reply(text) {
  await ghApi(`/repos/${repo}/issues/${issueNumber}/comments`, { method: 'POST', body: { body: text } });
}

const cmd = parseCoverCommand(process.env.COMMENT_BODY ?? '');
if (!cmd) {
  console.log('not a cover command');
  process.exit(0);
}

// 拿到 PR head 分支并检出
const pr = await ghApi(`/repos/${repo}/pulls/${issueNumber}`);
const branch = pr.head.ref;
if (!branch.startsWith('intake/')) {
  console.log('not an intake PR');
  process.exit(0);
}
git('fetch', 'origin', branch);
git('checkout', branch);
git('config', 'user.name', 'jodie-site-bot');
git('config', 'user.email', 'bot@users.noreply.github.com');

// 读汇总评论里的候选映射
const comments = await ghApi(`/repos/${repo}/issues/${issueNumber}/comments?per_page=100`);
const summary = comments.find((c) => c.body?.includes(MARKER));
if (!summary) {
  await reply('没有找到候选封面评论，可能尚未生成。请稍后重试。');
  process.exit(0);
}
const meta = JSON.parse(summary.body.match(/<!-- cover-candidates\n([\s\S]*?)\n-->/)[1]);

if (cmd.action === 'select') {
  const item = meta.items.find((it) => it.n === cmd.n);
  if (!item) {
    await reply(`没有找到第 ${cmd.n} 号候选，请检查编号。`);
    process.exit(0);
  }
  const dest = `public/images/media/${item.slug}.jpg`;
  fs.mkdirSync('public/images/media', { recursive: true });
  fs.copyFileSync(item.path, dest);
  // 更新条目 cover 字段
  const entryPath = `src/content/media/${item.slug}.md`;
  const md = fs.readFileSync(entryPath, 'utf8');
  if (!/^cover:/m.test(md)) {
    fs.writeFileSync(entryPath, md.replace(/---\n$/, `cover: "/images/media/${item.slug}.jpg"\n---\n`));
  }
  fs.rmSync(path.join('.cover-candidates', item.slug), { recursive: true, force: true });
  meta.items = meta.items.filter((it) => it.slug !== item.slug);
  git('add', '-A');
  git('commit', '-m', `chore: pick cover ${cmd.n} for ${item.slug}`);
  git('push', 'origin', branch);
  await reply(`已将第 ${cmd.n} 号候选设为 \`${item.slug}\` 的封面。`);
} else {
  // regen：为仍无 cover 的 video 条目换一组时间戳重截
  const round = (meta.round ?? 0) + 1;
  const slugs = [...new Set(meta.items.map((it) => it.slug))];
  if (slugs.length === 0) {
    await reply('所有视频都已选定封面，无需重截。');
    process.exit(0);
  }
  for (const slug of slugs) {
    const md = fs.readFileSync(`src/content/media/${slug}.md`, 'utf8');
    const info = parseVideoEntry(md);
    if (!info || info.hasCover) continue;
    fs.rmSync(path.join('.cover-candidates', slug), { recursive: true, force: true });
    execFileSync('node', ['scripts/extract-cover-frames.mjs', info.url, path.join('.cover-candidates', slug), String(round)], { stdio: 'inherit' });
  }
  // 重新编号
  const items = [];
  let n = 0;
  for (const slug of fs.readdirSync('.cover-candidates').sort()) {
    for (const f of fs.readdirSync(path.join('.cover-candidates', slug)).sort()) {
      if (!f.endsWith('.jpg')) continue;
      n += 1;
      items.push({ n, slug, path: `.cover-candidates/${slug}/${f}`, chosen: false });
    }
  }
  meta.items = items;
  meta.round = round;
  git('add', '-A');
  git('commit', '-m', `chore: regenerate cover candidates (round ${round})`);
  git('push', 'origin', branch);
  await reply(`已重新生成 ${items.length} 张候选（第 ${round + 1} 批），请见更新后的候选评论。`);
}

// 更新汇总评论
const lines = meta.items.map(
  (it) => `**${it.n}.** \`${it.slug}\`\n\n![候选 ${it.n}](https://github.com/${repo}/blob/${branch}/${it.path}?raw=true)`,
);
const newBody = `${MARKER}\n${JSON.stringify(meta)}\n-->

## 视频候选封面

${meta.items.length ? `共 ${meta.items.length} 张候选。回复「封面 N」选定第 N 张；回复「换一批」为未选定的视频重新截取。\n\n${lines.join('\n\n')}` : '所有视频封面均已选定。'}`;

await ghApi(`/repos/${repo}/issues/comments/${summary.id}`, { method: 'PATCH', body: { body: newBody } });
```

- [ ] **Step 5: 创建 .github/workflows/cover-command.yml**

```yaml
name: cover-command
on: issue_comment
permissions:
  contents: write
  issues: write
  pull-requests: read
jobs:
  apply:
    if: >-
      github.event.issue.pull_request &&
      contains(fromJSON('["OWNER","MEMBER","COLLABORATOR"]'), github.event.comment.author_association)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - name: Install yt-dlp
        run: pip install yt-dlp
      - name: Apply cover command
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          COMMENT_BODY: ${{ github.event.comment.body }}
        run: node scripts/cover-apply.mjs
```

注意：select 提交（往 PR 分支加 cover）会触发 synchronize → cover-candidates 重跑，但该条 cover 已设、候选目录已删，会被跳过，不会覆盖选择——幂等。

- [ ] **Step 6: 本地验证**

```bash
node --check scripts/cover-apply.mjs && npm test
```

Expected: 语法检查通过、测试全 PASS。

- [ ] **Step 7: Commit**

```bash
git add scripts/lib/cover-command-parse.mjs scripts/cover-apply.mjs .github/workflows/cover-command.yml tests/cover-command-parse.test.mjs
git commit -m "feat: add cover selection and regeneration commands"
```

---

### Task 13: 文档更新与端到端验证

**Files:**
- Modify: `docs/content-operations-sop.md`（全文重写为新流程）
- Modify: `AGENTS.md`（§2 指向新 SOP/规格；§8 纯静态例外说明）
- Modify: `.gitignore`（确认含 `.env`）

**Interfaces:**
- Consumes: 前 12 个 Task 的全部产物。

- [ ] **Step 1: .gitignore 加 `.env`**

```
.DS_Store
node_modules/
dist/
.astro/
.superpowers/
.playwright-mcp/
.env
```

- [ ] **Step 2: 重写 docs/content-operations-sop.md**

```markdown
# 内容运营流程 SOP

> 自 2026-08 起，内容更新走「投递后台 + 云端自动入库」。运营不碰 Git，审核人在 GitHub 网页审 PR。

## 角色分工

| 角色 | 职责 |
|------|------|
| 运营 | 打开 `/admin`（密码登录），粘贴链接或上传照片 |
| 系统（GitHub Actions） | 解析、翻译、归类、查重、生成条目并开 PR；为视频生成候选封面 |
| 审核人（文晶指定） | 在 GitHub 网页审 PR、选封面、合并即发布 |

## 运营：投递

1. 打开 `https://<域名>/admin`，输入密码登录
2. **链接**：一行一个 URL 粘贴进文本框（单次最多 10 条）；知道素材性质时在「类型」下拉手动指定（不确定保持「自动判断」——广播/录音类请手动选「采访（含音频）」）
3. **照片**：选图（自动压缩）+ 一句图注（中或英）+ 可选日期
4. 提交后页面显示「已受理」；「最近投递」区可跟踪状态：处理中 / 待审核（附 PR 链接）/ 失败（附日志链接）。失败时把日志链接发给技术联系人

## 审核人：审 PR

1. 打开 PR，看「内容入库审核清单」：标题、链接、判定结果、判定依据、状态（成功/失败/跳过及原因）
2. **只在 Vercel 预览构建绿色（checks 全过）时合并**——红色说明条目有问题，不要合并，把 PR 链接发给技术联系人
3. 小错（类型、日期、翻译措辞）：点文件右上角「…」→ Edit file 直接改。类型就是 frontmatter 里一行，如 `type: "video"` 改成 `type: "interview"`
4. 整条不该收：在 PR 文件列表删除该文件；或关闭 PR 让运营重投
5. **视频封面**：PR 里会出现候选封面评论（统一编号）。回复「封面 3」选定第 3 张；不满意回复「换一批」重新截取，可反复多次直至满意，然后合并
6. 合并后 Vercel 自动构建，约 1–2 分钟上线

## 注意事项

- 阿语文案为 AI 翻译初稿，审核时如发现阿语问题直接在 PR 里改
- 同一 URL 重复投递会被自动跳过并在 PR 清单标注
- `/admin` 地址不要公开传播；密码定期更换（Vercel 环境变量 `ADMIN_PASSWORD`）
```

- [ ] **Step 3: 更新 AGENTS.md**

§2 的 SOP 条目改为：

```markdown
- `docs/content-operations-sop.md` —— 内容运营 SOP（2026-08-09 起：运营经 `/admin` 投递页投素材，GitHub Actions 自动解析入库开 PR，审核人合并发布；设计见 `docs/superpowers/specs/2026-08-09-admin-intake-pipeline-design.md`）。部署：GitHub + Vercel。
```

§8 部署节改为：

```markdown
## 8. 部署

GitHub 托管代码 + Vercel 构建发布。前台 24 个路由为纯静态；**例外**：`/admin` 与 `/api/*` 为按需渲染（`@astrojs/vercel` adapter），配合三个 GitHub Actions 工作流（intake-pipeline / cover-candidates / cover-command）实现运营投递与自动入库。所需环境变量与密钥见设计规格 §6。
```

- [ ] **Step 4: 最终构建验证**

```bash
npm run build && npx astro check && npm test
```

Expected: 全绿。

- [ ] **Step 5: Commit**

```bash
git add docs/content-operations-sop.md AGENTS.md .gitignore
git commit -m "docs: update operations sop and agents for intake pipeline"
```

- [ ] **Step 6: 端到端验证（部署后，需真实密钥，由用户配合）**

前置：仓库已推 GitHub、Vercel 已接入；GitHub Secrets 配好 `LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL`/`INTAKE_PAT`；Vercel 环境变量配好 `ADMIN_PASSWORD`/`ADMIN_COOKIE_SECRET`/`GH_INTAKE_TOKEN`/`GH_REPO`。

按规格 §9 验收标准逐项过：未登录拦截（标准 2）→ 投一条真实文章链接出 PR（3）→ 手动指定类型与音频链接归类（4）→ 重复 URL 跳过（5）→ 坏链接进失败清单（6）→ 照片三语图注（7）→ 临时填错 LLM key 验证状态区显示失败（8）→ 两条视频的候选编号/选定/换一批（9）→ 非协作者评论不触发（10）。逐项记录结果。
