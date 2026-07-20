# Jodie Wen 个人宣传网站 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按已批准的设计规格，用 Astro 5 + Tailwind CSS 实现文晶（Jodie Wen）的中英双语个人宣传静态网站（8 页 × 2 语言）。

**Architecture:** Astro 5 静态输出 + 内置 i18n 路由（英文无前缀，中文 `/zh/` 前缀）；三个 Content Collections（publications/media/activities）承载列表类内容，zod schema 校验；长文内容直接写在各语言路由模板里；零客户端 JS（语言切换靠路由，移动导航靠纯 CSS checkbox）。

**Tech Stack:** Astro 5、TypeScript、Tailwind CSS v4（`@tailwindcss/vite`）、zod（Astro 内置）、Node v26.3.1 + npm 11.16.0。

**规格文档:** `docs/superpowers/specs/2026-07-20-jodie-wen-personal-site-design.md`（本计划的唯一依据；如有出入以规格为准）。

## Global Constraints

- 技术栈：Astro 5 + `output: 'static'`；**不引入任何前端框架组件**（React/Vue 等），保持零运行时 JS 依赖。
- i18n：`defaultLocale: 'en'`，`locales: ['en', 'zh']`，`prefixDefaultLocale: false`；英文 `/about`，中文 `/zh/about`。
- 视觉：黑白灰 + 点缀色深青 `#0F766E`；系统字体栈（英文 `-apple-system, "Segoe UI", Roboto, "Helvetica Neue"`；中文 `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei"`；标题衬线 `"Georgia", "Songti SC", serif`）；不用网络字体；移动优先；正文最大宽度约 72ch。
- 所有外链一律 `target="_blank" rel="noopener"`。
- 视频 `embedUrl` 缺失时降级为链接卡片，不渲染 iframe；无素材版块渲染空态文案「内容整理中 / Content being compiled.」，不报错。
- YAGNI 红线（规格 §9，禁止添加）：联系表单、评论、搜索、博客/文章详情页、暗色模式、动画特效库、CMS 接入、部署配置。
- 联系方式只允许出现邮箱 `jodiewen@tsinghua.edu.cn`，不得虚构或公开其他个人私密信息。
- 肖像照/书封未提供：用灰色占位块（`bg-neutral-200` 的 div），列入待补充清单。
- 找不到真实链接的已知条目：URL 用占位符 `https://example.com/placeholder-<slug>`（可 grep），并记录到 `docs/pending-assets.md`；**宁可占位，不得虚构链接**。
- 环境：npm registry 直连若失败/过慢，改用 `npm install --registry=https://registry.npmmirror.com`；GitHub 直连不通，curl/git 外网检查走代理 `http://127.0.0.1:7890`（curl 加 `-x http://127.0.0.1:7890`）。
- 提交：每个任务末尾按步骤 commit，使用 conventional commits 英文消息（如 `feat: add publications page`）。
- 验证基线：无自动化测试框架；每个任务的"测试" = `npm run build` 成功 + `npx astro check` 无错误 + 对 `dist/` 产物的 grep/test -f 断言。

## 文件结构

```
jodie-wen-site/
├── package.json                    # Task 1
├── astro.config.mjs                # Task 1：static 输出 + i18n + tailwindcss vite 插件
├── tsconfig.json                   # Task 1
├── src/
│   ├── styles/global.css           # Task 1：Tailwind 导入 + @theme（accent 色、字体栈）+ .measure
│   ├── i18n/
│   │   ├── ui.ts                   # Task 2：Locale 类型 + UI 字符串字典（en/zh）
│   │   └── utils.ts                # Task 2：getLocaleFromPath / getAlternatePath / localizePath
│   ├── components/
│   │   ├── BaseLayout.astro        # Task 2：HTML 骨架 + Nav + Footer + slot
│   │   ├── Nav.astro               # Task 2：导航 + 语言切换 + 纯 CSS 汉堡菜单
│   │   ├── Footer.astro            # Task 2
│   │   ├── Hero.astro              # Task 4
│   │   ├── SectionHeader.astro     # Task 4
│   │   ├── TimelineItem.astro      # Task 5
│   │   ├── PublicationList.astro   # Task 7
│   │   ├── MediaCard.astro         # Task 8
│   │   ├── ActivityList.astro      # Task 9
│   │   ├── TalkIntro.astro         # Task 10
│   │   └── ContactBlock.astro      # Task 11
│   ├── content.config.ts           # Task 3：三个集合 + zod schema
│   ├── content/
│   │   ├── publications/*.md       # Task 3 样例 → Task 7 真实条目
│   │   ├── media/*.md              # Task 3 样例 → Task 8 真实条目
│   │   └── activities/*.md         # Task 3 样例 → Task 9 真实条目
│   └── pages/                      # Task 2 建全部桩页，Task 4–11 逐个替换为正式内容
│       ├── index.astro  about.astro  book.astro  publications.astro
│       ├── media.astro  activities.astro  talk.astro  contact.astro
│       └── zh/（同上 8 个文件）
└── docs/pending-assets.md          # Task 12：待补充素材清单
```

**页面职责：** 路由文件只组装组件与数据（frontmatter 里取集合、排序、切片），不写业务逻辑；长文 prose 直接写在对应语言的路由模板里。

---

### Task 1: 项目脚手架（Astro 5 + Tailwind，构建冒烟通过）

**Files:**
- Create: `package.json`
- Create: `astro.config.mjs`
- Create: `tsconfig.json`
- Create: `src/styles/global.css`
- Create: `src/pages/index.astro`（临时冒烟页，Task 2 替换）

**Interfaces:**
- Consumes: 无
- Produces: 可用的 `npm run dev` / `npm run build` / `npx astro check`；`src/styles/global.css` 定义 `@theme` 变量 `--color-accent: #0f766e`（产出 `bg-accent`/`text-accent`/`border-accent` 工具类）、`--font-sans`、`--font-serif`，以及 `.measure` 类（72ch）。后续所有任务依赖这些类名。

- [ ] **Step 1: 写 `package.json`**

```json
{
  "name": "jodie-wen-site",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "check": "astro check"
  },
  "dependencies": {
    "astro": "^5.0.0"
  },
  "devDependencies": {
    "@astrojs/check": "^0.9.0",
    "@tailwindcss/vite": "^4.0.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.6.0"
  }
}
```

- [ ] **Step 2: 写 `astro.config.mjs`**

```js
// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  output: 'static',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
```

- [ ] **Step 3: 写 `tsconfig.json`**

```json
{
  "extends": "astro/tsconfigs/strict",
  "include": [".astro/types.d.ts", "**/*"],
  "exclude": ["dist"]
}
```

- [ ] **Step 4: 写 `src/styles/global.css`**

```css
@import "tailwindcss";

@theme {
  --color-accent: #0f766e;
  --font-sans: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-serif: "Georgia", "Songti SC", serif;
}

@layer base {
  body {
    @apply bg-white font-sans text-neutral-800 antialiased;
  }
}

/* 正文最大宽度约 72ch（规格 §5） */
.measure {
  max-width: 72ch;
}
```

- [ ] **Step 5: 写临时冒烟页 `src/pages/index.astro`**

```astro
---
import '../styles/global.css';
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Jodie Wen</title>
  </head>
  <body>
    <h1 class="font-serif text-3xl font-bold text-accent">Jodie Wen</h1>
  </body>
</html>
```

- [ ] **Step 6: 安装依赖**

Run: `npm install`
若 5 分钟内未完成或报网络错误，改用：`npm install --registry=https://registry.npmmirror.com`
Expected: 成功生成 `node_modules/` 与 `package-lock.json`。

- [ ] **Step 7: 验证构建与类型检查**

Run: `npm run build && npx astro check`
Expected: build 成功，末尾有 `dist/` 目录；`astro check` 输出 `0 errors`；`test -f dist/index.html && grep -q 'Jodie Wen' dist/index.html` 退出码 0。

- [ ] **Step 8: Commit**

```bash
git add package.json package-lock.json astro.config.mjs tsconfig.json src/
git commit -m "feat: scaffold Astro 5 + Tailwind CSS v4 project"
```

---

### Task 2: i18n 基础设施 + BaseLayout/Nav/Footer + 16 个桩页面

**Files:**
- Create: `src/i18n/ui.ts`
- Create: `src/i18n/utils.ts`
- Create: `src/components/BaseLayout.astro`
- Create: `src/components/Nav.astro`
- Create: `src/components/Footer.astro`
- Modify: `src/pages/index.astro`（替换为桩页）
- Create: `src/pages/{about,book,publications,media,activities,talk,contact}.astro`（桩页）
- Create: `src/pages/zh/{index,about,book,publications,media,activities,talk,contact}.astro`（桩页）

