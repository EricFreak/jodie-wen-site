# AGENTS.md — Jodie Wen 个人宣传网站

> 本文件面向 AI 编码代理，假设读者对本项目一无所知。
> 项目中文化档为主，沟通与文档默认使用中文。

## 1. 项目概览

为文晶（Jodie Wen，清华大学战略与安全研究中心 CISS Fellow、中国论坛国际传播主任）建设的**个人宣传网站**，集中展示其学术履历、专著、发表文章、媒体采访、「文晶Talk」自媒体品牌与国际论坛活动。

- 受众：国际学术界与政策圈、中外媒体、会议邀请方。
- 成功标准：访客 1 分钟内了解其身份与专长，能找到文章/视频/联系方式；**中英阿三语完整对应**（阿语文案为 AI 翻译，待用户校对）。
- 内容版块参考 bilal-y-saab.com 的信息架构（视觉不参考）。

## 2. 当前状态（重要）

**实现已完成，构建通过。** 目录结构已按 §4 落地：8 个基础页面 × 中英阿三语（24 路由）+ 50 篇文字内容详情页 × 3 语（150 路由）= **177 路由**；`src/content` 共 5 个集合（publications 15、media 31、activities 11、gallery 0、articleBodies 150）。2026-07-21 新增阿拉伯语（`/ar/`，RTL）；2026-10-30 完成全站「第三方文字内容站内化」：50 篇文字链接全部加 `detail: true`，列表自动改内链；其中 30 篇放全文；20 篇为站内摘要（18 篇付费墙/反爬来源：SCMP 14、Berlingske 2、FT 中文 1、联合早报 1；另有 CGTN Radio 与 CISS 纯 PDF 页 2 篇无可抓全文），摘要页统一保留原文链接；文末统一保留来源署名与原文链接。

- `docs/superpowers/specs/2026-07-20-jodie-wen-personal-site-design.md` —— 已获用户批准的完整设计规格（目标、技术栈、架构、视觉、验证方案）；规格与本文如有出入，以规格文档为准。
- `docs/superpowers/specs/2026-08-05-media-social-redesign-design.md` —— 2026-08-06 已实施的增量改版：首页视频卡片（latest + `featured` 优先）、「More about Jodie」照片墙（`gallery` 集合）、`/talk` → `/social` 社媒页、页脚社媒图标、Media 页三段式。
- `docs/superpowers/specs/2026-09-21-home-activity-carousel-design.md` —— 2026-09-21 已实施的增量改版：首页「近期活动」轮播版块（`activities` 集合新增可选 `cover`，封面图抓自 CISS 报道页存于 `public/images/activities/`，用户可替换同名文件）。
- `docs/superpowers/specs/2026-09-28-spacious-redesign-design.md` —— 2026-09-28 已实施的全站「大气化」改版：容器放宽至 `max-w-6xl`（`main` 全宽、各页面自带 `mx-auto max-w-6xl px-6` 容器，散文仍限 `.measure` 72ch）、Hero 通栏左文右图、首页 Activities 全宽色带、页底新增 `ContactBand` 联系带、页脚改深色居中。高保真设计稿在 `docs/prototypes/spacious-home/`。同日曾按用户要求加入 Name/Email/Message 静态表单（FormSubmit 转发），后因国内邮箱延迟/收不到，2026-09-29 已移除，恢复纯邮箱展示。
- `materials/` —— 用户投放新素材的固定入口；解析后按 `materials/视频/` 与 `materials/文字/` 分目录归档（单条 Markdown，frontmatter 与集合字段对齐），再入库对应 collection 并去重（URL 相同或同文转载只留一条）。
- `docs/pending-assets.md` —— 待用户补充的素材清单（社媒平台链接、More about Jodie 照片、文晶Talk 代表文章等）。
- `docs/superpowers/specs/2026-10-30-article-detail-pages-design.md` —— 2026-10-30 已实现的「第三方文字内容站内详情页」试点设计：`detail` + `articleBodies` 数据模型、三语动态路由、ArticlePage/ArticleDetail 版式、列表内链、版权与 bidi 规则。
- `docs/content-operations-sop.md` —— 上线后的内容运营流程 SOP（2026-08-09 与用户确认：**不建后台**，保持「运营投素材到 `materials/` → AI 代理解析入库开 PR → 审核人合并 → Vercel 自动发布」）。部署方式：GitHub 托管代码 + Vercel 构建发布。

## 3. 技术栈（规格已确定）

- **Astro 5** + TypeScript（Astro 默认配置），`output: 'static'`，产物为纯静态 HTML/CSS/JS
- **Tailwind CSS**（`@tailwindcss/vite` 集成）
- 本机环境：Node v26.3.1 + npm 11.16.0，无需额外安装运行时
- **不引入任何前端框架组件**（React/Vue 等），保持零运行时 JS 依赖——语言切换靠路由，移动端导航折叠用纯 CSS checkbox 方案

