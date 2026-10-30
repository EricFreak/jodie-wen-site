# 内容运营流程 SOP

> 本文档定义网站上线后的日常内容更新流程。**不建后台系统**，内容以 Markdown 存于 Git 仓库，
> 运营投素材 → AI 代理解析入库 → 审核人合并 PR → Vercel 自动发布。

## 角色分工

| 角色 | 职责 |
|------|------|
| 运营 | 收集素材（链接、照片），投递到 `materials/` 目录 |
| AI 代理（Kimi Code） | 解析素材、翻译、生成内容条目、验证构建、推送并开 PR |
| 审核人（文晶指定） | 在 GitHub 审阅并合并 PR |

## 1. 素材投递（运营）

把素材放入仓库的 `materials/` 目录（或发给文晶由其放入）：

- **链接类**（文章、视频、采访）：URL 列表即可，格式不限（docx / txt / md / 微信复制的文本都行），可附备注（媒体名、日期）。按 `materials/视频/`、`materials/文字/` 分目录放置。
- **照片类**（首页「More about Jodie」照片墙）：图片文件 + 一句图注（中文或英文一种即可，另一种由 AI 补译）。

运营不需要懂 Git，也不需要填任何表单字段。

## 2. 解析入库（AI 代理）

投递完成后，在 Kimi Code 中对代理说一句「处理 materials 里的新素材」即可。代理执行：

1. 读取素材，联网解析链接元数据（标题、媒体、日期）
2. 判定归属集合：
   - `publications` —— 署名发表文章
   - `media` —— 视频（`type: video`）、采访（`interview`）、媒体引用（`mention`）
   - `activities` —— 论坛、二轨对话等活动
   - `gallery` —— 照片墙图文
   - `articleBodies` —— 需要站内全文的第三方文章正文（与 publications / media / activities 的原条目关联）
3. 补齐中英字段（AI 翻译初稿）；需要站内全文的条目再补阿语，写入 `articleBodies`（每篇每种语言一个 Markdown 文件）
4. 图片复制到 `public/images/`；CGTN 视频封面可用 `api.cgtn.com` 回放 API + ffmpeg 截帧生成
5. 去重：URL 相同或同文转载只保留一条
6. 按集合 schema（见 `src/content.config.ts`）生成 Markdown 条目到 `src/content/<collection>/`
7. 运行 `npm run build` + `npx astro check` 验证
8. 新建分支提交并推送，在 GitHub 开 PR，PR 描述列出新增条目清单供审核

### 2.1 站内全文（默认流程，2026-10-30 用户全局约束）

**所有文字类链接默认站内化**，不再在列表里直接外链原媒体。按以下步骤执行：

1. 抓取原文正文与封面，清理导航、广告、相关阅读、图片说明、微信页脚等非正文内容；能抓全文就放全文，付费墙/反爬/无正文的只做「关键摘要 + 原文链接」并在正文标注「摘要」
2. 保留原文标题、日期、来源、作者署名；正文不得改动事实、数字、引语
3. 在原条目加 `detail: true`，补 `cover`（本地封面）和 `titleAr`/`eventAr`/`locationAr` 等阿语字段
4. 在 `src/content/articleBodies/` 建 `<sourceId>.en.md`、`.zh.md`、`.ar.md`，frontmatter 按 schema 填 `sourceCollection`/`sourceId`/`locale`/`sourceLang`/`title`/`sourceName`/`coverCredit`
5. 三语正文都要完整，不得删段；阿语为 AI 翻译初稿，PR 里标注待校对
6. 详情页会自动生成 `/publications/<id>/`、`/media/<id>/`、`/activities/<id>/` 三语版本；列表链接文案统一为「阅读全文 / Read full text / اقرأ النص الكامل」，不出现「来源」，来源署名和「阅读原文」只放在详情页末尾
7. 版权：只对用户确认可转载/自有的内容放全文；SCMP、FT、Berlingske 等付费墙媒体默认只做摘要 + 原文链接，不整篇转载

## 3. 审核发布（审核人）

- 审核人在 GitHub 上审阅 PR，重点检查：翻译准确性（尤其阿语）、集合归类、外链是否可达、站内全文是否保留来源与原文链接
- 有问题直接在 PR 里评论，代理按评论修改
- 合并 PR 后 Vercel 自动构建，约 1–2 分钟后上线

## 注意事项

- 阿语文案（UI 字典、长文页面、`articleBodies`）为 AI 翻译，发布前需文晶校对；可在 PR 中直接改
- 站内全文页的封面图必须填 `coverCredit`（如「图片来源：中美聚焦」）；没有合适封面时用中性设计图，不盗用付费媒体图片
- 联系邮箱等公开信息以设计规格为准，不要在内容条目里写入私密信息
- 无素材的版块会渲染空态文案（如「内容整理中」），不是故障