**Interfaces:**
- Consumes: Task 1 的全局样式与 `font-serif`/`text-accent` 类。
- Produces:
  - `src/i18n/ui.ts`：`export const locales = ['en','zh'] as const; export type Locale; export const defaultLocale: Locale; export const ui: { en: {...}, zh: {...} } as const; export type UIKey`（key 清单见下方代码，后续任务只用这些 key）。
  - `src/i18n/utils.ts`：`getLocaleFromPath(pathname: string): Locale`、`getAlternatePath(pathname: string): string`、`localizePath(path: string, locale: Locale): string`。
  - `<BaseLayout title={string} locale={Locale} description?: string>`：内部渲染 Nav/Footer 与 `<slot />`；后续每个页面都包它。

- [ ] **Step 1: 写 `src/i18n/ui.ts`**

```ts
export const locales = ['en', 'zh'] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = 'en';

export const ui = {
  en: {
    'nav.home': 'Home',
    'nav.about': 'About',
    'nav.book': 'Book',
    'nav.publications': 'Publications',
    'nav.media': 'Media',
    'nav.activities': 'Activities',
    'nav.talk': 'Wenjing Talk',
    'nav.contact': 'Contact',
    'lang.switch': '中文',
    'footer.rights': 'All rights reserved.',
    'hero.kicker': 'Fellow, Center for International Security and Strategy (CISS), Tsinghua University',
    'hero.tagline': 'Scholar of U.S. foreign policy and Middle East politics; former senior journalist covering 40+ countries.',
    'hero.cta.book': 'The Book',
    'hero.cta.contact': 'Contact',
    'home.book.title': 'The Book',
    'home.publications.title': 'Latest Publications',
    'home.media.title': 'In the Media',
    'home.viewAll': 'View all →',
    'publications.title': 'Publications',
    'publications.subtitle': 'Op-eds and commentary in international media',
    'media.title': 'Media',
    'media.videos': 'Interviews & Videos',
    'media.mentions': 'Media Mentions',
    'media.wall': 'As featured in',
    'activities.title': 'Activities',
    'activities.subtitle': 'International forums and Track II dialogues',
    'talk.title': 'Wenjing Talk',
    'contact.title': 'Contact',
    'contact.email': 'Email',
    'contact.affiliation': 'Affiliation',
    'contact.affiliation.value': 'Center for International Security and Strategy (CISS), Tsinghua University, Beijing, China',
    'link.source': 'Source',
    'empty': 'Content being compiled.',
  },
  zh: {
    'nav.home': '首页',
    'nav.about': '关于',
    'nav.book': '著作',
    'nav.publications': '发表',
    'nav.media': '媒体',
    'nav.activities': '活动',
    'nav.talk': '文晶Talk',
    'nav.contact': '联系',
    'lang.switch': 'EN',
    'footer.rights': '版权所有。',
    'hero.kicker': '清华大学战略与安全研究中心研究员、中国论坛国际传播主任',
    'hero.tagline': '美国外交与中东政治研究者；资深媒体人，曾在 40 余国进行新闻报道与田野调查。',
    'hero.cta.book': '我的著作',
    'hero.cta.contact': '联系我',
    'home.book.title': '专著',
    'home.publications.title': '最新发表',
    'home.media.title': '媒体报道',
    'home.viewAll': '查看全部 →',
    'publications.title': '发表文章',
    'publications.subtitle': '发表于国内外媒体的评论文章',
    'media.title': '媒体报道',
    'media.videos': '采访与视频',
    'media.mentions': '媒体引用',
    'media.wall': '合作媒体',
    'activities.title': '学术活动',
    'activities.subtitle': '国际论坛与二轨对话',
    'talk.title': '文晶Talk',
    'contact.title': '联系方式',
    'contact.email': '邮箱',
    'contact.affiliation': '单位',
    'contact.affiliation.value': '清华大学战略与安全研究中心（CISS），北京',
    'link.source': '来源',
    'empty': '内容整理中',
  },
} as const;

export type UIKey = keyof (typeof ui)['en'];
```

- [ ] **Step 2: 写 `src/i18n/utils.ts`**

```ts
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
```

- [ ] **Step 3: 写 `src/components/Nav.astro`（含纯 CSS 汉堡菜单与语言切换）**

```astro
---
import { ui, type Locale } from '../i18n/ui';
import { getAlternatePath, localizePath } from '../i18n/utils';

interface Props {
  locale: Locale;
  currentPath: string;
}
const { locale, currentPath } = Astro.props;
const t = ui[locale];

const items = [
  { path: '/', label: t['nav.home'] },
  { path: '/about', label: t['nav.about'] },
  { path: '/book', label: t['nav.book'] },
  { path: '/publications', label: t['nav.publications'] },
  { path: '/media', label: t['nav.media'] },
  { path: '/activities', label: t['nav.activities'] },
  { path: '/talk', label: t['nav.talk'] },
  { path: '/contact', label: t['nav.contact'] },
];

const normalize = (p: string) => (p.length > 1 ? p.replace(/\/+$/, '') : p);
const current = normalize(currentPath);
const isCurrent = (path: string) => normalize(localizePath(path, locale)) === current;
const alternatePath = getAlternatePath(currentPath);
---
<header class="relative border-b border-neutral-200">
  <nav class="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
    <a href={localizePath('/', locale)} class="font-serif text-xl font-bold">
      {locale === 'zh' ? '文晶' : 'Jodie Wen'}
    </a>
    <input type="checkbox" id="nav-toggle" class="peer hidden" />
    <label for="nav-toggle" class="cursor-pointer text-2xl leading-none md:hidden" aria-label="Menu">☰</label>
    <ul class="absolute left-0 right-0 top-full z-10 hidden flex-col gap-1 border-b border-neutral-200 bg-white px-4 py-3 peer-checked:flex md:static md:flex md:flex-row md:items-center md:gap-5 md:border-0 md:p-0">
      {items.map((item) => (
        <li>
          <a
            href={localizePath(item.path, locale)}
            class:list={[
              'block py-1 text-sm',
              isCurrent(item.path) ? 'font-semibold text-accent' : 'text-neutral-700 hover:text-accent',
            ]}
          >
            {item.label}
          </a>
        </li>
      ))}
      <li>
        <a href={alternatePath} class="block py-1 text-sm font-semibold text-accent hover:underline">
          {t['lang.switch']}
        </a>
      </li>
    </ul>
  </nav>
</header>
```

- [ ] **Step 4: 写 `src/components/Footer.astro`**

```astro
---
import { ui, type Locale } from '../i18n/ui';

interface Props {
  locale: Locale;
}
const { locale } = Astro.props;
const t = ui[locale];
const year = new Date().getFullYear();
---
<footer class="mt-16 border-t border-neutral-200">
  <div class="mx-auto flex max-w-5xl flex-col gap-2 px-4 py-8 text-sm text-neutral-500 md:flex-row md:items-center md:justify-between">
    <p>© {year} {locale === 'zh' ? '文晶' : 'Jodie Wen'}. {t['footer.rights']}</p>
    <p>
      <a href="mailto:jodiewen@tsinghua.edu.cn" class="text-accent hover:underline">jodiewen@tsinghua.edu.cn</a>
    </p>
  </div>
</footer>
```

- [ ] **Step 5: 写 `src/components/BaseLayout.astro`**

```astro
---
import '../styles/global.css';
import Nav from './Nav.astro';
import Footer from './Footer.astro';
import type { Locale } from '../i18n/ui';

interface Props {
  title: string;
  locale: Locale;
  description?: string;
}
const { title, locale, description } = Astro.props;
---
<!doctype html>
<html lang={locale === 'zh' ? 'zh-CN' : 'en'}>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    {description && <meta name="description" content={description} />}
    <title>{title}</title>
  </head>
  <body class="flex min-h-screen flex-col">
    <Nav locale={locale} currentPath={Astro.url.pathname} />
    <main class="mx-auto w-full max-w-3xl flex-1 px-4 py-10">
      <slot />
    </main>
    <Footer locale={locale} />
  </body>
</html>
```

- [ ] **Step 6: 写 16 个桩页面**

英文桩页模板（以 `src/pages/about.astro` 为例；`../components/` 一层）：

```astro
---
import BaseLayout from '../components/BaseLayout.astro';
---
<BaseLayout title="About — Jodie Wen" locale="en">
  <h1 class="font-serif text-3xl font-bold">About</h1>
</BaseLayout>
```

中文桩页模板（以 `src/pages/zh/about.astro` 为例；`../../components/` 两层）：

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
---
<BaseLayout title="关于 — 文晶" locale="zh">
  <h1 class="font-serif text-3xl font-bold">关于</h1>