## 4. 架构要点

### 三语路由（Astro 内置 i18n）

- `defaultLocale: 'en'`（国际受众优先），`locales: ['en', 'zh', 'ar']`，`prefixDefaultLocale: false`
- 英文 `/about`，中文 `/zh/about`，阿语 `/ar/about`；桌面端导航语言切换为 `<details>` 下拉（触发器显示当前语言，面板列出另两种语言路径），移动端汉堡菜单内保持 EN / 中文 / العربية 平铺链接
- 阿语页 `<html lang="ar" dir="rtl">`，英文/中文页显式 `dir="ltr"`；方向相关样式一律用 Tailwind 逻辑属性（`ms-/me-/ps-/pe-/start-/end-` 等），不用物理方向类
- UI 字符串集中在 `src/i18n/ui.ts` 字典（三语），按 locale 取用；路由工具在 `src/i18n/utils.ts`
- 阿语文案（UI 字典与长文页面）为 AI 翻译，**待用户校对**

### 页面（8 个页面 × 3 语言一一对应）

`/`（首页 Hero + 专著 + 最新发表 + 视频卡片（featured 优先、日期倒序前 3）+ 活动轮播（`ActivityCarousel`，仅展示有 `cover` 的活动，日期倒序最多 5 张；纯 CSS 左右箭头 + 圆点指示器轮播，隐藏 input 用 fixed 定位防页面跳动；View all 无条件显示；无 `url` 的活动纯展示不可点击）+ More about Jodie 照片墙）、`/about`（履历）、`/book`（专著《美国的中东政策研究（2009-2017）》）、`/publications`（文章列表，按年份分组，静态展示不做交互过滤）、`/media`（`MediaBrowser` 组件：纯 CSS 媒体筛选标签 + 视频横向卡片（左封面右简介）+ 采访/引用紧凑单行，视频默认 4 条、采访默认 10 条，超出纯 CSS 展开）、`/activities`（论坛/二轨对话；用户提供完整活动稿件时，可新增对应的三语站内详情页，如 `/activities/2026-trends-conference-abu-dhabi/`）、`/social`（社媒平台卡片 + 文晶Talk 精选，平台数据在 `src/data/socials.ts`，无 `url` 且无 `qr` 的平台隐藏）、`/contact`（邮箱 jodiewen.ox@gmail.com + 页底联系带）。

详情页：带 `detail: true` 且 `articleBodies` 中存在对应语言正文的条目，会生成 `/publications/<id>/`、`/media/<id>/`、`/activities/<id>/` 三语页面；版式由 `ArticlePage`/`ArticleDetail` 复用 TRENDS 活动稿的样式（返回链接、kicker、标题、16:9 封面、Markdown 正文、来源署名 + 原文链接）。`PublicationList`、`ActivityList`、`ActivityCarousel`、`MediaRow` 对 `detail` 条目自动改用站内链接。**当前所有 50 篇文字内容均已转换**：30 篇全文，20 篇为摘要页（正文以「摘要 / Summary / ملخص」开头，明确说明不转载全文）。视频条目仍为外链视频卡，不生成详情页。

### 内容模型（Astro Content Collections，zod 校验）

`src/content.config.ts` 定义五个集合，条目为 Markdown 文件，frontmatter 携带中英字段，阿语字段可选：

- `publications`：`titleEn`/`titleZh`/`titleAr`(可选)/`outlet`/`date`/`url`/`lang`/`cover`(可选)/`detail`(可选，站内全文)
- `media`：`titleEn`/`titleZh`/`titleAr`(可选)/`type`(video/interview/mention)/`outlet`/`date`/`url`/`embedUrl`(可选)/`platform`(youtube/bilibili/cgtv/other)/`featured`(可选，首页视频卡片优先)/`cover`(可选，本地封面路径，缺省用平台色渐变占位；CGTN 封面可用 `api.cgtn.com` 回放 API + ffmpeg 截帧生成)/`summaryEn`/`summaryZh`(可选，Media 页横向卡片简介)/`detail`(可选)
- `activities`：`titleEn`/`titleZh`/`titleAr`(可选)/`event`/`location`/`eventZh`/`locationZh`/`eventAr`/`locationAr`(可选)/`date`/`url`(可选，支持外部来源 URL 或以 `/` 开头的站内详情路径)/`cover`(可选，本地封面路径，首页轮播只展示有 `cover` 的活动)/`detail`(可选)
- `gallery`：`image`/`captionEn`/`captionZh`/`captionAr`/`date`(可选)——首页「More about Jodie」照片墙
- `articleBodies`：`sourceCollection`(publications/media/activities)/`sourceId`/`locale`(en/zh/ar)/`sourceLang`/`title`/`sourceName`/`coverCredit`(可选)——站内全文的三语 Markdown 正文，按 `sourceId + locale` 与原条目关联；`title` 是该语言的标题，`sourceName` 用于文末“原载于”署名。

