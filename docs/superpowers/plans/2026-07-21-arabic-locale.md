# 阿拉伯语第三语言版 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按已批准的规格为网站增加阿拉伯语第三语言（`/ar/` 前缀，8 页全量对应，RTL 布局，三向语言切换）。

**Architecture:** Astro i18n 增加 `ar` locale；UI 字典增 ar 全文；逻辑属性改造实现 RTL（一套 class 双向适配）；新增 `src/pages/ar/` 8 个页面（长文阿语翻译，内容条目保持英文标题）。

**Tech Stack:** Astro 5、TypeScript、Tailwind CSS v4（逻辑属性工具类）。

**规格文档:** `docs/superpowers/specs/2026-07-21-arabic-locale-design.md`（唯一依据）。

## Global Constraints

- i18n：`locales: ['en', 'zh', 'ar']`，`defaultLocale: 'en'`，`prefixDefaultLocale: false`；阿语路径形式 `/ar/about`。
- 阿语页 `<html lang="ar" dir="rtl">`；中英页 `dir="ltr"`（显式声明，行为不变）。
- RTL 只用 **Tailwind 逻辑属性**（`ps/pe/ms/me/start/end/border-s/border-e/text-start/text-end`）；**禁止** `rtl:` 变体、禁止在 global.css 写 `[dir="rtl"]` 覆盖。
- 不引网络字体；日期保持 ISO（YYYY-MM-DD）；23 条内容条目在阿语页保持英文标题，不新增阿语字段；书籍中文书名《美国的中东政策研究（2009-2017）》阿语页保留中文原名。
- 品牌名保留拉丁字母：Wenjing Talk（阿语页同样用拉丁写法）。
- 零客户端 JS；所有外链 `target="_blank" rel="noopener"`；YAGNI（规格 §6）：不翻条目标题、不做阿语数字/日期本地化、不做 hreflang、不做语言自动探测。
- 验证基线：`npm run build` 成功 + `npx astro check` 0 错误 + 对 `dist/` 产物的 grep 断言。
- 提交：每任务末尾 commit，conventional commits 英文消息。
- MediaCard 嵌入规则：zh 页禁 YouTube iframe；**非 zh 页（含 ar）禁 bilibili iframe**；无 embedUrl 一律链接卡片。
- 字典 `ui` 三个 locale 的 key 集合必须完全一致（TypeScript `as const` 强制）；`lang.switch` 键随三向切换器上线从三个字典中一并删除。

## 文件结构

```
修改：
├── astro.config.mjs                  # Task 1：locales 加 'ar'
├── src/i18n/ui.ts                    # Task 1：locales/类型加 'ar'、ar 字典、删 lang.switch
├── src/i18n/utils.ts                 # Task 1：重写（stripLocalePrefix 新增，getAlternatePath 删除）
├── src/components/Nav.astro          # Task 1：三向语言切换器
├── src/components/BaseLayout.astro   # Task 1：html lang + dir
├── src/components/TimelineItem.astro # Task 2：逻辑属性
├── src/components/ActivityList.astro # Task 2：逻辑属性
├── src/components/MediaCard.astro    # Task 2：bilibili 规则 zh→非zh
├── src/components/Hero.astro         # Task 4：credentials 三向
新增：
└── src/pages/ar/
    ├── index.astro                   # Task 1 桩页 → Task 4 正式
    ├── about.astro                   # Task 1 桩页 → Task 3 正式
    ├── book.astro                    # Task 1 桩页 → Task 3 正式
    ├── talk.astro                    # Task 1 桩页 → Task 3 正式
    ├── publications.astro            # Task 1 桩页 → Task 4 正式
    ├── media.astro                   # Task 1 桩页 → Task 4 正式
    ├── activities.astro              # Task 1 桩页 → Task 4 正式
    └── contact.astro                 # Task 1 桩页 → Task 4 正式
文档：AGENTS.md、PROGRESS.md（Task 5 更新）
```

---

### Task 1: 三语 i18n 基建 + 三向语言切换 + BaseLayout dir + ar 桩页

**Files:**
- Modify: `astro.config.mjs`
- Modify: `src/i18n/ui.ts`
- Modify: `src/i18n/utils.ts`
- Modify: `src/components/Nav.astro`
- Modify: `src/components/BaseLayout.astro`
- Create: `src/pages/ar/{index,about,book,publications,media,activities,talk,contact}.astro`（桩页）

**Interfaces:**
- Consumes: 现有 en/zh 字典与组件。
- Produces:
  - `ui.ts`：`locales = ['en','zh','ar'] as const`；`Locale`；`defaultLocale`；`ui.en/zh/ar`（key 完全一致，无 `lang.switch`）；后续任务使用 ar 字典全部 key。
  - `utils.ts`：`getLocaleFromPath(pathname): Locale`、`stripLocalePrefix(pathname): string`、`localizePath(path, locale): string`（**不再有** `getAlternatePath`）。
  - `<BaseLayout>` 按 locale 输出 `lang` 与 `dir`；Nav 三向切换器渲染 EN/中文/العربية。