</BaseLayout>
```

按下表创建全部 16 个文件（title / h1 均取表中文字，逐字使用）：

| 文件 | locale | title | h1 |
|---|---|---|---|
| `src/pages/index.astro` | en | `Jodie Wen — CISS Fellow, Tsinghua University` | `Jodie Wen` |
| `src/pages/about.astro` | en | `About — Jodie Wen` | `About` |
| `src/pages/book.astro` | en | `Book — Jodie Wen` | `Book` |
| `src/pages/publications.astro` | en | `Publications — Jodie Wen` | `Publications` |
| `src/pages/media.astro` | en | `Media — Jodie Wen` | `Media` |
| `src/pages/activities.astro` | en | `Activities — Jodie Wen` | `Activities` |
| `src/pages/talk.astro` | en | `Wenjing Talk — Jodie Wen` | `Wenjing Talk` |
| `src/pages/contact.astro` | en | `Contact — Jodie Wen` | `Contact` |
| `src/pages/zh/index.astro` | zh | `文晶 — 清华大学战略与安全研究中心研究员` | `文晶` |
| `src/pages/zh/about.astro` | zh | `关于 — 文晶` | `关于` |
| `src/pages/zh/book.astro` | zh | `著作 — 文晶` | `著作` |
| `src/pages/zh/publications.astro` | zh | `发表 — 文晶` | `发表` |
| `src/pages/zh/media.astro` | zh | `媒体 — 文晶` | `媒体` |
| `src/pages/zh/activities.astro` | zh | `活动 — 文晶` | `活动` |
| `src/pages/zh/talk.astro` | zh | `文晶Talk — 文晶` | `文晶Talk` |
| `src/pages/zh/contact.astro` | zh | `联系 — 文晶` | `联系` |

- [ ] **Step 7: 验证全部路由与语言切换**

Run: `npm run build && npx astro check`
Expected: `0 errors`；以下断言全部退出码 0：

```bash
for f in index about book publications media activities talk contact; do
  test -f "dist/$f/index.html" || { echo "MISSING dist/$f/index.html"; exit 1; }
  test -f "dist/zh/$f/index.html" || { echo "MISSING dist/zh/$f/index.html"; exit 1; }
done
grep -q 'href="/zh/about' dist/about/index.html   # en → zh 切换链接（href 实际为 /zh/about/，前缀匹配即可）
grep -q 'href="/about' dist/zh/about/index.html   # zh → en 切换链接（开头引号确保不会误匹配 /zh/about）
grep -q 'lang="zh-CN"' dist/zh/about/index.html
grep -q 'lang="en"' dist/about/index.html
```

- [ ] **Step 8: Commit**

```bash
git add src/
git commit -m "feat: add i18n infrastructure, layout components and stub pages"
```

---

### Task 3: Content Collections（三个集合 + zod schema + 样例条目 + 坏数据验证）

**Files:**
- Create: `src/content.config.ts`
- Create: `src/content/publications/000-sample.md`
- Create: `src/content/media/000-sample.md`
- Create: `src/content/activities/000-sample.md`
- Create + Delete: `src/content/publications/999-bad.md`（负向测试用）

**Interfaces:**
- Consumes: 无（Astro 5 content layer）。
- Produces: 三个集合 `publications` / `media` / `activities`；后续任务用 `getCollection('publications')` 等取数，`entry.data` 字段名与类型以下方 schema 为准（`date` 经 `z.coerce.date()` 输出为 `Date`）。

- [ ] **Step 1: 写 `src/content.config.ts`**

```ts
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
    date: z.coerce.date(),
    url: z.string().url().optional(),
  }),
});

export const collections = { publications, media, activities };
```

- [ ] **Step 2: 写 3 个样例条目**（占位用，Task 7/8/9 会删除替换）

`src/content/publications/000-sample.md`:

```markdown
---
titleEn: "Sample publication entry"
titleZh: "样例文章条目"
outlet: "Sample Outlet"
date: 2026-01-01
url: "https://example.com/placeholder-sample-publication"
lang: "en"
---
```

`src/content/media/000-sample.md`:

```markdown
---
titleEn: "Sample media entry"
titleZh: "样例媒体条目"
type: "interview"
outlet: "Sample Outlet"
date: 2026-01-01
url: "https://example.com/placeholder-sample-media"
platform: "other"
---
```

`src/content/activities/000-sample.md`:

```markdown
---
titleEn: "Sample activity entry"
titleZh: "样例活动条目"
event: "Sample Forum"
location: "Beijing"
date: 2026-01-01
url: "https://example.com/placeholder-sample-activity"
---
```

- [ ] **Step 3: 验证构建通过**

Run: `npm run build && npx astro check`
Expected: 成功，`0 errors`（schema 生效，样例数据合法）。

- [ ] **Step 4: 负向测试——构造缺字段坏数据，确认 schema 拦截**

写 `src/content/publications/999-bad.md`（缺 `titleEn`、`url` 非法）：

```markdown
---
titleZh: "坏数据"
outlet: "Bad"
date: 2026-01-01
url: "not-a-url"
lang: "en"
---
```

Run: `npm run build`
Expected: **构建失败**，报错信息包含 `titleEn` / `Invalid url`（schema 校验拦截生效）。

- [ ] **Step 5: 删除坏数据并恢复构建**

Run: `rm src/content/publications/999-bad.md && npm run build`
Expected: 构建恢复成功。

- [ ] **Step 6: Commit**

```bash
git add src/content.config.ts src/content/
git commit -m "feat: add content collections with zod schemas and sample entries"
```

---

### Task 4: 首页（Hero + 精选入口，中英两页）

**Files:**
- Create: `src/components/Hero.astro`
- Create: `src/components/SectionHeader.astro`
- Modify: `src/pages/index.astro`
- Modify: `src/pages/zh/index.astro`

**Interfaces:**
- Consumes: `BaseLayout`、`ui` 字典（`hero.*`、`home.*` key）、`localizePath`、publications 集合。
- Produces: `<Hero locale={Locale} />`、`<SectionHeader title={string} subtitle?: string />`；后续任务（book/media 页）复用 SectionHeader。

- [ ] **Step 1: 写 `src/components/Hero.astro`**

```astro
---
import { ui, type Locale } from '../i18n/ui';
import { localizePath } from '../i18n/utils';

interface Props {
  locale: Locale;
}
const { locale } = Astro.props;
const t = ui[locale];
---
<section class="flex flex-col gap-8 py-6 md:flex-row md:items-center">
  <div class="h-48 w-48 shrink-0 rounded-md bg-neutral-200" role="img" aria-label="Portrait placeholder"></div>
  <div>
    <h1 class="font-serif text-4xl font-bold">{locale === 'zh' ? '文晶' : 'Jodie Wen'}</h1>
    <p class="mt-2 text-lg text-neutral-600">{t['hero.kicker']}</p>
    <p class="measure mt-4 text-neutral-700">{t['hero.tagline']}</p>
    <div class="mt-6 flex gap-3">
      <a href={localizePath('/book', locale)} class="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90">{t['hero.cta.book']}</a>
      <a href={localizePath('/contact', locale)} class="rounded-md border border-accent px-4 py-2 text-sm font-medium text-accent hover:bg-accent hover:text-white">{t['hero.cta.contact']}</a>
    </div>
  </div>
</section>
```

- [ ] **Step 2: 写 `src/components/SectionHeader.astro`**

```astro
---
interface Props {
  title: string;
  subtitle?: string;
}
const { title, subtitle } = Astro.props;
---
<div class="mb-8">
  <h2 class="font-serif text-3xl font-bold">{title}</h2>
  {subtitle && <p class="mt-2 text-neutral-600">{subtitle}</p>}
  <div class="mt-3 h-0.5 w-12 bg-accent"></div>
</div>
```

- [ ] **Step 3: 写正式英文首页 `src/pages/index.astro`**

注意：首页"最新发表"section 依赖 Task 7 的 `PublicationList`，本任务**不包含**该 section，由 Task 7 Step 5 统一补回。本步只写 Hero + Book + Media 墙：

```astro
---
import BaseLayout from '../components/BaseLayout.astro';
import Hero from '../components/Hero.astro';
import SectionHeader from '../components/SectionHeader.astro';
import { ui } from '../i18n/ui';
import { localizePath } from '../i18n/utils';

