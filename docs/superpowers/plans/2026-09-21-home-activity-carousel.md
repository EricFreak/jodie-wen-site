# 首页「近期活动」轮播版块 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在三语首页的媒体报道版块之下新增「近期活动」横向滑动卡片区，展示有封面图和外链的活动，点击跳转活动报道外链。

**Architecture:** `activities` 集合 schema 增加可选 `cover` 字段；封面图从各活动 frontmatter 已有的 CISS 公开报道页抓取、压缩后存入 `public/images/activities/`；新组件 `ActivityCarousel.astro` 用纯 CSS scroll-snap 实现横向滑动（零客户端 JS）；三个首页（en/zh/ar）以相同方式接入。

**Tech Stack:** Astro 5 + Content Collections (zod) + Tailwind CSS 4（`@tailwindcss/vite`）；macOS 自带 `sips` 做图片压缩；无测试框架，验证以 `npm run build` + `npx astro check` + 人工走查为准。

**参考规格：** `docs/superpowers/specs/2026-09-21-home-activity-carousel-design.md`

## Global Constraints

- 零客户端 JS：轮播只用 CSS `overflow-x-auto` + `scroll-snap`，不写任何 `<script>`
- 外链一律 `target="_blank" rel="noopener"`
- 方向相关样式一律用 Tailwind 逻辑属性（`ms-/me-/ps-/pe-/start-/end-`），阿语 RTL 自然适配
- 视觉沿用现状：黑白灰 + 深青 `#0F766E`（`accent`）、卡片样式对齐 `VideoCard.astro` 纵向卡片
- 首页只展示**同时有 `cover` 和 `url`** 的活动，按 `date` 倒序；一条都没有时整个版块（含标题与 View all）不渲染
- 标题取 `locale === 'zh' ? titleZh : titleEn`（与 `src/components/ActivityList.astro:19` 的阿语回退一致）；地点同理取 `locationZh`/`location`
- 不改动 `/activities` 页面及 `ActivityList.astro`
- 每个 Task 完成后按步骤提交 git commit

---

### Task 1: activities schema 增加 `cover` 字段 + 三语 UI 词条

**Files:**
- Modify: `src/content.config.ts:34-46`（activities 集合 schema）
- Modify: `src/i18n/ui.ts`（三个 locale 字典各加 2 个词条）

**Interfaces:**
- Produces:
  - `activities` 条目 `data.cover?: string`（本地路径，形如 `/images/activities/<slug>.jpg`）
  - UI 词条 `home.activities.title`、`home.activities.subtitle`（en/zh/ar 三语），Task 4 的首页使用；View all 复用已有 `home.viewAll`

- [ ] **Step 1: 修改 `src/content.config.ts` 的 activities schema**

在 `url: z.string().url().optional(),` 之后加一行：

```ts
    url: z.string().url().optional(),
    cover: z.string().optional(),
```

- [ ] **Step 2: 在 `src/i18n/ui.ts` 三个 locale 各加词条**

英文（`home.media.title` 行之后）：

```ts
    'home.activities.title': 'Activities',
    'home.activities.subtitle': 'Recent forums and events',
```

中文：

```ts
    'home.activities.title': '活动动态',
    'home.activities.subtitle': '近期论坛与活动',
```

阿语（AI 翻译，待用户校对）：

```ts
    'home.activities.title': 'الأنشطة',
    'home.activities.subtitle': 'منتديات وفعاليات حديثة',
```

- [ ] **Step 3: 验证构建与类型**

Run: `npx astro check && npm run build`
Expected: 类型检查无错误，构建成功（现有 24 路由）

- [ ] **Step 4: Commit**

```bash
git add src/content.config.ts src/i18n/ui.ts
git commit -m "feat: add optional cover field to activities and trilingual home.activities strings"
```

---

### Task 2: 抓取活动封面图并写入 frontmatter

**Files:**
- Create: `public/images/activities/<slug>.jpg`（每个成功抓图的活动一张）
- Modify: `src/content/activities/*.md`（仅成功抓图的活动加 `cover` 行）

**Interfaces:**
- Consumes: Task 1 的 `cover?: string` 字段
- Produces: 若干活动条目的 frontmatter 含 `cover: "/images/activities/<slug>.jpg"`，且对应文件真实存在；Task 4 的首页过滤条件 `cover && url` 依赖此

**背景：** 7 个活动条目的 `url` 均为 CISS 官网报道页（`https://ciss.tsinghua.edu.cn/...`，见各 `.md` frontmatter）。目标是至少 3 场活动拿到封面（首页桌面一行 3 张）；找不到合适图片的活动**跳过**，不加 `cover`，并在 commit message 或交付说明里记录。

- [ ] **Step 1: 抓取每个报道页的 HTML，列出候选图片**