- [ ] **Step 1: `astro.config.mjs` locales 加 'ar'**

把 `locales: ['en', 'zh'],` 改为：

```js
    locales: ['en', 'zh', 'ar'],
```

- [ ] **Step 2: 重写 `src/i18n/ui.ts`（全文替换）**

```ts
export const locales = ['en', 'zh', 'ar'] as const;
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
    'footer.rights': 'All rights reserved.',
    'hero.kicker': 'Fellow, Center for International Security and Strategy (CISS), Tsinghua University',
    'hero.tagline': 'Scholar of U.S. foreign policy and Middle East politics; former senior journalist covering 40+ countries.',
    'hero.bio': 'She is the author of Studies of U.S. Middle East Policy (2009–2017), and a frequent commentator for The New York Times, BBC, CGTN and other leading outlets.',
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
    'footer.rights': '版权所有。',
    'hero.kicker': '清华大学战略与安全研究中心研究员、中国论坛国际传播主任',
    'hero.tagline': '美国外交与中东政治研究者；资深媒体人，曾在 40 余国进行新闻报道与田野调查。',
    'hero.bio': '著有《美国的中东政策研究（2009-2017）》，常应《纽约时报》、BBC、CGTN 等媒体之邀提供分析评论。',
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
  ar: {
    'nav.home': 'الرئيسية',
    'nav.about': 'نبذة عني',
    'nav.book': 'الكتاب',
    'nav.publications': 'المنشورات',
    'nav.media': 'وسائل الإعلام',
    'nav.activities': 'الأنشطة',
    'nav.talk': 'Wenjing Talk',
    'nav.contact': 'تواصل',
    'footer.rights': 'جميع الحقوق محفوظة.',
    'hero.kicker': 'باحثة في مركز الأمن الدولي والاستراتيجية (CISS) بجامعة تسينغهوا، ومديرة التواصل الدولي في منتدى الصين',
    'hero.tagline': 'باحثة في السياسة الخارجية الأمريكية وسياسات الشرق الأوسط؛ إعلامية مخضرمة غطّت أكثر من 40 دولة.',
    'hero.bio': 'مؤلفة كتاب «دراسات سياسة الولايات المتحدة في الشرق الأوسط (2009-2017)»، ومساهِمة دائمة بالتحليل والتعليق لدى نيويورك تايمز وBBC وCGTN وغيرها من كبريات وسائل الإعلام.',
    'hero.cta.book': 'الكتاب',
    'hero.cta.contact': 'تواصل معي',
    'home.book.title': 'الكتاب',
    'home.publications.title': 'أحدث المنشورات',
    'home.media.title': 'في وسائل الإعلام',
    'home.viewAll': 'عرض الكل ←',
    'publications.title': 'المنشورات',
    'publications.subtitle': 'مقالات وتعليقات منشورة في وسائل إعلام دولية',
    'media.title': 'وسائل الإعلام',
    'media.videos': 'مقابلات وفيديوهات',
    'media.mentions': 'إشارات في وسائل الإعلام',
    'media.wall': 'ظهرت في',
    'activities.title': 'الأنشطة',
    'activities.subtitle': 'منتديات دولية وحوارات المسار الثاني',
    'talk.title': 'Wenjing Talk',
    'contact.title': 'التواصل',
    'contact.email': 'البريد الإلكتروني',
    'contact.affiliation': 'الجهة',
    'contact.affiliation.value': 'مركز الأمن الدولي والاستراتيجية (CISS)، جامعة تسينغهوا، بكين، الصين',
    'link.source': 'المصدر',
    'empty': 'المحتوى قيد الإعداد.',
  },
} as const;
```

注意：`lang.switch` 键已从三个字典删除（三向切换器用固定语言名，见 Task 1 Step 4）；若构建报某处仍引用 `lang.switch`，说明有遗漏调用点，先找到并改为本任务 Step 4 的切换器写法。

- [ ] **Step 3: 重写 `src/i18n/utils.ts`（全文替换）**

```ts
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
```

- [ ] **Step 4: `Nav.astro` 三向语言切换器**

`Nav.astro` frontmatter 中，删除 `getAlternatePath` 的 import 与 `const alternatePath = ...`，改为：

```astro
---
import { ui, locales, type Locale } from '../i18n/ui';
import { localizePath, stripLocalePrefix } from '../i18n/utils';

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
const neutralPath = stripLocalePrefix(currentPath);
const langNames: Record<Locale, string> = { en: 'EN', zh: '中文', ar: 'العربية' };
---
```

模板中把语言切换 `<li>`（原来单个 `t['lang.switch']` 链接）替换为：

```astro
      <li class="flex items-center gap-3">
        {locales.map((loc) =>
          loc === locale ? (
            <span class="py-1 text-sm font-semibold text-accent">{langNames[loc]}</span>
          ) : (
            <a href={localizePath(neutralPath, loc)} class="py-1 text-sm text-neutral-700 hover:text-accent">
              {langNames[loc]}
            </a>
          ),
        )}
      </li>
```