const locale = 'en' as const;
const t = ui[locale];
const outlets = ['The New York Times', 'BBC', 'South China Morning Post', 'CGTN', 'Phoenix TV', 'China-US Focus'];
---
<BaseLayout title="Jodie Wen — CISS Fellow, Tsinghua University" locale={locale} description={t['hero.tagline']}>
  <Hero locale={locale} />

  <section class="mt-14">
    <SectionHeader title={t['home.book.title']} />
    <div class="flex flex-col gap-6 sm:flex-row">
      <div class="h-56 w-40 shrink-0 rounded-md bg-neutral-200" role="img" aria-label="Book cover placeholder"></div>
      <div>
        <h3 class="font-serif text-xl font-semibold">Studies of U.S. Middle East Policy (2009–2017)</h3>
        <p class="mt-1 text-sm text-neutral-500">《美国的中东政策研究（2009-2017）》 · January 2026</p>
        <p class="measure mt-3 text-neutral-700">A systematic study of U.S. policy toward the Middle East from 2009 to 2017, drawing on Dr. Wen's research and field experience in the region.</p>
        <a href={localizePath('/book', locale)} class="mt-3 inline-block text-sm font-medium text-accent hover:underline">{t['home.viewAll']}</a>
      </div>
    </div>
  </section>

  <section class="mt-14">
    <SectionHeader title={t['home.media.title']} />
    <ul class="flex flex-wrap gap-3">
      {outlets.map((o) => <li class="rounded-md border border-neutral-200 px-3 py-2 text-sm text-neutral-600">{o}</li>)}
    </ul>
    <a href={localizePath('/media', locale)} class="mt-3 inline-block text-sm font-medium text-accent hover:underline">{t['home.viewAll']}</a>
  </section>
</BaseLayout>
```

- [ ] **Step 4: 写正式中文首页 `src/pages/zh/index.astro`**

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
import Hero from '../../components/Hero.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import { ui } from '../../i18n/ui';
import { localizePath } from '../../i18n/utils';

const locale = 'zh' as const;
const t = ui[locale];
const outlets = ['《纽约时报》', 'BBC', '《南华早报》', 'CGTN', '凤凰卫视', 'China-US Focus'];
---
<BaseLayout title="文晶 — 清华大学战略与安全研究中心研究员" locale={locale} description={t['hero.tagline']}>
  <Hero locale={locale} />

  <section class="mt-14">
    <SectionHeader title={t['home.book.title']} />
    <div class="flex flex-col gap-6 sm:flex-row">
      <div class="h-56 w-40 shrink-0 rounded-md bg-neutral-200" role="img" aria-label="书封占位"></div>
      <div>
        <h3 class="font-serif text-xl font-semibold">《美国的中东政策研究（2009-2017）》</h3>
        <p class="mt-1 text-sm text-neutral-500">2026 年 1 月出版</p>
        <p class="measure mt-3 text-neutral-700">本书系统研究 2009 至 2017 年间美国的中东政策，基于作者长期的研究积累与在中东地区的田野调查。</p>
        <a href={localizePath('/book', locale)} class="mt-3 inline-block text-sm font-medium text-accent hover:underline">{t['home.viewAll']}</a>
      </div>
    </div>
  </section>

  <section class="mt-14">
    <SectionHeader title={t['home.media.title']} />
    <ul class="flex flex-wrap gap-3">
      {outlets.map((o) => <li class="rounded-md border border-neutral-200 px-3 py-2 text-sm text-neutral-600">{o}</li>)}
    </ul>
    <a href={localizePath('/media', locale)} class="mt-3 inline-block text-sm font-medium text-accent hover:underline">{t['home.viewAll']}</a>
  </section>
</BaseLayout>
```

- [ ] **Step 5: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -q 'Studies of U.S. Middle East Policy' dist/index.html` 与 `grep -q '美国的中东政策研究' dist/zh/index.html` 退出码 0；`grep -q 'Portrait placeholder' dist/index.html` 退出码 0（肖像占位块存在）。

- [ ] **Step 6: Commit**

```bash
git add src/
git commit -m "feat: add home pages with hero, book teaser and media wall"
```

---

### Task 5: About 页（履历，中英两页）

**Files:**
- Create: `src/components/TimelineItem.astro`
- Modify: `src/pages/about.astro`
- Modify: `src/pages/zh/about.astro`

**Interfaces:**
- Consumes: `BaseLayout`、`SectionHeader`（Task 4）、ui 字典。
- Produces: `<TimelineItem period?: string title={string} org?: string description?: string />`（必须包在 `<ul>` 里使用，组件渲染 `<li>`）。

Bio 素材（已用 `textutil` 从 `/Users/eric/Downloads/Jodie*Bio.docx` 提取，直接采用，下方页面代码已内嵌）。

- [ ] **Step 1: 写 `src/components/TimelineItem.astro`**

```astro
---
interface Props {
  period?: string;
  title: string;
  org?: string;
  description?: string;
}
const { period, title, org, description } = Astro.props;
---
<li class="relative border-l-2 border-neutral-200 pb-8 pl-6 last:pb-0">
  <span class="absolute top-1 -left-[7px] h-3 w-3 rounded-full bg-accent"></span>
  {period && <p class="text-sm text-neutral-500">{period}</p>}
  <h3 class="mt-1 font-semibold">{title}</h3>
  {org && <p class="text-neutral-600">{org}</p>}
  {description && <p class="measure mt-2 text-sm text-neutral-700">{description}</p>}
</li>
```

- [ ] **Step 2: 写正式英文 About 页 `src/pages/about.astro`**

```astro
---
import BaseLayout from '../components/BaseLayout.astro';
import SectionHeader from '../components/SectionHeader.astro';
import TimelineItem from '../components/TimelineItem.astro';

const locale = 'en' as const;
---
<BaseLayout title="About — Jodie Wen" locale={locale} description="Biography of Dr. Jodie Wen, Fellow at CISS, Tsinghua University.">
  <SectionHeader title="About" />

  <div class="measure space-y-4 text-neutral-700">
    <p>Dr. Jodie Wen (Wen Jing) is a Fellow at the Center for International Security and Strategy (CISS), Tsinghua University, where she also serves as Director of International Communication for the China Forum, a platform dedicated to facilitating high-level exchanges on China-related issues both domestically and internationally.</p>
    <p>Specializing in U.S. foreign policy, Middle East politics, and international communication, Dr. Wen holds a Ph.D. in Middle East Studies from Peking University, conducted postdoctoral research in Law at Tsinghua University, and was a visiting scholar at the University of Oxford from 2021 to 2022. In January 2026, she published her latest book on U.S. Middle East policy.</p>
    <p>Dr. Wen is actively engaged in international forums as well as Track II dialogues involving China, the United States, and the Middle East. She frequently provides analysis and commentary for leading media outlets, including The New York Times, BBC, South China Morning Post, CGTN, Phoenix TV, and China-US Focus.</p>
    <p>Prior to her academic career, Dr. Wen had a distinguished background in journalism. She worked as a senior journalist and news anchor, reporting from more than 40 countries across Europe, Asia, and the Middle East—including the United Kingdom, Germany, Belgium, Japan, South Korea, Pakistan, Iraq, Iran, Turkey, and Lebanon—for both news coverage and field-based research.</p>
  </div>

  <div class="mt-14">
    <SectionHeader title="Experience & Education" />
    <ul>
      <TimelineItem period="Current" title="Fellow" org="Center for International Security and Strategy (CISS), Tsinghua University" description="Also Director of International Communication, China Forum." />
      <TimelineItem period="2021–2022" title="Visiting Scholar" org="Oxford School of Global and Area Studies, University of Oxford" />
      <TimelineItem title="Postdoctoral Researcher in Law" org="Tsinghua University" />
      <TimelineItem title="Ph.D. in Middle East Studies" org="Peking University" />
      <TimelineItem title="Senior Journalist & News Anchor" description="Reported from 40+ countries across Europe, Asia, and the Middle East for news coverage and field-based research." />
    </ul>
  </div>

  <div class="mt-14">
    <SectionHeader title="Research Areas" />
    <ul class="flex flex-wrap gap-3">
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">U.S. foreign policy</li>
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">Middle East politics</li>
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">International communication</li>
    </ul>
  </div>
