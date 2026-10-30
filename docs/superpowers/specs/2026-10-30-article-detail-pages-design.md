# 第三方文字内容站内详情页设计（全量）

- 日期：2026-10-30
- 状态：2026-10-30 全量已实现、合并上线（50 篇 × 3 语，177 路由）
- 关联：`AGENTS.md` §4/§6/§7、`docs/content-operations-sop.md` §2.1

## 1. 背景与目标

网站上的文章、采访、活动多数直接外链第三方（微信公众号、CISS、中美聚焦、SCMP、FT 等）。用户希望把**关键图文内容留在站内**，用现有 TRENDS 活动详情页的版式呈现，同时在文末保留原文链接与来源署名。

先以 3 篇试点验证抓取、清洗、三语翻译、版式和列表内链，随后扩展到全部 50 篇文字内容（32 篇全文 + 18 篇付费墙/反爬摘要，另加 CGTN Radio 与 CISS 纯 PDF 页 2 篇摘要）。

## 2. 最初试点范围

| 原文 | 类型 | 原文语言 | 来源 |
|---|---|---|---|
| CISS《From Reliance on the United States to the Pursuit of Strategic Autonomy》 | publication | en | ciss.tsinghua.edu.cn |
| 中美聚焦《美伊谈判历史根源、现状和前景》 | publication | zh | cn.chinausfocus.com |
| CISS 公众号《文晶应邀参加2026年阿布扎比希利论坛》 | activity | zh | mp.weixin.qq.com |

## 3. 数据模型

- 原条目（publications/media/activities）加 `detail: true`；publications 新增可选 `cover`。
- 新增 `articleBodies` 集合：一篇原文每种语言一个 Markdown 文件，文件名 `<sourceId>.<locale>.md`。
- `articleBodies` frontmatter：`sourceCollection`、`sourceId`、`locale`、`sourceLang`、`title`、`sourceName`、`coverCredit`（可选）。
- 列表组件按 `detail` 判断：true → 站内详情；false → 原外链。
- 新增可选阿语字段：`titleAr`（三个集合）、`eventAr`/`locationAr`（activities）；阿语详情页与列表优先使用，缺省回退英文。

## 4. 路由与版式

- 动态路由：`/publications/[slug]/`、`/media/[slug]/`、`/activities/[slug]/`，各含 en/zh/ar 三份。
- 组件：`ArticlePage`（版式）+ `ArticleDetail`（取数、渲染 Markdown、拼 kicker/来源）。
- 版式复用 TRENDS 稿：返回链接、kicker（媒体/活动 + 日期）、H1、16:9 封面、可选封面署名、译文提示、Markdown 正文、文末“原载于…”+“阅读原文”。
- 正文样式：`.article-body` 控制段落间距、`##` 标题、列表、引文；页面容器 `max-w-4xl`。
- 阿语页 RTL；列表中的英文标题、ISO 日期用 `<bdi>`/`dir="ltr"` 隔离，避免问号移位和日期倒序。

## 5. 内容与版权规则

- 只对用户确认可转载/自有的内容放全文；SCMP、FT、Berlingske、联合早报等付费墙媒体默认摘要 + 原文链接。
- 每篇保留原文 `url`、`sourceName`、`coverCredit`；正文不改事实、数字、引语。
- 三语译文为 AI 初稿，阿语需人工校对；页面显示“AI 翻译，待校对”。
- 封面：优先原文 og:image/正文图并压缩；无图时用中性设计封面，不盗用付费媒体图片。

## 6. 验证

- 最终 `npm run build` 177 路由；`npx astro check` 0 errors。
- 150 个详情页本地与生产均 200；语言切换成对；列表内链正确；原文链接 `target="_blank" rel="noopener"`。
- 桌面 1440 / 窄屏 500 走查；阿语 RTL、日期、标题 bidi 检查。
- 内部链接全量扫描 0 断链。

## 7. 已知限制

- CISS 封面是生成的英文标题卡，中/阿页也显示英文封面；如需本地化封面，后续给 `articleBodies` 加可选 `cover`。
- 列表页除试点条目外，阿语仍回退英文标题。
- 20 篇摘要页（18 篇付费墙/反爬 + CGTN Radio、CISS 纯 PDF 页）不是全文；如获授权可补全文。
- 部分无图来源使用本站生成的英文标题封面，中/阿页共用。
- 三语译文为 AI 初稿，仍需人工校对，阿语优先。