其余模板（品牌、汉堡 checkbox、菜单容器、导航项渲染、`aria-current`）保持现有实现不动。

- [ ] **Step 5: `BaseLayout.astro` html 行加 dir**

把 `<html lang={locale === 'zh' ? 'zh-CN' : 'en'}>` 改为：

```astro
<html lang={locale === 'zh' ? 'zh-CN' : locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
```

- [ ] **Step 6: 写 8 个 ar 桩页面**

模板（以 `src/pages/ar/about.astro` 为例）：

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
---
<BaseLayout title="نبذة عني — جودي ون" locale="ar">
  <h1 class="font-serif text-3xl font-bold">نبذة عني</h1>
</BaseLayout>
```

按下表创建全部 8 个文件（title / h1 逐字使用）：

| 文件 | title | h1 |
|---|---|---|
| `src/pages/ar/index.astro` | `جودي ون — باحثة في مركز CISS، جامعة تسينغهوا` | `جودي ون` |
| `src/pages/ar/about.astro` | `نبذة عني — جودي ون` | `نبذة عني` |
| `src/pages/ar/book.astro` | `الكتاب — جودي ون` | `الكتاب` |
| `src/pages/ar/publications.astro` | `المنشورات — جودي ون` | `المنشورات` |
| `src/pages/ar/media.astro` | `وسائل الإعلام — جودي ون` | `وسائل الإعلام` |
| `src/pages/ar/activities.astro` | `الأنشطة — جودي ون` | `الأنشطة` |
| `src/pages/ar/talk.astro` | `Wenjing Talk — جودي ون` | `Wenjing Talk` |
| `src/pages/ar/contact.astro` | `التواصل — جودي ون` | `التواصل` |

- [ ] **Step 7: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；以下断言全部退出码 0：

```bash
for loc in '' 'zh/' 'ar/'; do
  for f in about book publications media activities talk contact; do
    test -f "dist/${loc}$f/index.html" || { echo "MISSING dist/${loc}$f/index.html"; exit 1; }
  done
  test -f "dist/${loc}index.html" || { echo "MISSING dist/${loc}index.html"; exit 1; }
done
grep -q 'dir="rtl"' dist/ar/index.html && grep -q 'lang="ar"' dist/ar/index.html
grep -q 'dir="ltr"' dist/index.html && grep -q 'dir="ltr"' dist/zh/index.html
grep -q 'العربية' dist/index.html          # 每页都有三向切换器
grep -q 'العربية' dist/zh/index.html
grep -q 'EN' dist/ar/about/index.html      # ar 页可切回英文
grep -q 'href="/ar/about' dist/about/index.html
grep -q 'href="/zh/about' dist/ar/about/index.html
! grep -rq 'lang.switch' src/ || { echo "lang.switch still referenced"; exit 1; }
```

- [ ] **Step 8: Commit**

```bash
git add astro.config.mjs src/i18n/ src/components/Nav.astro src/components/BaseLayout.astro src/pages/ar/
git commit -m "feat: add Arabic locale infrastructure with three-way language switcher"
```

---

### Task 2: RTL 逻辑属性改造 + MediaCard 平台规则

**Files:**
- Modify: `src/components/TimelineItem.astro`
- Modify: `src/components/ActivityList.astro`
- Modify: `src/components/MediaCard.astro`
- Modify: 审计中发现的其他含方向物理类的文件（预期没有；有则同法处理）

**Interfaces:**
- Consumes: Task 1 的 dir="rtl"（阿语页）。
- Produces: 方向逻辑属性化的组件；LTR 页视觉零回归。

- [ ] **Step 1: `TimelineItem.astro` 逻辑属性化**

把 `<li>` 与圆点的 class 改为：

```astro
<li class="relative border-s-2 border-neutral-200 pb-8 ps-6 last:pb-0">
  <span class="absolute top-1 -start-[7px] h-3 w-3 rounded-full bg-accent"></span>
```

（其余不动。）

- [ ] **Step 2: `ActivityList.astro` 逻辑属性化**

把 `<li>` 的 class 改为：

```astro
    <li class="border-s-2 border-accent ps-4">
```

（其余不动。）

- [ ] **Step 3: `MediaCard.astro` 平台规则扩展**

把 `embedBlocked` 条件改为：

```ts
const embedBlocked =
  (locale === 'zh' && d.platform === 'youtube') ||
  (locale !== 'zh' && d.platform === 'bilibili');
```

- [ ] **Step 4: 全仓方向物理类审计**

Run:

```bash
grep -rnE 'border-l-|border-r-|[^-]pl-|[^-]pr-|[^-]ml-|[^-]mr-|text-left|text-right|[^-]left-|[^-]right-|space-x-' src/ --include='*.astro' --include='*.css' | grep -v 'node_modules'
```

Expected: 仅可能命中对称场景（如 `left-0 right-0` 同时出现、`max-w-*` 拼写误命中）。逐一人工核对：对称/非方向的保留，方向的换逻辑属性（`ps/pe/ms/me/start/end/border-s/border-e`）。把每一处处理结果写入报告。

- [ ] **Step 5: 验证（LTR 零回归）**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -q 'border-s-2' src/components/TimelineItem.astro` 退出码 0；中英关键页排版类名在 dist 中仍然存在（`grep -q 'border-s-2' dist/about/index.html` 退出码 0）。