</BaseLayout>
```

- [ ] **Step 3: 写正式中文 About 页 `src/pages/zh/about.astro`**

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import TimelineItem from '../../components/TimelineItem.astro';

const locale = 'zh' as const;
---
<BaseLayout title="关于 — 文晶" locale={locale} description="文晶，清华大学战略与安全研究中心研究员、中国论坛国际传播主任。">
  <SectionHeader title="关于" />

  <div class="measure space-y-4 text-neutral-700">
    <p>文晶，清华大学战略与安全研究中心（CISS）研究员、中国论坛国际传播主任。中国论坛是致力于推动国内外就中国议题开展高层次交流的平台。</p>
    <p>文晶为清华大学法学博士后、北京大学中东研究方向博士、牛津大学全球与区域研究院访问学者（2021–2022）。主要研究领域：美国外交、中东政治与国际传播。2026 年 1 月出版专著《美国的中东政策研究（2009-2017）》。</p>
    <p>她曾多次参与外交部、中宣部等部委重大研究课题，多次作为中国学者代表参加国际论坛及中美、中东二轨对话，是央视、凤凰卫视、东方卫视等多家媒体的特约评论员，并常为《纽约时报》、BBC、《南华早报》、CGTN、China-US Focus 等媒体提供分析评论。</p>
    <p>从事学术工作之前，文晶曾是资深记者与新闻主播，在欧洲、亚洲和中东地区 40 多个国家——包括英国、德国、比利时、日本、韩国、巴基斯坦、伊拉克、伊朗、土耳其、黎巴嫩等——进行新闻报道和田野调查。</p>
  </div>

  <div class="mt-14">
    <SectionHeader title="经历与教育" />
    <ul>
      <TimelineItem period="现任" title="研究员" org="清华大学战略与安全研究中心（CISS）" description="兼任中国论坛国际传播主任。" />
      <TimelineItem period="2021–2022" title="访问学者" org="牛津大学全球与区域研究院" />
      <TimelineItem title="法学博士后" org="清华大学" />
      <TimelineItem title="中东研究博士" org="北京大学" />
      <TimelineItem title="资深记者、新闻主播" description="在欧美、中东和东南亚地区 40 多个国家进行新闻报道和田野调查。" />
    </ul>
  </div>

  <div class="mt-14">
    <SectionHeader title="研究领域" />
    <ul class="flex flex-wrap gap-3">
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">美国外交</li>
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">中东政治</li>
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">国际传播</li>
    </ul>
  </div>
</BaseLayout>
```

- [ ] **Step 4: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -q 'Peking University' dist/about/index.html` 与 `grep -q '北京大学' dist/zh/about/index.html` 退出码 0。

- [ ] **Step 5: Commit**

```bash
git add src/
git commit -m "feat: add about pages with bio and career timeline"
```

---

### Task 6: Book 页（专著，中英两页）

**Files:**
- Modify: `src/pages/book.astro`
- Modify: `src/pages/zh/book.astro`

**Interfaces:**
- Consumes: `BaseLayout`、`SectionHeader`。
- Produces: 无新组件。

- [ ] **Step 1: 联网核实书籍出版信息**

用 WebSearch 搜索：`《美国的中东政策研究（2009-2017）》 文晶`、`文晶 美国的中东政策研究 出版社`、`Jodie Wen book US Middle East policy`。
目标：出版社、出版日期、ISBN、购买/出版社页面链接。
规则：只写核实到的信息；核实不到就在页面用「待补充」占位文案，并把缺口记入 Task 12 的 `docs/pending-assets.md`。**不得虚构出版社/ISBN/链接。**

- [ ] **Step 2: 写正式英文 Book 页 `src/pages/book.astro`**

```astro
---
import BaseLayout from '../components/BaseLayout.astro';
import SectionHeader from '../components/SectionHeader.astro';

const locale = 'en' as const;
---
<BaseLayout title="Book — Jodie Wen" locale={locale} description="Studies of U.S. Middle East Policy (2009–2017), a monograph by Dr. Jodie Wen.">
  <SectionHeader title="The Book" />
  <div class="flex flex-col gap-8 sm:flex-row">
    <div class="h-72 w-52 shrink-0 rounded-md bg-neutral-200" role="img" aria-label="Book cover placeholder"></div>
    <div>
      <h3 class="font-serif text-2xl font-semibold">Studies of U.S. Middle East Policy (2009–2017)</h3>
      <p class="mt-1 text-neutral-500">《美国的中东政策研究（2009-2017）》 · Chinese-language monograph · January 2026</p>
      <div class="measure mt-4 space-y-4 text-neutral-700">
        <p>Drawing on years of research and fieldwork across the Middle East, this book offers a systematic study of U.S. policy toward the region from 2009 to 2017, tracing its evolution, drivers, and impact on regional order.</p>
        <p>Dr. Wen is a Fellow at the Center for International Security and Strategy (CISS), Tsinghua University, specializing in U.S. foreign policy and Middle East politics.</p>
      </div>
      <div class="mt-6">
        <h4 class="text-sm font-semibold uppercase tracking-wide text-neutral-500">Publication</h4>
        <p class="mt-1 text-sm text-neutral-600">Publisher / ISBN / purchase link to be added.</p>
      </div>
    </div>
  </div>
</BaseLayout>
```

若 Step 1 核实到出版信息，把 "Publisher / ISBN / purchase link to be added." 替换为真实信息（链接用 `target="_blank" rel="noopener"`）。

- [ ] **Step 3: 写正式中文 Book 页 `src/pages/zh/book.astro`**

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';

const locale = 'zh' as const;
---
<BaseLayout title="著作 — 文晶" locale={locale} description="文晶专著《美国的中东政策研究（2009-2017）》。">
  <SectionHeader title="著作" />
  <div class="flex flex-col gap-8 sm:flex-row">
    <div class="h-72 w-52 shrink-0 rounded-md bg-neutral-200" role="img" aria-label="书封占位"></div>
    <div>
      <h3 class="font-serif text-2xl font-semibold">《美国的中东政策研究（2009-2017）》</h3>
      <p class="mt-1 text-neutral-500">学术专著 · 2026 年 1 月出版</p>
      <div class="measure mt-4 space-y-4 text-neutral-700">
        <p>本书基于作者多年研究与在中东地区的田野调查，系统梳理 2009 至 2017 年间美国中东政策的演变脉络、内在动因及其对地区秩序的影响。</p>
        <p>作者文晶为清华大学战略与安全研究中心研究员，主要研究领域为美国外交与中东政治。</p>
      </div>
      <div class="mt-6">
        <h4 class="text-sm font-semibold uppercase tracking-wide text-neutral-500">出版信息</h4>
        <p class="mt-1 text-sm text-neutral-600">出版社 / ISBN / 购买链接待补充。</p>
      </div>
    </div>
  </div>
</BaseLayout>
```

同样，核实到真实出版信息则替换占位文案。

