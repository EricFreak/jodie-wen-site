# 首页「近期活动」轮播版块 —— 设计规格

日期：2026-09-21
状态：已获用户批准（2026-09-21）

## 1. 背景与目标

用户希望首页与活动相关的内容更丰富。在首页新增一个「近期活动」横向滑动卡片区，展示有封面图的线下论坛/活动，引导访客进入活动报道外链或 Activities 页。

**非目标**（本次明确不做）：

- 不做活动图文详情页（用户 2026-09-21 明确放弃「图文稿详情页」方向）
- 不改动 `/activities` 页面本身及其列表样式
- 不引入任何客户端 JS（轮播用纯 CSS scroll-snap）
- 不做自动播放、不做切换按钮组（横向滑动卡片即可）

## 2. 决策记录（来自与用户的确认）

| 问题 | 结论 |
| --- | --- |
| 与 /activities 页的关系 | Activities 页保持不变；仅在首页新增轮播版块 |
| 内容来源 | 封面图由实现方从活动已有公开报道链接抓取；用户日后提供素材可直接替换同名文件 |
| 轮播形式 | 横向滑动卡片（CSS scroll-snap，零 JS） |
| 展示哪些活动 | 只展示「有封面图」的活动，按日期倒序 |
| 卡片点击跳转 | 有 `url` 的活动跳到外链（新窗口）；无 `url` 的活动（如 2026-09 希利论坛，用户提供的新闻稿无公开链接）纯展示不可点击 |

## 3. 数据模型

`src/content.config.ts` 的 `activities` 集合 schema 新增一个**可选**字段：

- `cover: z.string().optional()` —— 本地封面图路径，形如 `/images/activities/<slug>.jpg`

封面图落地规则（2026-09-21 更新：用户要求首页轮播只保留希利论坛内容，此前抓取的 7 张封面及对应 frontmatter `cover` 已全部移除，仅保留用户提供的素材）：

- 实现方从各活动 frontmatter 已有的 `url`（CISS 官网等公开报道页）抓取合适图片，下载到 `public/images/activities/`，文件名与活动条目 slug 一致
- 图片压缩到合理体积（宽度约 1200px 以内、JPEG 质量约 80）
- 找不到合适封面图的活动不加 `cover` 字段，该活动不出现在首页轮播，仅在 Activities 页保持现状
- 用户后续提供素材时直接替换同名文件即可，无需改代码

## 4. 首页版块

新组件 `src/components/ActivityCarousel.astro`，在三语首页（`src/pages/index.astro`、`zh/index.astro`、`ar/index.astro`）中引用。

**位置**：首页「In the Media / 媒体报道」视频版块之下、「More about Jodie」照片墙之上。

**结构**（2026-09-21 按用户要求修订为左右箭头轮播样式）：

- 版块标题 + 副标题（`src/i18n/ui.ts` 新增三语词条，如 `home.activities.title` / `home.activities.subtitle`；阿语为 AI 翻译待校对）
- "View all →" 链接到当前语言的 `activities` 页（无条件显示，与轮播数量无关）
- 左右箭头轮播（纯 CSS：radio + label 切换幻灯片，零 JS；不用锚点跳转，点击箭头页面位置保持不变）：一次展示一张幻灯片，左右两侧圆形箭头按钮切换上一张/下一张（仅 1 张或首张/末张时不显示对应箭头）
- 最多展示最新 5 场有封面图的活动（有几个展示几个）；图片下方居中显示圆点指示器（每点对应一张幻灯片、可点击切换、当前页深青高亮，仅 1 张时不显示）
- 每张幻灯片内容（上方图片、下方文字）：
  - 封面图，16:9 `object-cover` 裁切
  - 标题：`locale === 'zh' ? titleZh : titleEn`（与 `ActivityList.astro:19` 现有阿语回退逻辑一致，阿语页显示英文标题）
  - 日期 + 地点小字（地点同样按 locale 取 `location`/`locationZh`）
- 有 `url` 的活动：封面图与标题均可点击，`target="_blank" rel="noopener"` 跳外链；**无 `url` 的活动以纯展示渲染（不可点击）**，仍可进入轮播
- 方向相关样式一律用 Tailwind 逻辑属性（箭头用 `start-/end-` + `rtl:-scale-x-100`），阿语 RTL 下滚动与排版自然适配

**空态**：过滤后没有任何带 `cover` 的活动时，整个版块（含标题与 View all）不渲染。

**视觉**：沿用站点现有语言 —— 黑白灰 + 深青 `#0F766E` 点缀、衬线标题、卡片样式与首页 `VideoCard` 保持一致（圆角、边框/阴影、hover 态）。

## 5. 数据流

1. 首页 Astro 模板 `getCollection('activities')`
2. 过滤 `entry.data.cover` 非空 → 按 `date` 倒序
3. 取前 5 条传给 `ActivityCarousel` 渲染；组件内不做数据获取，只接收 props；View all 链接无条件渲染

## 6. 错误处理与边界

- `cover` 文件缺失：构建不报错（public 静态引用），实现时逐张核对文件存在
- 活动无 `url`：仍可进入轮播（schema 中 `url` 为可选），幻灯片以纯展示渲染、不可点击
- 图片抓取失败的活动：跳过，不加 `cover`，记入交付说明

## 7. 验证

1. `npm run build` 成功，`npx astro check` 无类型错误
2. 三语首页（`/`、`/zh/`、`/ar/`）人工走查：版块出现、View all 指向对应语言 activities 页、卡片点击新开外链
3. 移动端 375px：横向滑动顺畅、卡片宽度与露出比例正确；桌面 1280px：一行约 3 张
4. 阿语首页 RTL 下布局与滑动方向正确
5. 临时构造一个无 `cover` 的活动条目验证其不出现在首页（验证后还原）