- [ ] **Step 6: Commit**

```bash
git add src/
git commit -m "feat: convert directional utilities to logical properties for RTL"
```

---

### Task 3: ar 长文页（about / book / talk）

**Files:**
- Modify: `src/pages/ar/about.astro`
- Modify: `src/pages/ar/book.astro`
- Modify: `src/pages/ar/talk.astro`

**Interfaces:**
- Consumes: `BaseLayout`、`SectionHeader`（含 `as` prop）、`TimelineItem`、`TalkIntro`（`locale`、`links`、`qrImage` props）、ui ar 字典。
- Produces: 三页完整阿语译文页面。

- [ ] **Step 1: 写正式 `src/pages/ar/about.astro`（全文）**

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import TimelineItem from '../../components/TimelineItem.astro';

const locale = 'ar' as const;
---
<BaseLayout title="نبذة عني — جودي ون" locale={locale} description="جودي ون، باحثة في مركز الأمن الدولي والاستراتيجية (CISS) بجامعة تسينغهوا، ومديرة التواصل الدولي في منتدى الصين.">
  <SectionHeader as="h1" title="نبذة عني" />

  <div class="flex flex-col gap-6 sm:flex-row sm:items-start">
    <img src="/images/portrait.jpg" alt="صورة جودي ون" class="h-96 w-auto shrink-0 rounded-md" />
    <div class="measure space-y-4 text-neutral-700">
    <p>الدكتورة جودي ون (ون جينغ) باحثة في مركز الأمن الدولي والاستراتيجية (CISS) بجامعة تسينغهوا، وتشغل أيضًا منصب مديرة التواصل الدولي في منتدى الصين، وهو منصة تُعنى بتيسير التبادلات رفيعة المستوى حول القضايا المتعلقة بالصين داخل البلاد وخارجها.</p>
    <p>متخصصة في السياسة الخارجية الأمريكية وسياسات الشرق الأوسط والتواصل الدولي، تحمل الدكتورة ون درجة الدكتوراه في دراسات الشرق الأوسط من جامعة بكين، وأجرت بحوث ما بعد الدكتوراه في القانون بجامعة تسينغهوا، وكانت باحثة زائرة بجامعة أكسفورد في الفترة من 2021 إلى 2022. وفي يناير 2026، نشرت أحدث كتبها حول سياسة الولايات المتحدة في الشرق الأوسط.</p>
    <p>تشارك الدكتورة ون بنشاط في المنتديات الدولية وحوارات المسار الثاني التي تجمع الصين والولايات المتحدة ودول الشرق الأوسط. وتقدّم باستمرار التحليلات والتعليقات لكبريات وسائل الإعلام، من بينها ذا نيويورك تايمز وBBC وساوث تشاينا مورنينغ بوست وCGTN وتلفزيون فينيكس وChina-US Focus.</p>
    <p>قبل مسيرتها الأكاديمية، كانت للدكتورة ون مسيرة صحفية متميزة، إذ عملت صحفية أولى ومذيعة أخبار، وغطّت الأخبار من أكثر من 40 دولة في أوروبا وآسيا والشرق الأوسط — منها المملكة المتحدة وألمانيا وبلجيكا واليابان وكوريا الجنوبية وباكستان والعراق وإيران وتركيا ولبنان — في تغطيات إخبارية وبحوث ميدانية.</p>
    </div>
  </div>

  <div class="mt-14">
    <SectionHeader title="المسيرة والتعليم" />
    <ul>
      <TimelineItem period="حاليًا" title="باحثة" org="مركز الأمن الدولي والاستراتيجية (CISS)، جامعة تسينغهوا" description="ومديرة التواصل الدولي في منتدى الصين." />
      <TimelineItem period="2021–2022" title="باحثة زائرة" org="معهد أكسفورد للدراسات العالمية والإقليمية، جامعة أكسفورد" />
      <TimelineItem title="باحثة ما بعد الدكتوراه في القانون" org="جامعة تسينغهوا" />
      <TimelineItem title="دكتوراه في دراسات الشرق الأوسط" org="جامعة بكين" />
      <TimelineItem title="صحفية أولى ومذيعة أخبار" description="غطّت الأخبار وأجرت بحوثًا ميدانية في أكثر من 40 دولة في أوروبا وآسيا والشرق الأوسط." />
    </ul>
  </div>

  <div class="mt-14">
    <SectionHeader title="مجالات البحث" />
    <ul class="flex flex-wrap gap-3">
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">السياسة الخارجية الأمريكية</li>
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">سياسات الشرق الأوسط</li>
      <li class="rounded-md bg-neutral-100 px-3 py-2 text-sm text-neutral-700">التواصل الدولي</li>
    </ul>
  </div>
