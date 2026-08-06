# 媒体版块改版 + Social Media 页 + materials 素材入库 — 设计规格

日期：2026-08-05　状态：已获用户批准（原型确认后）

## 背景

- 首页 Media 版块原为一排媒体名标签，访客需两级跳转才能看到内容；Media 页全是文字链接卡片。
- 用户要求：首页直接展示富媒体视频卡片；新增「More about Jodie」生活照片版块；Wenjing Talk 改为 Social Media 页（社媒 logo + 链接 + 相关内容）；页脚加社媒图标。
- 素材入口：`materials/` 目录（用户持续投放），解析后视频/文字分两个子目录存放，入库时与现有内容去重。

## 决策（已与用户确认）

1. 首页视频卡片逻辑：**latest**（按日期倒序取前 3 条 `type: video`），media schema 新增可选 `featured: boolean`，标记的优先展示，不足 3 条按日期补齐。
2. 视频呈现：**封面卡片挂外链**（新标签页打开官方播放页）；不下载、不转载视频（版权/带宽/零 JS 红线）。media 页保留 `embedUrl` 内嵌机制。media schema 新增可选 `cover`（本地封面路径），无封面时用平台品牌色渐变占位 + 播放按钮。
3. 社媒卡片：无链接的平台**先隐藏**；数据集中在 `src/data/socials.ts`，拿到链接填入 `url` 即显示。
4. 页脚社媒图标：点击跳到本站 Social Media 页（各语言对应路由）。
5. 去重：URL 相同直接跳过；同一文章多渠道发布（澎湃/FT中文网 vs CISS 转载）保留一条，优先已收录条目。

## 改动清单

- `src/content.config.ts`：media 加 `featured`/`cover`；新增 `gallery` 集合（image/captionEn/captionZh/captionAr/date?）
- 新组件：`VideoCard.astro`（封面卡片）、`SocialIcon.astro`（内联 SVG 图标）、`Gallery.astro`（照片墙）
- `src/data/socials.ts`：社媒平台数据（icon/name/handle/url?/descEn/descZh/descAr）
- 首页 ×3：Media 版块改视频卡片 + 保留媒体墙小标签；底部新增 More about Jodie（gallery 空时显示空态文案）
- Media 页 ×3：视频卡片网格（videos）/ 文字采访列表（interviews）/ 媒体引用（mentions）三段
- 路由：`/talk` → `/social`（×3 语言），删除 `talk.astro` 与 `TalkIntro.astro`；Nav 更新
- `Footer.astro`：加社媒图标行
- `src/i18n/ui.ts`：`nav.talk`→`nav.social`，新增 social.*/home.moreAbout/media.interviews 等键
- `materials/视频/`、`materials/文字/`：docx 解析出的单条 Markdown（frontmatter 与集合字段对齐）
- 入库：新增约 23 条 collection 条目（SCMP 12、Berlingske 2、中评社 2、IPD 1、CGTN 视频 5、中美聚焦文章 1）
- 文档：AGENTS.md、PROGRESS.md、docs/pending-assets.md 同步

## 已知数据处理

- CGTN Global Watch 3/1：现有条目回放 ID `CcdIEAA` vs docx `CcdbJIA`，实施时验证后留有效者
- docx 笔误：`cn.ft.com.`（FT 条目因重复本就跳过）、SCMP 4/9 URL 含空格（修正常见连字符断行）
- 无照片前 More about Jodie 显示空态；照片投入 `public/images/gallery/` 后建 gallery 条目

## 验证

`npm run build` + `npx astro check` + 浏览器抽查首页/Media/Social 三页 ×（桌面 1280 / 移动 375）。