对每个活动 URL 执行（以 2026-dalian-summer-davos 为例）：

```bash
curl -sL "https://ciss.tsinghua.edu.cn/info/yw/2000000012559" -o /tmp/ciss-page.html
grep -oE '(src|data-src)="[^"]+\.(jpg|jpeg|png)[^"]*"' /tmp/ciss-page.html | head -20
```

CISS 页面图片多为 `/__local/.../xxx.jpg` 相对路径，需拼上 `https://ciss.tsinghua.edu.cn` 前缀。挑正文里尺寸最大的现场照片（跳过 logo、二维码、装饰图）。

- [ ] **Step 2: 下载、压缩、落盘**

每张选定的图：

```bash
mkdir -p public/images/activities
curl -sL "<图片完整URL>" -o /tmp/cover-raw.jpg
sips -Z 1200 -s format jpeg -s formatOptions 80 /tmp/cover-raw.jpg --out "public/images/activities/<slug>.jpg"
sips -g pixelWidth -g pixelHeight "public/images/activities/<slug>.jpg"
```

Expected: 输出宽度 ≤1200 的 JPEG；文件大小一般 < 300KB。若 `sips` 报 `not a valid image`，说明抓到的是 webp 或 HTML 错误页，换候选图重试。

- [ ] **Step 3: 给成功的活动加 frontmatter**

在对应 `src/content/activities/<slug>.md` 的 `url:` 行后加：

```yaml
cover: "/images/activities/<slug>.jpg"
```

- [ ] **Step 4: 验证**

Run: `npm run build`
Expected: 构建成功；`ls public/images/activities/` 中每个文件都有对应 frontmatter `cover` 条目，且路径拼写一致

- [ ] **Step 5: Commit**

```bash
git add public/images/activities src/content/activities
git commit -m "feat: add scraped cover images for N activities (skipped: <没抓到的 slug 列表>)"
```

---

### Task 3: ActivityCarousel 组件

**Files:**
- Create: `src/components/ActivityCarousel.astro`

**Interfaces:**
- Consumes: Task 1 的 `cover` 字段类型
- Produces: 组件 `ActivityCarousel`，Props 为 `{ entries: CollectionEntry<'activities'>[]; locale: Locale }`；调用方负责过滤（`cover && url`）与排序，组件只渲染。Task 4 的三个首页都引用它

- [ ] **Step 1: 创建组件**

```astro
---
import type { CollectionEntry } from 'astro:content';
import type { Locale } from '../i18n/ui';

interface Props {
  entries: CollectionEntry<'activities'>[];
  locale: Locale;
}
const { entries, locale } = Astro.props;
const fmt = (dt: Date) => dt.toISOString().slice(0, 10);
---
<div class="-mx-4 overflow-x-auto px-4 [scroll-snap-type:x_mandatory] sm:mx-0 sm:px-0">
  <div class="flex gap-5 pb-2">
    {entries.map((e) => {
      const d = e.data;
      const title = locale === 'zh' ? d.titleZh : d.titleEn;
      const location = locale === 'zh' ? d.locationZh : d.location;
      return (
        <a
          href={d.url}
          target="_blank"
          rel="noopener"
          class="group w-[85%] shrink-0 overflow-hidden rounded-lg border border-neutral-200 bg-white transition-shadow [scroll-snap-align:start] hover:shadow-md sm:w-[calc((100%-1.25rem)/2)] lg:w-[calc((100%-2.5rem)/3)]"
        >
          <div class="aspect-video overflow-hidden">
            <img src={d.cover} alt="" loading="lazy" class="h-full w-full object-cover" />
          </div>
          <div class="p-3.5">
            <p class="line-clamp-2 text-sm leading-snug font-medium text-neutral-800">{title}</p>
            <p class="mt-1.5 text-xs text-neutral-500">{location} · {fmt(d.date)}</p>
          </div>
        </a>
      );
    })}
  </div>
</div>
```

说明：移动端卡片 85% 宽露出下一张边缘；sm 一行 2 张、lg 一行 3 张（gap-5 = 1.25rem）；`-mx-4 px-4` 让移动端滑动时图片贴边，与 BaseLayout 主容器 padding 抵消（若 BaseLayout 主容器 padding 不是 1rem，按实际值调整这两个类）。

- [ ] **Step 2: 验证类型**

Run: `npx astro check`
Expected: 无类型错误（组件暂未被引用也纳入检查）

- [ ] **Step 3: Commit**

```bash
git add src/components/ActivityCarousel.astro
git commit -m "feat: add ActivityCarousel component (pure CSS scroll-snap, zero JS)"
```

---

### Task 4: 三语首页接入轮播版块

**Files:**
- Modify: `src/pages/index.astro`
- Modify: `src/pages/zh/index.astro`
- Modify: `src/pages/ar/index.astro`