</BaseLayout>
```

- [ ] **Step 2: 写正式 `src/pages/ar/book.astro`（全文）**

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';

const locale = 'ar' as const;
---
<BaseLayout title="الكتاب — جودي ون" locale={locale} description="كتاب «دراسات سياسة الولايات المتحدة في الشرق الأوسط (2009-2017)» للدكتورة جودي ون.">
  <SectionHeader as="h1" title="الكتاب" />
  <div class="flex flex-col gap-8 sm:flex-row sm:items-center">
    <input type="checkbox" id="cover-zoom" class="peer sr-only" />
    <label for="cover-zoom" class="w-fit shrink-0 cursor-zoom-in rounded-md peer-focus-visible:ring-2 peer-focus-visible:ring-accent">
      <img src="/images/book-cover.jpg" alt="غلاف كتاب «دراسات سياسة الولايات المتحدة في الشرق الأوسط (2009-2017)»" class="h-96 w-auto rounded-md" />
    </label>
    <div>
      <h3 class="font-serif text-2xl font-semibold">دراسات سياسة الولايات المتحدة في الشرق الأوسط (2009-2017)</h3>
      <p class="mt-1 text-neutral-500">《美国的中东政策研究（2009-2017）》 · كتاب أكاديمي صادر باللغة الصينية · يناير 2026</p>
      <div class="measure mt-4 space-y-4 text-neutral-700">
        <p>بالاستناد إلى سنوات من البحث والعمل الميداني في الشرق الأوسط، يقدّم هذا الكتاب دراسة منهجية لسياسة الولايات المتحدة تجاه المنطقة في الفترة من 2009 إلى 2017، متتبعًا تطورها ومحركاتها وأثرها في النظام الإقليمي.</p>
        <p>الدكتورة ون باحثة في مركز الأمن الدولي والاستراتيجية (CISS) بجامعة تسينغهوا، ومتخصصة في السياسة الخارجية الأمريكية وسياسات الشرق الأوسط.</p>
      </div>
      <div class="mt-6">
        <h4 class="text-sm font-semibold uppercase tracking-wide text-neutral-500">بيانات النشر</h4>
        <p class="mt-1 text-sm text-neutral-600">دار نشر المعرفة العالمية (World Affairs Press 世界知识出版社) · يناير 2026 · ISBN 9787501269600 · <a href="https://product.dangdang.com/30001244.html" target="_blank" rel="noopener" class="text-accent hover:underline">الشراء عبر Dangdang</a></p>
      </div>
    </div>
    <label for="cover-zoom" class="fixed inset-0 z-50 hidden cursor-zoom-out items-center justify-center bg-neutral-900/70 p-6 peer-checked:flex">
      <img src="/images/book-cover.jpg" alt="غلاف كتاب «دراسات سياسة الولايات المتحدة في الشرق الأوسط (2009-2017)» (مكبّر)" class="max-h-[90vh] max-w-full rounded-md object-contain" />
    </label>
  </div>
</BaseLayout>
```

- [ ] **Step 3: 写正式 `src/pages/ar/talk.astro`（全文）**

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import TalkIntro from '../../components/TalkIntro.astro';
import { ui } from '../../i18n/ui';

const locale = 'ar' as const;
const t = ui[locale];
const links: { label: string; url: string }[] = [
  // 文晶Talk 平台链接待用户补充（见 docs/pending-assets.md）
];
---
<BaseLayout title="Wenjing Talk — جودي ون" locale={locale} description="Wenjing Talk (文晶Talk)، العلامة الإعلامية المستقلة التي أسستها جودي ون.">
  <SectionHeader as="h1" title={t['talk.title']} />
  <TalkIntro locale={locale} links={links} qrImage="/images/wenjing-talk-qr.jpg">
    <p class="text-neutral-700">Wenjing Talk (文晶Talk) هي العلامة الإعلامية المستقلة التي أسستها الدكتورة جودي ون خلال سنوات عملها صحفية أولى، وتقدّم تقاريرها وتعليقاتها في الشؤون الدولية مع تركيز على الشرق الأوسط، مستندة إلى عمل ميداني في أكثر من 40 دولة في أوروبا وآسيا والشرق الأوسط.</p>
  </TalkIntro>
</BaseLayout>
```

（说明：`TalkIntro` 的二维码说明文字是组件内 locale 三元，目前只有 zh/en 两句——本任务 Step 4 补 ar 分支。）

- [ ] **Step 4: `TalkIntro.astro` 二维码说明补 ar 分支**

把 figcaption 行改为：

```astro
      <figcaption class="mt-2 text-sm text-neutral-600">{locale === 'zh' ? '微信扫码关注「文晶Talk」' : locale === 'ar' ? 'امسح الرمز بتطبيق WeChat لمتابعة Wenjing Talk' : 'Scan with WeChat to follow Wenjing Talk'}</figcaption>