长文内容（bio 全文、书籍简介、文晶Talk 介绍）**不进集合**，直接写在对应页面的 Astro 模板里（英文页写英文，`/zh/` 页写中文）。第三方文章的站内全文则进 `articleBodies`，每篇每种语言一个 Markdown 文件。

### 组件

`src/components/` 下小型单职责组件（`BaseLayout`、`Nav`、`Footer`、`Hero`、`SectionHeader`、`TimelineItem`、`PublicationList`、`MediaCard`、`MediaBrowser`、`MediaRow`、`VideoCard`、`Gallery`、`SocialIcon`、`ActivityList`、`ActivityCarousel`、`ContactBand`、`ContactBlock`、`ArticlePage`、`ArticleDetail`）。**页面只组装组件与数据，不写业务逻辑。** `ContactBand`（页底联系带：标题 + 副标题 + 纯文本邮箱展示 + 社媒圆点 + 单位行）由 `BaseLayout` 在 `</main>` 后统一挂载，全站所有页面显示。（2026-09-28 曾按用户要求内嵌 FormSubmit 表单，因转发到国内邮箱延迟/收不到，2026-09-29 用户决定移除表单，恢复纯邮箱展示。）

## 5. 构建与验证命令（实现后生效）

```bash
npm run dev        # 本地预览
npm run build      # 构建纯静态产物
npx astro check    # 类型检查
```

验收标准（来自规格第 8 节）：

1. `npm run build` 成功，`astro check` 无类型错误
2. 逐页人工检查：8 个基础页面 × 3 语言 + 150 个详情页（177 路由）全部可达
3. 每页语言切换链接指向对应的另一语言同页
4. 移动（375px）与桌面（1280px）宽度布局检查
5. 构造一条缺字段的坏数据验证 content collection schema 能拦截（验证后删除）
6. 构建后抽查主要外链可达性

无自动化测试框架，验证以构建 + 类型检查 + 人工页面走查为主。

## 6. 开发约定

- **YAGNI 红线**（规格第 9 节明确列为非目标）：评论、搜索、暗色模式、动画特效库、CMS 接入、部署配置。不要主动添加这些功能。文章/活动详情页已按用户要求全量实现；新增文字链接仍按 `articleBodies` 模式生成三语详情页，文末必须保留原文链接与来源署名；视频仍外链。（联系表单曾于 2026-09-28 加入，2026-09-29 已移除，恢复纯静态零 JS。）
- 零客户端 JS：交互需求优先用路由与纯 CSS 解决。
- 外链一律 `target="_blank" rel="noopener"`。
- 视频 `embedUrl` 缺失时降级为链接卡片，不渲染 iframe。
- 无素材的版块渲染空态文案（如「内容整理中」），不报错。
- 视觉：现代简约国际感，黑白灰 + 点缀色深青 `#0F766E`（联系带用深色延伸 `#115e59`，`--color-accent-dark`）；系统字体栈（不用网络字体，避免国内访问问题）；标题用衬线 `"Georgia", "Songti SC", serif` 增加学术感；移动优先响应式；页面内容容器 `mx-auto max-w-6xl px-6`（导航同宽，通栏版块除外），散文段落另用 `.measure` 限宽 72ch。

## 7. 素材与安全注意事项

- 文章/采访链接等素材由实现方**联网搜集公开信息**（关键词见规格第 6 节：`Jodie Wen Tsinghua`、`文晶 清华`、`文晶Talk` 等）；每条素材须记录来源 URL。
- 视频嵌入差异化：中文页优先国内平台（B站/CGTN），英文页优先 YouTube。
- 找不到真实链接的条目用占位符，交付时附《待补充素材清单》。
- 肖像照与书封用户尚未提供，先用灰色占位块。
- 站内全文：30 篇可公开抓取的来源放全文；20 篇摘要页（SCMP、FT、Berlingske、联合早报等 18 篇付费墙/反爬来源，加 CGTN Radio、CISS 纯 PDF 页 2 篇）只做摘要 + 原文链接，不整篇转载。每篇必须保留 `url` 原文链接、`sourceName` 署名和 `coverCredit`（有图时）；三语译文为 AI 初稿，发布前需校对。
- 联系邮箱 jodiewen.ox@gmail.com（2026-09-29 用户要求全站改用此邮箱，原 jodiewen@tsinghua.edu.cn 停用）为规格中明确要求公开的联系方式，可写入页面；除此之外不要虚构或公开任何个人私密信息。

## 8. 部署

生产域名：**https://jodiewen.com**（2026-09-28 用户确认，自动 301 到 www；GitHub 托管 + Vercel 自动构建发布）。构建产物必须是**纯静态文件**，可部署到任意静态托管。不要添加任何依赖特定平台的服务端配置。