- [ ] **Step 4: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -q 'Studies of U.S. Middle East Policy' dist/book/index.html` 与 `grep -q '美国的中东政策研究' dist/zh/book/index.html` 退出码 0。

- [ ] **Step 5: Commit**

```bash
git add src/
git commit -m "feat: add book pages"
```

---

### Task 7: Publications（联网搜集 + 条目 + PublicationList + 两页）

**Files:**
- Create: `src/components/PublicationList.astro`
- Create: `src/content/publications/*.md`（真实条目，目标 6–12 条）
- Delete: `src/content/publications/000-sample.md`
- Modify: `src/pages/publications.astro`、`src/pages/zh/publications.astro`
- Modify: `src/pages/index.astro`、`src/pages/zh/index.astro`（补回"最新发表"section）

**Interfaces:**
- Consumes: `publications` 集合（schema 见 Task 3）；`BaseLayout`、`SectionHeader`。
- Produces: `<PublicationList entries={CollectionEntry<'publications'>[]} locale={Locale} />`（按年份分组、组内按 date 排序由页面保证；组件内也按年份倒序分组渲染）。

- [ ] **Step 1: 联网搜集发表文章**

用 WebSearch 依次尝试（中英文都搜）：
- `Jodie Wen Tsinghua`
- `"Jodie Wen" CISS`
- `文晶 清华 文章`
- `文晶 中国论坛`
- `文晶 China-US Focus`
- `文晶 南华早报` / `Jodie Wen SCMP`
- `site:chinausfocus.com 文晶`

对每条候选：用 FetchURL 打开链接确认是文晶本人署名的文章/评论，记录标题（中英，若只有一种语言则翻译补齐另一字段）、媒体名、日期、URL、原文语种。

规则：
- 只收录核实存在的真实链接；重复链接去重。
- 已知存在但找不到链接的条目：`url` 用 `https://example.com/placeholder-<slug>` 并在文件顶部注释 `<!-- placeholder -->`，同时记入待补充清单。
- 找不到 6 条真实条目时，有几条写几条（≥1 即可继续），差额记入待补充清单。

- [ ] **Step 2: 写条目 Markdown**

每条一个文件，命名 `src/content/publications/<year>-<slug>.md`，frontmatter 模板：

```markdown
---
titleEn: "Article title in English"
titleZh: "文章标题中文"
outlet: "China-US Focus"
date: 2025-06-15
url: "https://example.org/real-article-url"
lang: "en"
---
```

同时删除样例：`rm src/content/publications/000-sample.md`

- [ ] **Step 3: 写 `src/components/PublicationList.astro`**

```astro
---
import type { CollectionEntry } from 'astro:content';
import { ui, type Locale } from '../i18n/ui';

interface Props {
  entries: CollectionEntry<'publications'>[];
  locale: Locale;
}
const { entries, locale } = Astro.props;
const t = ui[locale];

const byYear = new Map<number, CollectionEntry<'publications'>[]>();
for (const e of entries) {
  const y = e.data.date.getFullYear();
  if (!byYear.has(y)) byYear.set(y, []);
  byYear.get(y)!.push(e);
}
const years = [...byYear.keys()].sort((a, b) => b - a);
const fmt = (d: Date) => d.toISOString().slice(0, 10);
---
{entries.length === 0 ? (
  <p class="text-neutral-500">{t['empty']}</p>
) : (
  years.map((year) => (
    <section class="mb-10">
      <h3 class="mb-4 font-serif text-2xl font-semibold">{year}</h3>
      <ul class="space-y-4">
        {byYear.get(year)!.map((e) => (
          <li>
            <a href={e.data.url} target="_blank" rel="noopener" class="text-accent hover:underline">
              {locale === 'zh' ? e.data.titleZh : e.data.titleEn}
            </a>
            <p class="text-sm text-neutral-500">{e.data.outlet} · {fmt(e.data.date)}</p>
          </li>
        ))}
      </ul>
    </section>
  ))
)}
```

- [ ] **Step 4: 写两个 Publications 页面**

`src/pages/publications.astro`:

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../components/BaseLayout.astro';
import SectionHeader from '../components/SectionHeader.astro';
import PublicationList from '../components/PublicationList.astro';
import { ui } from '../i18n/ui';

const locale = 'en' as const;
const t = ui[locale];
const entries = (await getCollection('publications'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
---
<BaseLayout title="Publications — Jodie Wen" locale={locale} description={t['publications.subtitle']}>
  <SectionHeader title={t['publications.title']} subtitle={t['publications.subtitle']} />
  <PublicationList entries={entries} locale={locale} />
</BaseLayout>
```

`src/pages/zh/publications.astro`:

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import PublicationList from '../../components/PublicationList.astro';
import { ui } from '../../i18n/ui';

const locale = 'zh' as const;
const t = ui[locale];
const entries = (await getCollection('publications'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
---
<BaseLayout title="发表 — 文晶" locale={locale} description={t['publications.subtitle']}>
  <SectionHeader title={t['publications.title']} subtitle={t['publications.subtitle']} />
  <PublicationList entries={entries} locale={locale} />
</BaseLayout>
```

- [ ] **Step 5: 首页补回"最新发表"section**

`src/pages/index.astro`：在 frontmatter 顶部追加

```ts
import { getCollection } from 'astro:content';
import PublicationList from '../components/PublicationList.astro';
```

和 frontmatter 内（`outlets` 定义之后）：

```ts
const latest = (await getCollection('publications'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime())
  .slice(0, 3);
```

并在 Book section 之后、Media section 之前插入：

```astro
  <section class="mt-14">
    <SectionHeader title={t['home.publications.title']} />
    <PublicationList entries={latest} locale={locale} />
    <a href={localizePath('/publications', locale)} class="text-sm font-medium text-accent hover:underline">{t['home.viewAll']}</a>
  </section>
```

`src/pages/zh/index.astro` 同样处理（import 路径为 `../../components/...`）。

- [ ] **Step 6: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -o 'target="_blank"' dist/publications/index.html | wc -l` ≥ 条目数；`grep -q '发表文章' dist/zh/publications/index.html` 退出码 0；`dist/` 中不含 `000-sample` 字样（`grep -rq '000-sample' dist/ || echo OK` → 输出 OK）。

- [ ] **Step 7: Commit**

```bash
git add src/
git commit -m "feat: add publications pages with collected article entries"
```

---

### Task 8: Media（联网搜集 + 条目 + MediaCard + 两页）

**Files:**
- Create: `src/components/MediaCard.astro`
- Create: `src/content/media/*.md`（真实条目，目标 ≥4 条视频/采访 + 若干 mention）
- Delete: `src/content/media/000-sample.md`
- Modify: `src/pages/media.astro`、`src/pages/zh/media.astro`

**Interfaces:**
- Consumes: `media` 集合（schema 见 Task 3）。
- Produces: `<MediaCard entry={CollectionEntry<'media'>} locale={Locale} />`。嵌入规则（规格 §6 差异化）：`embedUrl` 存在且非「zh 页 + youtube」、非「en 页 + bilibili」时渲染 iframe；否则渲染链接卡片。

- [ ] **Step 1: 联网搜集采访视频与媒体引用**

WebSearch 查询：
- `文晶 CGTN`
- `Jodie Wen CGTN`
- `文晶 凤凰卫视`
- `Jodie Wen BBC interview`
- `Jodie Wen New York Times`
- `文晶 采访 中东`
- YouTube 搜索 `Jodie Wen` / `文晶`；B站搜索 `文晶`（可用 `https://search.bilibili.com/all?keyword=文晶` 经 FetchURL 或直接 WebSearch `文晶 bilibili`）

嵌入地址格式：
- YouTube：`https://www.youtube.com/embed/<VIDEO_ID>`（`platform: "youtube"`）
- Bilibili：`https://player.bilibili.com/player.html?bvid=<BV号>`（`platform: "bilibili"`）
- CGTN/其他：无嵌入则只填 `url`（`platform: "cgtv"` 或 `"other"`），自动降级为链接卡片。

规则同 Task 7：只收真实核实链接；无法确定是同一人的条目不收；找不到嵌入地址就只填 `url`。

- [ ] **Step 2: 写条目 Markdown 并删样例**

模板（`src/content/media/<year>-<slug>.md`）：

```markdown
---
titleEn: "Interview title in English"
titleZh: "采访标题中文"
type: "video"
outlet: "CGTN"
date: 2025-04-20
url: "https://example.org/real-watch-url"
embedUrl: "https://www.youtube.com/embed/XXXXXXXXXXX"
platform: "youtube"
---
```

媒体引用（无视频）用 `type: "mention"`，无 `embedUrl`。
`rm src/content/media/000-sample.md`

- [ ] **Step 3: 写 `src/components/MediaCard.astro`**

```astro
---
import type { CollectionEntry } from 'astro:content';
import { ui, type Locale } from '../i18n/ui';

interface Props {
  entry: CollectionEntry<'media'>;
  locale: Locale;
}
const { entry, locale } = Astro.props;
const t = ui[locale];
const d = entry.data;
const title = locale === 'zh' ? d.titleZh : d.titleEn;
const embedBlocked =
  (locale === 'zh' && d.platform === 'youtube') ||
  (locale === 'en' && d.platform === 'bilibili');
const showEmbed = Boolean(d.embedUrl) && !embedBlocked;
const fmt = (dt: Date) => dt.toISOString().slice(0, 10);
---
{showEmbed ? (
  <figure class="mb-8">
    <div class="aspect-video w-full overflow-hidden rounded-md bg-neutral-100">
      <iframe src={d.embedUrl!} title={title} class="h-full w-full" allowfullscreen loading="lazy"></iframe>
    </div>
    <figcaption class="mt-2 text-sm text-neutral-600">
      {title} · {d.outlet} · {fmt(d.date)} ·
      <a href={d.url} target="_blank" rel="noopener" class="text-accent hover:underline">{t['link.source']}</a>
    </figcaption>
  </figure>
) : (
  <div class="mb-4 rounded-md border border-neutral-200 p-4">
    <a href={d.url} target="_blank" rel="noopener" class="font-medium text-accent hover:underline">{title}</a>
    <p class="mt-1 text-sm text-neutral-500">{d.outlet} · {fmt(d.date)}</p>
  </div>
)}
```

- [ ] **Step 4: 写两个 Media 页面**

`src/pages/media.astro`:

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../components/BaseLayout.astro';
import SectionHeader from '../components/SectionHeader.astro';
import MediaCard from '../components/MediaCard.astro';
import { ui } from '../i18n/ui';

const locale = 'en' as const;
const t = ui[locale];
const all = (await getCollection('media'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
const features = all.filter((e) => e.data.type === 'video' || e.data.type === 'interview');
const mentions = all.filter((e) => e.data.type === 'mention');
const outlets = ['The New York Times', 'BBC', 'South China Morning Post', 'CGTN', 'Phoenix TV', 'China-US Focus'];
---
<BaseLayout title="Media — Jodie Wen" locale={locale} description="Interviews, videos and media mentions of Dr. Jodie Wen.">
  <SectionHeader title={t['media.title']} />

  <h3 class="mb-6 font-serif text-2xl font-semibold">{t['media.videos']}</h3>
  {features.length === 0
    ? <p class="text-neutral-500">{t['empty']}</p>
    : features.map((e) => <MediaCard entry={e} locale={locale} />)}

  <h3 class="mt-12 mb-6 font-serif text-2xl font-semibold">{t['media.mentions']}</h3>
  {mentions.length === 0
    ? <p class="text-neutral-500">{t['empty']}</p>
    : mentions.map((e) => <MediaCard entry={e} locale={locale} />)}

  <h3 class="mt-12 mb-6 font-serif text-2xl font-semibold">{t['media.wall']}</h3>
  <ul class="flex flex-wrap gap-3">
    {outlets.map((o) => <li class="rounded-md border border-neutral-200 px-3 py-2 text-sm text-neutral-600">{o}</li>)}
  </ul>
</BaseLayout>
```

`src/pages/zh/media.astro`：同上结构，差异：import 用 `../../components/...`、`const locale = 'zh' as const;`、`title="媒体 — 文晶"`、description 用 `"文晶的媒体采访、视频与引用报道。"`、outlets 数组为 `['《纽约时报》', 'BBC', '《南华早报》', 'CGTN', '凤凰卫视', 'China-US Focus']`。

- [ ] **Step 5: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；中文页不含 YouTube iframe：`! grep -q 'youtube.com/embed' dist/zh/media/index.html`；英文页不含 B站 iframe：`! grep -q 'player.bilibili.com' dist/media/index.html`（若搜集中确实没有对应平台条目则自然通过）；`grep -q '合作媒体' dist/zh/media/index.html` 退出码 0。

- [ ] **Step 6: Commit**

```bash
git add src/
git commit -m "feat: add media pages with interview videos and outlet wall"
```

---

### Task 9: Activities（联网搜集 + 条目 + ActivityList + 两页）

**Files:**
- Create: `src/components/ActivityList.astro`
- Create: `src/content/activities/*.md`（真实条目，目标 ≥4 条）
- Delete: `src/content/activities/000-sample.md`
- Modify: `src/pages/activities.astro`、`src/pages/zh/activities.astro`

**Interfaces:**
- Consumes: `activities` 集合（schema 见 Task 3）。
- Produces: `<ActivityList entries={CollectionEntry<'activities'>[]} locale={Locale} />`。

- [ ] **Step 1: 联网搜集论坛/对话活动**

WebSearch 查询：
- `文晶 香山论坛` / `Jodie Wen Xiangshan Forum`
- `文晶 二轨对话`
- `Jodie Wen track II dialogue`
- `文晶 中国论坛 CISS`
- `Jodie Wen Tsinghua forum Middle East`
- 清华 CISS 官网活动报道（`ciss.tsinghua.edu.cn` 相关结果）

只收录有公开报道佐证的活动（论坛官网/新闻稿/机构页面），记录活动名、会议/论坛名、地点、日期、报道 URL。核实不足的记入待补充清单。

- [ ] **Step 2: 写条目 Markdown 并删样例**

模板（`src/content/activities/<year>-<slug>.md`）：

```markdown
---
titleEn: "Panel on Middle East security"
titleZh: "中东安全议题研讨"
event: "Beijing Xiangshan Forum"
location: "Beijing, China"
date: 2025-09-18
url: "https://example.org/real-report-url"
---
```

`rm src/content/activities/000-sample.md`

- [ ] **Step 3: 写 `src/components/ActivityList.astro`**

```astro
---
import type { CollectionEntry } from 'astro:content';
import { ui, type Locale } from '../i18n/ui';

interface Props {
  entries: CollectionEntry<'activities'>[];
  locale: Locale;
}
const { entries, locale } = Astro.props;
const t = ui[locale];
const fmt = (d: Date) => d.toISOString().slice(0, 10);
---
{entries.length === 0 ? (
  <p class="text-neutral-500">{t['empty']}</p>
) : (
  <ul class="space-y-6">
    {entries.map((e) => (
      <li class="border-l-2 border-accent pl-4">
        <h3 class="font-semibold">{locale === 'zh' ? e.data.titleZh : e.data.titleEn}</h3>
        <p class="mt-1 text-sm text-neutral-600">{e.data.event} · {e.data.location} · {fmt(e.data.date)}</p>
        {e.data.url && (
          <a href={e.data.url} target="_blank" rel="noopener" class="text-sm text-accent hover:underline">{t['link.source']}</a>
        )}
      </li>
    ))}
  </ul>
)}
```

- [ ] **Step 4: 写两个 Activities 页面**

`src/pages/activities.astro`:

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../components/BaseLayout.astro';
import SectionHeader from '../components/SectionHeader.astro';
import ActivityList from '../components/ActivityList.astro';
import { ui } from '../i18n/ui';

const locale = 'en' as const;
const t = ui[locale];
const entries = (await getCollection('activities'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
---
<BaseLayout title="Activities — Jodie Wen" locale={locale} description={t['activities.subtitle']}>
  <SectionHeader title={t['activities.title']} subtitle={t['activities.subtitle']} />
  <ActivityList entries={entries} locale={locale} />
</BaseLayout>
```

`src/pages/zh/activities.astro`：同上结构，差异：import `../../components/...`、`const locale = 'zh' as const;`、`title="活动 — 文晶"`。

- [ ] **Step 5: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -q '学术活动' dist/zh/activities/index.html` 退出码 0；`grep -q 'Track II' dist/activities/index.html` 退出码 0。

- [ ] **Step 6: Commit**

```bash
git add src/
git commit -m "feat: add activities pages with forum and dialogue entries"
```

---

### Task 10: 文晶Talk 页（中英两页）

**Files:**
- Create: `src/components/TalkIntro.astro`
- Modify: `src/pages/talk.astro`、`src/pages/zh/talk.astro`

**Interfaces:**
- Consumes: `BaseLayout`、`SectionHeader`。
- Produces: `<TalkIntro locale={Locale} links={{ label: string; url: string }[]} />`（slot 放介绍 prose；links 为空时渲染空态文案）。

- [ ] **Step 1: 联网搜索「文晶Talk」平台与代表内容**

WebSearch：`文晶Talk`、`文晶Talk 公众号`、`文晶Talk 视频号`、`文晶 自媒体`、`文晶 播客`。
能确认的代表内容链接收入页面 `links`；确认不到就传空数组（渲染空态），记入待补充清单。

- [ ] **Step 2: 写 `src/components/TalkIntro.astro`**

```astro
---
import { ui, type Locale } from '../i18n/ui';

interface Props {
  locale: Locale;
  links: { label: string; url: string }[];
}
const { locale, links } = Astro.props;
const t = ui[locale];
---
<div class="measure">
  <slot />
  {links.length === 0 ? (
    <p class="mt-6 text-neutral-500">{t['empty']}</p>
  ) : (
    <ul class="mt-6 space-y-3">
      {links.map((l) => (
        <li>
          <a href={l.url} target="_blank" rel="noopener" class="text-accent hover:underline">{l.label}</a>
        </li>
      ))}
    </ul>
  )}
</div>
```

- [ ] **Step 3: 写两个 Talk 页面**

`src/pages/talk.astro`:

```astro
---
import BaseLayout from '../components/BaseLayout.astro';
import SectionHeader from '../components/SectionHeader.astro';
import TalkIntro from '../components/TalkIntro.astro';
import { ui } from '../i18n/ui';

const locale = 'en' as const;
const t = ui[locale];
const links: { label: string; url: string }[] = [
  // 填入 Step 1 核实的链接；无则保持空数组
];
---
<BaseLayout title="Wenjing Talk — Jodie Wen" locale={locale} description="Wenjing Talk, the independent media brand founded by Jodie Wen.">
  <SectionHeader title={t['talk.title']} />
  <TalkIntro locale={locale} links={links}>
    <p class="text-neutral-700">Wenjing Talk (文晶Talk) is the independent media brand founded by Dr. Jodie Wen during her years as a senior journalist. It features her reporting and commentary on international affairs, with a focus on the Middle East, drawn from fieldwork across more than 40 countries in Europe, Asia, and the Middle East.</p>
  </TalkIntro>
</BaseLayout>
```

`src/pages/zh/talk.astro`:

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import TalkIntro from '../../components/TalkIntro.astro';
import { ui } from '../../i18n/ui';

const locale = 'zh' as const;
const t = ui[locale];
const links: { label: string; url: string }[] = [
  // 填入 Step 1 核实的链接；无则保持空数组
];
---
<BaseLayout title="文晶Talk — 文晶" locale={locale} description="文晶创办的自媒体品牌「文晶Talk」。">
  <SectionHeader title={t['talk.title']} />
  <TalkIntro locale={locale} links={links}>
    <p class="text-neutral-700">「文晶Talk」是文晶在资深媒体人生涯中创办的个人自媒体品牌，聚焦国际议题尤其是中东方向的新闻报道与评论，素材来自她在欧美、中东和东南亚 40 多个国家的田野调查与一线报道。</p>
  </TalkIntro>
</BaseLayout>
```

- [ ] **Step 4: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -q '文晶Talk' dist/zh/talk/index.html` 与 `grep -q 'Wenjing Talk' dist/talk/index.html` 退出码 0；links 为空时 `grep -q '内容整理中' dist/zh/talk/index.html` 退出码 0（空态渲染）。

- [ ] **Step 5: Commit**

```bash
git add src/
git commit -m "feat: add Wenjing Talk pages"
```

---

### Task 11: Contact 页（中英两页）

**Files:**
- Create: `src/components/ContactBlock.astro`
- Modify: `src/pages/contact.astro`、`src/pages/zh/contact.astro`

**Interfaces:**
- Consumes: `BaseLayout`、`SectionHeader`、ui 字典 `contact.*`。
- Produces: `<ContactBlock locale={Locale} />`。

- [ ] **Step 1: 写 `src/components/ContactBlock.astro`**

```astro
---
import { ui, type Locale } from '../i18n/ui';

interface Props {
  locale: Locale;
}
const { locale } = Astro.props;
const t = ui[locale];
---
<div class="space-y-8">
  <div>
    <h3 class="text-sm font-semibold uppercase tracking-wide text-neutral-500">{t['contact.email']}</h3>
    <a href="mailto:jodiewen@tsinghua.edu.cn" class="mt-2 inline-block text-lg text-accent hover:underline">jodiewen@tsinghua.edu.cn</a>
  </div>
  <div>
    <h3 class="text-sm font-semibold uppercase tracking-wide text-neutral-500">{t['contact.affiliation']}</h3>
    <p class="mt-2 text-lg">{t['contact.affiliation.value']}</p>
  </div>
</div>
```

- [ ] **Step 2: 写两个 Contact 页面**

`src/pages/contact.astro`:

```astro
---
import BaseLayout from '../components/BaseLayout.astro';
import SectionHeader from '../components/SectionHeader.astro';
import ContactBlock from '../components/ContactBlock.astro';
import { ui } from '../i18n/ui';

const locale = 'en' as const;
const t = ui[locale];
---
<BaseLayout title="Contact — Jodie Wen" locale={locale} description="Contact information for Dr. Jodie Wen.">
  <SectionHeader title={t['contact.title']} />
  <ContactBlock locale={locale} />
</BaseLayout>
```

`src/pages/zh/contact.astro`：同上结构，差异：import `../../components/...`、`const locale = 'zh' as const;`、`title="联系 — 文晶"`、description 用 `"文晶的联系方式。"`。

- [ ] **Step 3: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -q 'mailto:jodiewen@tsinghua.edu.cn' dist/contact/index.html` 与 `grep -q '清华大学战略与安全研究中心' dist/zh/contact/index.html` 退出码 0。

- [ ] **Step 4: Commit**

```bash
git add src/
git commit -m "feat: add contact pages"
```

---

### Task 12: 终验 + 待补充素材清单 + 文档更新

**Files:**
- Create: `docs/pending-assets.md`
- Modify: `PROGRESS.md`
- Modify: `AGENTS.md`（§2 当前状态、§5 命令已生效）

**Interfaces:**
- Consumes: 全部前序任务产物。
- Produces: 可交付的静态站点与交接文档。

- [ ] **Step 1: 全量构建与类型检查**

Run: `npm run build && npx astro check`
Expected: 成功，`0 errors`。

- [ ] **Step 2: 16 路由全部可达**

```bash
for f in index about book publications media activities talk contact; do
  test -f "dist/$f/index.html" || { echo "MISSING dist/$f/index.html"; exit 1; }
  test -f "dist/zh/$f/index.html" || { echo "MISSING dist/zh/$f/index.html"; exit 1; }
done
echo "ALL 16 ROUTES OK"
```

Expected: 输出 `ALL 16 ROUTES OK`。

- [ ] **Step 3: 每页语言切换链接成对正确**

```bash
for f in about book publications media activities talk contact; do
  grep -q "href=\"/zh/$f" "dist/$f/index.html" || { echo "EN->ZH link missing: $f"; exit 1; }
  grep -q "href=\"/$f" "dist/zh/$f/index.html" || { echo "ZH->EN link missing: $f"; exit 1; }
done
grep -q 'href="/zh/"' dist/index.html || { echo "EN->ZH link missing: index"; exit 1; }
grep -q 'href="/"' dist/zh/index.html || { echo "ZH->EN link missing: index"; exit 1; }
echo "LANG SWITCH LINKS OK"
```

（说明：构建产物中的 href 带尾部斜杠，如 `/zh/about/`，故用前缀匹配；`href="/` 开头的引号保证 zh 页检查不会误匹配 `/zh/...` 链接。）

Expected: 输出 `LANG SWITCH LINKS OK`。

- [ ] **Step 4: 坏数据 schema 负向复验**

临时写 `src/content/media/999-bad.md`（缺 `platform` 字段）：

```markdown
---
titleEn: "Bad"
titleZh: "坏"
type: "video"
outlet: "Bad"
date: 2026-01-01
url: "https://example.com/bad"
---
```

Run: `npm run build` → Expected: **失败**，报错含 `platform`。
然后 `rm src/content/media/999-bad.md && npm run build` → Expected: 恢复成功。

- [ ] **Step 5: 外链抽查可达性**

从 `dist/` 提取全部外链，去重后抽查前 10 条：

```bash
grep -rhoE 'href="https://[^"]+' dist/ | sed 's/href="//' | sort -u | grep -v 'example.com/placeholder' | head -10 | while read -r u; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -x http://127.0.0.1:7890 -L --max-time 15 "$u" || echo "FAIL")
  echo "$code $u"
done
```

Expected: 大部分返回 200/301/302/403（媒体站常有反爬 403，可接受）；404/域名不存在的链接必须回到对应内容条目修正或降级为占位符并记入清单。

- [ ] **Step 6: 写 `docs/pending-assets.md`（待补充素材清单）**

结构：

```markdown
# 待补充素材清单

> 交付时由用户补充；每条注明在网站中的位置。

## 图片
- [ ] 肖像照（首页 Hero、About 页）— 当前为灰色占位块
- [ ] 《美国的中东政策研究（2009-2017）》书封图（首页、Book 页）— 当前为灰色占位块

## 链接
- [ ] 书籍购买/出版社链接（Book 页）
- [ ] 文晶Talk 平台与代表内容链接（Talk 页）
- [ ] （按实际搜集中未找到的条目列出，注明对应 content 文件中的 placeholder URL）

## 内容缺口
- [ ] （搜集中未能核实的文章/采访/活动条目列表）
```

按 Task 6–10 实际搜集结果填全后两项。

- [ ] **Step 7: 更新 `PROGRESS.md` 与 `AGENTS.md`**

`PROGRESS.md`：当前状态改为「已实现并构建通过」，列出构建/验证命令与待补充素材清单位置。
`AGENTS.md` §2：当前状态改为实现完成，说明目录结构已按 §4 落地、命令已生效；删除「尚无 package.json」等过时表述。

- [ ] **Step 8: 人工页面走查（交给用户）**

Run: `npm run dev`，请用户在浏览器检查：
1. 8 页 × 2 语言逐页浏览；
2. 375px（手机）与 1280px（桌面）宽度布局；
3. 每页语言切换跳到对应另一语言同页；
4. 视频嵌入/链接卡片降级表现正常。

- [ ] **Step 9: Commit**

```bash
git add docs/pending-assets.md PROGRESS.md AGENTS.md src/
git commit -m "docs: add pending assets checklist and update project docs"
```

---

## Self-Review 记录

- **Spec coverage：** §4.1 路由/i18n → Task 2；§4.2 八页 → Task 4–11；§4.3 内容模型 → Task 3；§4.4 组件 → Task 2/4/5/7/8/9/10/11；§5 视觉 → Task 1 global.css + 各组件类名；§6 素材搜集 → Task 6/7/8/9/10 Step 1；§7 错误处理 → Task 3 schema、MediaCard 降级、各列表空态、Task 12 外链抽查；§8 验证 → Task 12；§9 YAGNI → Global Constraints 红线。
- **Placeholder scan：** 全部代码步骤均含完整代码；Task 4 首页不含"最新发表"section（依赖 Task 7 组件，由 Task 7 Step 5 补回），已在步骤内显式说明，无跨任务模糊引用。
- **Type consistency：** 组件 props 与 ui 字典 key 在定义处（Task 2）与使用处（Task 4–11）逐一核对一致；集合字段名与 Task 3 schema 一致；`MediaCard` 中 `embedUrl` 为 optional，iframe 分支用 `d.embedUrl!` 断言（`showEmbed` 已保证存在），通过 strict 检查。
- **验证命令可执行性：** 构建产物 href 带尾部斜杠（`/zh/about/`），所有 grep 断言均按前缀匹配编写；外链计数用 `grep -o ... | wc -l`。