```

img 的 alt 同样加 ar 分支：

```astro
      <img src={qrImage} alt={locale === 'zh' ? '文晶Talk 微信公众号二维码' : locale === 'ar' ? 'رمز الاستجابة السريعة لحساب Wenjing Talk على WeChat' : 'Wenjing Talk WeChat official account QR code'} class="h-44 w-44 rounded-md border border-neutral-200" />
```

- [ ] **Step 5: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；`grep -q 'الدكتورة جودي ون' dist/ar/about/index.html`、`grep -q 'دار نشر المعرفة العالمية' dist/ar/book/index.html`、`grep -q 'العلامة الإعلامية المستقلة' dist/ar/talk/index.html`、`grep -q 'dir="rtl"' dist/ar/about/index.html` 全部退出码 0。

- [ ] **Step 6: Commit**

```bash
git add src/
git commit -m "feat: add Arabic about, book and talk pages"
```

---

### Task 4: ar 数据页（home / publications / media / activities / contact）+ Hero 三向

**Files:**
- Modify: `src/components/Hero.astro`
- Modify: `src/pages/ar/index.astro`
- Modify: `src/pages/ar/publications.astro`
- Modify: `src/pages/ar/media.astro`
- Modify: `src/pages/ar/activities.astro`
- Modify: `src/pages/ar/contact.astro`

**Interfaces:**
- Consumes: Task 1 的 ar 字典与工具函数；`PublicationList`/`MediaCard`/`ActivityList`/`ContactBlock`/`Hero`/`SectionHeader` 组件；三个内容集合。
- Produces: 5 个阿语正式页面；Hero credentials 支持 ar。

- [ ] **Step 1: `Hero.astro` credentials 改三向**

把 credentials 定义改为：

```ts
const credentials =
  locale === 'zh'
    ? ['北京大学中东研究博士', '牛津大学访问学者', '清华大学法学博士后', '资深媒体人']
    : locale === 'ar'
      ? ['دكتوراه في دراسات الشرق الأوسط (جامعة بكين)', 'باحثة زائرة بجامعة أكسفورد', 'باحثة ما بعد الدكتوراه في القانون (تسينغهوا)', 'إعلامية مخضرمة']
      : ['Ph.D. in Middle East Studies, PKU', 'Oxford Visiting Scholar', 'Postdoc in Law, Tsinghua', 'Former Senior Journalist'];
```

- [ ] **Step 2: 写正式 `src/pages/ar/index.astro`（全文）**

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../components/BaseLayout.astro';
import Hero from '../../components/Hero.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import PublicationList from '../../components/PublicationList.astro';
import { ui } from '../../i18n/ui';
import { localizePath } from '../../i18n/utils';

const locale = 'ar' as const;
const t = ui[locale];
const latest = (await getCollection('publications'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime())
  .slice(0, 3);
const outlets = ['The New York Times', 'BBC', 'South China Morning Post', 'CGTN', 'Phoenix TV', 'China-US Focus'];
---
<BaseLayout title="جودي ون — باحثة في مركز CISS، جامعة تسينغهوا" locale={locale} description={t['hero.tagline']}>
  <Hero locale={locale} />

  <section class="mt-14">
    <SectionHeader title={t['home.book.title']} />
    <div class="flex flex-col gap-6 sm:flex-row sm:items-center">
      <input type="checkbox" id="cover-zoom" class="peer sr-only" />
      <label for="cover-zoom" class="w-fit shrink-0 cursor-zoom-in rounded-md peer-focus-visible:ring-2 peer-focus-visible:ring-accent">
        <img src="/images/book-cover.jpg" alt="غلاف كتاب «دراسات سياسة الولايات المتحدة في الشرق الأوسط (2009-2017)»" class="h-72 w-auto rounded-md" />
      </label>
      <div>
        <h3 class="font-serif text-xl font-semibold">دراسات سياسة الولايات المتحدة في الشرق الأوسط (2009-2017)</h3>
        <p class="mt-1 text-sm text-neutral-500">《美国的中东政策研究（2009-2017）》 · يناير 2026</p>
        <p class="measure mt-3 text-neutral-700">دراسة منهجية لسياسة الولايات المتحدة تجاه الشرق الأوسط في الفترة من 2009 إلى 2017، بالاستناد إلى بحوث المؤلفة وخبرتها الميدانية في المنطقة.</p>
        <a href={localizePath('/book', locale)} class="mt-3 inline-block text-sm font-medium text-accent hover:underline">{t['home.viewAll']}</a>
      </div>
      <label for="cover-zoom" class="fixed inset-0 z-50 hidden cursor-zoom-out items-center justify-center bg-neutral-900/70 p-6 peer-checked:flex">
        <img src="/images/book-cover.jpg" alt="غلاف كتاب «دراسات سياسة الولايات المتحدة في الشرق الأوسط (2009-2017)» (مكبّر)" class="max-h-[90vh] max-w-full rounded-md object-contain" />
      </label>
    </div>
  </section>

  <section class="mt-14">
    <SectionHeader title={t['home.publications.title']} />
    <PublicationList entries={latest} locale={locale} />
    <a href={localizePath('/publications', locale)} class="text-sm font-medium text-accent hover:underline">{t['home.viewAll']}</a>
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

（说明：阿语首页书封采用与中英首页一致的 checkbox 点击放大结构（纯 CSS，无锚点）；中英页面保持现状不动。）

- [ ] **Step 3: 写正式 `src/pages/ar/publications.astro`（全文）**

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import PublicationList from '../../components/PublicationList.astro';
import { ui } from '../../i18n/ui';

const locale = 'ar' as const;
const t = ui[locale];
const entries = (await getCollection('publications'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
---
<BaseLayout title="المنشورات — جودي ون" locale={locale} description={t['publications.subtitle']}>
  <SectionHeader as="h1" title={t['publications.title']} subtitle={t['publications.subtitle']} />
  <PublicationList entries={entries} locale={locale} />
</BaseLayout>
```