**Interfaces:**
- Consumes: Task 2 的 `cover` 数据、Task 3 的 `ActivityCarousel` 组件（Props `{ entries, locale }`）、Task 1 的 `home.activities.*` 词条
- Produces: 三语首页在媒体报道版块与 More about Jodie 之间出现活动轮播

三个文件结构相同（仅 import 路径深度与 `locale` 常量不同），以下以英文页为例，zh/ar 页做同样改动（import 用 `../../` 前缀）。

- [ ] **Step 1: 英文页 `src/pages/index.astro` — frontmatter 加数据查询与 import**

在 frontmatter 的 import 区加：

```ts
import ActivityCarousel from '../components/ActivityCarousel.astro';
```

在 `photos` 查询之后加：

```ts
// 首页活动轮播：仅展示同时有封面图与外链的活动，按日期倒序
const activities = (await getCollection('activities'))
  .filter((e) => e.data.cover && e.data.url)
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
```

- [ ] **Step 2: 英文页 — 在媒体版块 `</section>` 之后、More about Jodie `<section>` 之前插入**

```astro
  {activities.length > 0 && (
    <section class="mt-14">
      <div class="flex items-start justify-between gap-4">
        <SectionHeader title={t['home.activities.title']} subtitle={t['home.activities.subtitle']} />
        <a href={localizePath('/activities', locale)} class="mt-2 shrink-0 text-sm font-medium text-accent hover:underline">{t['home.viewAll']}</a>
      </div>
      <ActivityCarousel entries={activities} locale={locale} />
    </section>
  )}
```

- [ ] **Step 3: zh、ar 首页做同样改动**

`src/pages/zh/index.astro`：`locale` 已是 `'zh'`，import 路径前缀为 `../../`，插入位置与英文页相同（媒体版块后、`home.moreAbout` 版块前）。
`src/pages/ar/index.astro`：同上，`locale` 为 `'ar'`。

- [ ] **Step 4: 验证构建与类型**

Run: `npx astro check && npm run build`
Expected: 无错误，24 路由构建成功

- [ ] **Step 5: 抽查构建产物**

```bash
grep -l "ActivityCarousel\|scroll-snap\|活动动态\|الأنشطة" dist/index.html dist/zh/index.html dist/ar/index.html
grep -o 'href="[^"]*activities[^"]*"' dist/zh/index.html | head -3
```

Expected: 三个首页产物都包含版块标记；中文页 View all 指向 `/zh/activities`（阿语页指向 `/ar/activities`，英文页 `/activities`）；卡片链接含 `target="_blank"`

- [ ] **Step 6: Commit**

```bash
git add src/pages/index.astro src/pages/zh/index.astro src/pages/ar/index.astro
git commit -m "feat: add activities carousel section to trilingual homepages"
```

---

### Task 5: 端到端验证（人工走查 + 空态验证）

**Files:**
- 无新增（验证用临时改动需还原）

**Interfaces:**
- Consumes: Task 1-4 的全部产出

- [ ] **Step 1: 空态验证（验证后还原）**

```bash
mv public/images/activities /tmp/activities-covers-bak
# 临时把所有活动 .md 里的 cover 行注释掉（或 git stash 方式）后：
npm run build && grep -c "home.activities\|活动动态" dist/index.html
```

Expected: 版块不渲染（grep 计数为 0）。随后还原：`mv /tmp/activities-covers-bak public/images/activities`，恢复 frontmatter，`npm run build` 重新构建确认版块回来。

- [ ] **Step 2: 本地预览人工走查**

Run: `npm run dev`，浏览器检查：

1. `/`、`/zh/`、`/ar/` 三个首页：版块出现在媒体报道之下、More about Jodie 之上
2. 1280px 宽度：一行约 3 张卡片；375px：卡片约 85% 宽、可横向滑动、露出下一张边缘
3. 阿语首页 RTL：卡片从右往左排、滑动方向自然
4. 点击卡片新开标签页到 CISS 报道外链；View all 指向对应语言 activities 页
5. 中文页卡片显示 `titleZh`/`locationZh`，英文与阿语页显示 `titleEn`/`location`

- [ ] **Step 3: 封面图抽查**

确认每张卡片封面真实加载（无 404）、图片内容与活动相关、无 logo/二维码误抓。若有误抓，替换对应 `public/images/activities/<slug>.jpg` 或删除该条目的 `cover` 字段。

- [ ] **Step 4: 最终提交与收尾**

```bash
npm run build && npx astro check
git status   # 确认无未提交的临时改动
```

Expected: 构建与类型检查全绿，工作区干净。向用户汇报：成功配封面的活动数、跳过的活动及原因、待用户后续替换素材的说明（替换 `public/images/activities/` 同名文件即可）。
