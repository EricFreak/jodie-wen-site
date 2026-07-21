# 阿拉伯语第三语言版 — 设计规格

- 日期：2026-07-21
- 状态：设计已获用户批准
- 项目：`/Users/eric/kimi-projects/jodie-wen-site`（Astro 5 + Tailwind v4 静态站，现有中英双语）
- 前置规格：`2026-07-20-jodie-wen-personal-site-design.md`（本规格为其增量，冲突处以本规格为准）

## 1. 目标

为网站增加阿拉伯语第三语言（她是中东学者，阿语受众是合理扩展），路由前缀 `/ar/`，8 页全量对应，RTL（从右向左）布局。阿语访客能与中英访客获得同等的信息架构体验。

## 2. 已确认的决策（需求澄清）

| 决策点 | 结论 |
|---|---|
| 范围 | 全站 8 页阿语版（首页/关于/著作/发表/媒体/活动/文晶Talk/联系） |
| 翻译 | 由实现方（AI）翻译全部 UI 字符串与页面长文，用户上线前校对 |
| 内容条目标题 | 23 条（8 文章 + 8 媒体 + 7 活动）在阿语页保持英文标题，不新增阿语字段 |
| RTL 实现 | Tailwind 逻辑属性改造（一套 class 双向适配），不用 rtl: 变体、不用全局 CSS 覆盖 |

## 3. 架构

### 3.1 路由与配置

- `astro.config.mjs`：`locales: ['en', 'zh', 'ar']`，`defaultLocale` 仍为 `'en'`，`prefixDefaultLocale: false` → 阿语路径 `/ar/about` 形式
- 新增 `src/pages/ar/` 目录，8 个页面文件与 `src/pages/zh/` 一一对应（index/about/book/publications/media/activities/talk/contact）

### 3.2 i18n 工具与字典

- `src/i18n/ui.ts`：`locales` 增加 `'ar'`；`ui` 增加 `ar` 字典，key 集合与 en/zh 完全一致（约 40 个）；`Locale` 类型随之变为 `'en' | 'zh' | 'ar'`
- `src/i18n/utils.ts`：
  - `getLocaleFromPath`：识别 `/ar` 与 `/ar/` 前缀
  - `localizePath(path, locale)`：ar 加 `/ar` 前缀
  - 新增 `stripLocalePrefix(pathname): string`：从当前路径剥离语言前缀得到中性路径（如 `/ar/about/` → `/about`、`/zh/` → `/`）
  - 废弃 `getAlternatePath`（双语互切时代产物），由「中性路径 + localizePath 到目标语言」取代；Nav 是唯一调用方，同步改造

### 3.3 RTL 布局

- `BaseLayout.astro`：输出 `<html lang={...} dir={...}>`——阿语 `lang="ar" dir="rtl"`，英中 `dir="ltr"`
- 逻辑属性改造（Tailwind v4 原生支持）：方向相关物理类全部换为逻辑类
  - `TimelineItem.astro`：`border-l-2 → border-s-2`、`pl-6 → ps-6`、圆点 `-left-[7px] → -start-[7px]`
  - `ActivityList.astro`：`border-l-2 → border-s-2`、`pl-4 → ps-4`
  - 全仓审计其余方向类（`ml-/mr-/pl-/pr-/text-left/text-right/left-/right-/border-l/border-r/space-x-*`），逐处换逻辑等价物；flex/grid 布局随 `dir` 自动镜像，不改
- 字体：不引网络字体（规格红线不变）。阿语字形自动回退到系统阿语字体（macOS Geeza Pro、Windows Sakkal Majalla 等）；标题衬线栈对阿语字符同样回退系统默认，可接受
- 日期显示保持 ISO（YYYY-MM-DD），三语通用，不改

### 3.4 语言切换器（2 → 3）

- `Nav.astro` 语言区改为三个链接：EN / 中文 / العربية
- 当前语言以普通文本呈现（不可点击、无下划线），其余两个为链接，指向当前页面的对应语言路径：`localizePath(stripLocalePrefix(currentPath), targetLocale)`
- 移动端折叠菜单内同样呈现三个选项

### 3.5 阿语文案

由实现方翻译（用户上线前校对）：

- `ar` 字典全部 UI 字符串（导航、Hero、版块标题、空态、联系标签等）
- About 页：bio 四段、时间线条目、研究领域标签
- Book 页：简介与出版信息文案
- Talk 页：品牌介绍
- 各页 `title` / `description` meta

保持不动：23 条内容条目（英文标题 + 英文字段）；`eventZh/locationZh` 仅 zh 页使用；书籍中文书名《美国的中东政策研究（2009-2017）》在阿语页保留中文原名 + 阿语说明（书籍无阿语译名）。

### 3.6 组件接口变化

- `Nav.astro`：无 props 变化（内部改为三链接渲染）
- `BaseLayout.astro`：props 不变（内部按 locale 决定 `dir`）
- 其余组件：接口不变；`MediaCard` 的平台嵌入规则不变（阿语页同英文页规则：bilibili 降级为链接卡片）

## 4. 错误处理与边界

- 空态文案、外链属性（`target="_blank" rel="noopener"`）、schema 校验行为三语一致
- 阿语页若某 key 缺失，TypeScript 编译期即报错（字典为 `as const` 且 key 集合强制一致——实现时以 en 为准逐 key 对齐）
- RTL 不影响功能，仅影响排版；中英页 `dir="ltr"` 显式声明，行为不变

## 5. 验证

1. `npm run build` 成功、`npx astro check` 0 错误
2. 24 个路由（8 页 × 3 语）全部产出
3. 断言：每个阿语页 `lang="ar"`、`dir="rtl"`；中英页 `dir="ltr"`
4. 每页语言切换：三个链接分别指向本页的另外两种语言路径（24 页逐一断言）
5. 逻辑属性改造后中英页排版无回归（截图对比关键页面：首页、About）
6. Playwright 截图人工核查 `/ar/` 与 `/ar/about`：导航镜像、时间线边框在右侧、文字右对齐

## 6. 非目标（YAGNI）

- 不翻译 23 条内容条目的标题/字段（保持英文，§2 已决）
- 不引入阿拉伯语网络字体、不做字体子集化
- 不做阿语数字（١٢٣）本地化、不做阿语日期格式
- 不做 hreflang/SEO 扩展（沿用现有最小 meta；后续可单独评估）
- 不做语言自动探测/重定向（用户手动切换）