- [ ] **Step 4: 写正式 `src/pages/ar/media.astro`（全文）**

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import MediaCard from '../../components/MediaCard.astro';
import { ui } from '../../i18n/ui';

const locale = 'ar' as const;
const t = ui[locale];
const all = (await getCollection('media'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
const features = all.filter((e) => e.data.type === 'video' || e.data.type === 'interview');
const mentions = all.filter((e) => e.data.type === 'mention');
const outlets = ['The New York Times', 'BBC', 'South China Morning Post', 'CGTN', 'Phoenix TV', 'China-US Focus'];
---
<BaseLayout title="وسائل الإعلام — جودي ون" locale={locale} description="مقابلات وفيديوهات وإشارات إعلامية للدكتورة جودي ون.">
  <SectionHeader as="h1" title={t['media.title']} />

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

- [ ] **Step 5: 写正式 `src/pages/ar/activities.astro`（全文）**

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import ActivityList from '../../components/ActivityList.astro';
import { ui } from '../../i18n/ui';

const locale = 'ar' as const;
const t = ui[locale];
const entries = (await getCollection('activities'))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
---
<BaseLayout title="الأنشطة — جودي ون" locale={locale} description={t['activities.subtitle']}>
  <SectionHeader as="h1" title={t['activities.title']} subtitle={t['activities.subtitle']} />
  <ActivityList entries={entries} locale={locale} />
</BaseLayout>
```

（说明：`ActivityList` 当前按 `locale === 'zh'` 取 eventZh/locationZh，其余取英文字段——ar 自动走英文字段，无需改组件。）

- [ ] **Step 6: 写正式 `src/pages/ar/contact.astro`（全文）**

```astro
---
import BaseLayout from '../../components/BaseLayout.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import ContactBlock from '../../components/ContactBlock.astro';
import { ui } from '../../i18n/ui';

const locale = 'ar' as const;
const t = ui[locale];
---
<BaseLayout title="التواصل — جودي ون" locale={locale} description="معلومات التواصل مع الدكتورة جودي ون.">
  <SectionHeader as="h1" title={t['contact.title']} />
  <ContactBlock locale={locale} />
</BaseLayout>
```

- [ ] **Step 7: 验证**

Run: `npm run build && npx astro check`
Expected: `0 errors`；以下全部退出码 0：

```bash
grep -q 'أحدث المنشورات' dist/ar/index.html
grep -q 'دكتوراه في دراسات الشرق الأوسط' dist/ar/index.html   # Hero 阿语资历标签
grep -q 'المنشورات' dist/ar/publications/index.html
grep -q 'عرض الكل' dist/ar/index.html
grep -q 'البريد الإلكتروني' dist/ar/contact/index.html
grep -q 'target="_blank"' dist/ar/publications/index.html
! grep -q 'player.bilibili.com' dist/ar/media/index.html      # ar 页无 bilibili iframe（当前数据集无 embedUrl，自然通过）
```

- [ ] **Step 8: Commit**

```bash
git add src/
git commit -m "feat: add Arabic home, publications, media, activities and contact pages"
```

---

### Task 5: 终验 + 文档更新

**Files:**
- Modify: `AGENTS.md`（§3/§4 技术栈与 i18n 描述）
- Modify: `PROGRESS.md`（当前状态）

**Interfaces:**
- Consumes: Task 1–4 全部产物。
- Produces: 三语可交付站点与同步后的文档。

- [ ] **Step 1: 全量构建与类型检查**

Run: `npm run build && npx astro check`
Expected: 成功，`0 errors`。

- [ ] **Step 2: 24 路由全部可达**

```bash
for loc in '' 'zh/' 'ar/'; do
  for f in about book publications media activities talk contact; do
    test -f "dist/${loc}$f/index.html" || { echo "MISSING dist/${loc}$f/index.html"; exit 1; }
  done
  test -f "dist/${loc}index.html" || { echo "MISSING dist/${loc}index.html"; exit 1; }
done
echo "ALL 24 ROUTES OK"
```

Expected: 输出 `ALL 24 ROUTES OK`。

- [ ] **Step 3: 三向语言切换断言（24 页逐一）**

```bash
for f in about book publications media activities talk contact; do
  grep -q "href=\"/zh/$f" "dist/$f/index.html" || { echo "EN->ZH missing: $f"; exit 1; }
  grep -q "href=\"/ar/$f" "dist/$f/index.html" || { echo "EN->AR missing: $f"; exit 1; }
  grep -q "href=\"/$f" "dist/zh/$f/index.html" || { echo "ZH->EN missing: $f"; exit 1; }
  grep -q "href=\"/ar/$f" "dist/zh/$f/index.html" || { echo "ZH->AR missing: $f"; exit 1; }
  grep -q "href=\"/$f" "dist/ar/$f/index.html" || { echo "AR->EN missing: $f"; exit 1; }
  grep -q "href=\"/zh/$f" "dist/ar/$f/index.html" || { echo "AR->ZH missing: $f"; exit 1; }
done
grep -q 'href="/zh/"' dist/index.html && grep -q 'href="/ar/"' dist/index.html
grep -q 'href="/"' dist/zh/index.html && grep -q 'href="/ar/"' dist/zh/index.html
grep -q 'href="/"' dist/ar/index.html && grep -q 'href="/zh/"' dist/ar/index.html
echo "LANG SWITCH 3-WAY OK"
```

Expected: 输出 `LANG SWITCH 3-WAY OK`。

- [ ] **Step 4: dir / lang 断言**

```bash
for f in index about book publications media activities talk contact; do
  grep -q 'lang="ar"' "dist/ar/$f/index.html" || { echo "ar lang missing: $f"; exit 1; }
  grep -q 'dir="rtl"' "dist/ar/$f/index.html" || { echo "rtl missing: $f"; exit 1; }
done
for f in index about book publications media activities talk contact; do
  grep -q 'dir="ltr"' "dist/$f/index.html" || { echo "en ltr missing: $f"; exit 1; }
  grep -q 'dir="ltr"' "dist/zh/$f/index.html" || { echo "zh ltr missing: $f"; exit 1; }
done
echo "DIR/LANG OK"
```

Expected: 输出 `DIR/LANG OK`。

- [ ] **Step 5: LTR 无回归 + RTL 人工核查**

Run: `npm run dev`，用 Playwright 截图并人工核查：
1. `/about` 与 `/zh/about`（LTR 排版与逻辑属性改造前一致：时间线边框在左、圆点贴线）
2. `/ar/`（导航镜像、Hero 图右文左、文字右对齐、资历标签正常换行）
3. `/ar/about`（时间线边框在右、圆点贴右线、bio 右对齐）
4. 移动端 375px：`/ar/` 汉堡菜单展开，三个语言链接可用

把截图结论写入报告；发现排版缺陷先修复再继续。

- [ ] **Step 6: 更新文档**

`AGENTS.md`：§3 技术栈 i18n 行改为 `locales: ['en', 'zh', 'ar']`；§4.1 双语路由一节改为三语（阿语 `/ar/` 前缀、RTL 逻辑属性、三向语言切换、UI 字典三语）；§4.2 页面表改为 8 页 × 3 语言；提及阿语翻译待用户校对。
`PROGRESS.md`：当前状态补一行——2026-07-21 新增阿拉伯语第三语言（`/ar/`，RTL），24 路由；阿语文案为 AI 翻译，待用户校对。

- [ ] **Step 7: Commit**

```bash
git add AGENTS.md PROGRESS.md src/
git commit -m "docs: document Arabic locale in AGENTS.md and PROGRESS.md"
```

---

## Self-Review 记录

- **Spec coverage：** 规格 §3.1 路由/配置 → Task 1；§3.2 字典/工具 → Task 1；§3.3 RTL → Task 1(dir)/Task 2(逻辑属性)；§3.4 三向切换 → Task 1；§3.5 阿语文案 → Task 1(字典)/Task 3(长文)/Task 4(数据页)；§3.6 组件接口 → Task 1/2/4；§4 错误处理 → Task 1 Step 2 注 + 各验证步；§5 验证 → Task 5；§6 非目标 → Global Constraints。
- **Placeholder scan：** 无 TBD/TODO；全部代码步骤含完整代码与完整阿语译文；审计类步骤（Task 2 Step 4）给出确切命令与处理规则。
- **Type consistency：** `stripLocalePrefix`/`localizePath`/`getLocaleFromPath` 签名在 Task 1 定义处与 Nav/页面使用处一致；`Locale` 三值在组件三元/Record 处一致覆盖；`UIKey` 保持已删除状态（此前终审修复波已作为死导出删除，本计划不再引入）。
- **已决偏差的显式说明：** 阿语首页书封放大与中英首页同款 checkbox 结构（计划初稿曾简化处理，自审修正）；`lang.switch` 删除（规格 §3.4 三向切换器取代，Task 1 Step 2 注明）。
