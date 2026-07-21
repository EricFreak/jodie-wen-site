# AGENTS.md — Jodie Wen 个人宣传网站

> 本文件面向 AI 编码代理，假设读者对本项目一无所知。
> 项目中文化档为主，沟通与文档默认使用中文。

## 1. 项目概览

为文晶（Jodie Wen，清华大学战略与安全研究中心 CISS Fellow、中国论坛国际传播主任）建设的**个人宣传网站**，集中展示其学术履历、专著、发表文章、媒体采访、「文晶Talk」自媒体品牌与国际论坛活动。

- 受众：国际学术界与政策圈、中外媒体、会议邀请方。
- 成功标准：访客 1 分钟内了解其身份与专长，能找到文章/视频/联系方式；**中英阿三语完整对应**（阿语文案为 AI 翻译，待用户校对）。
- 内容版块参考 bilal-y-saab.com 的信息架构（视觉不参考）。

## 2. 当前状态（重要）

**实现已完成，构建通过。** 目录结构已按 §4 落地（`src/pages` 8 页 × 中英阿三语、`src/components` 11 个组件、`src/content` 三个集合共 23 条真实条目），§5 所列构建与验证命令均已生效。2026-07-21 新增阿拉伯语第三语言（`/ar/`，RTL），共 24 路由。

- `docs/superpowers/specs/2026-07-20-jodie-wen-personal-site-design.md` —— 已获用户批准的完整设计规格（目标、技术栈、架构、视觉、验证方案）；规格与本文如有出入，以规格文档为准。
- `docs/pending-assets.md` —— 待用户补充的素材清单（肖像照、书封图、文晶Talk 平台链接等）。

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

`/`（首页 Hero + 精选入口）、`/about`（履历）、`/book`（专著《美国的中东政策研究（2009-2017）》）、`/publications`（文章列表，按年份分组，静态展示不做交互过滤）、`/media`（采访视频 + 链接 + 媒体墙）、`/activities`（论坛/二轨对话）、`/talk`（文晶Talk）、`/contact`（邮箱 jodiewen@tsinghua.edu.cn，**不做联系表单**）。

### 内容模型（Astro Content Collections，zod 校验）

`src/content.config.ts` 定义三个集合，条目为 Markdown 文件，frontmatter 携带中英双字段：

- `publications`：`titleEn`/`titleZh`/`outlet`/`date`/`url`/`lang`
- `media`：`titleEn`/`titleZh`/`type`(video/interview/mention)/`outlet`/`date`/`url`/`embedUrl`(可选)/`platform`(youtube/bilibili/cgtv/other)
- `activities`：`titleEn`/`titleZh`/`event`/`location`/`eventZh`/`locationZh`（活动与地点的中文译名）/`date`/`url`(可选)

长文内容（bio 全文、书籍简介、文晶Talk 介绍）**不进集合**，直接写在对应页面的 Astro 模板里（英文页写英文，`/zh/` 页写中文）。

### 组件

`src/components/` 下小型单职责组件（`BaseLayout`、`Nav`、`Footer`、`Hero`、`SectionHeader`、`TimelineItem`、`PublicationList`、`MediaCard`、`ActivityList`、`TalkIntro`、`ContactBlock`）。**页面只组装组件与数据，不写业务逻辑。**

## 5. 构建与验证命令（实现后生效）

```bash
npm run dev        # 本地预览
npm run build      # 构建纯静态产物
npx astro check    # 类型检查
```

验收标准（来自规格第 8 节）：

1. `npm run build` 成功，`astro check` 无类型错误
2. 逐页人工检查：8 个页面 × 3 语言（24 路由）全部可达
3. 每页语言切换链接指向对应的另一语言同页
4. 移动（375px）与桌面（1280px）宽度布局检查
5. 构造一条缺字段的坏数据验证 content collection schema 能拦截（验证后删除）
6. 构建后抽查主要外链可达性

无自动化测试框架，验证以构建 + 类型检查 + 人工页面走查为主。

## 6. 开发约定

- **YAGNI 红线**（规格第 9 节明确列为非目标）：联系表单、评论、搜索、博客/文章详情页（文章一律外链原媒体）、暗色模式、动画特效库、CMS 接入、部署配置。不要主动添加这些功能。
- 零客户端 JS：交互需求优先用路由与纯 CSS 解决。
- 外链一律 `target="_blank" rel="noopener"`。
- 视频 `embedUrl` 缺失时降级为链接卡片，不渲染 iframe。
- 无素材的版块渲染空态文案（如「内容整理中」），不报错。
- 视觉：现代简约国际感，黑白灰 + 点缀色深青 `#0F766E`；系统字体栈（不用网络字体，避免国内访问问题）；标题用衬线 `"Georgia", "Songti SC", serif` 增加学术感；移动优先响应式，正文最大宽度约 72ch。

## 7. 素材与安全注意事项

- 文章/采访链接等素材由实现方**联网搜集公开信息**（关键词见规格第 6 节：`Jodie Wen Tsinghua`、`文晶 清华`、`文晶Talk` 等）；每条素材须记录来源 URL。
- 视频嵌入差异化：中文页优先国内平台（B站/CGTN），英文页优先 YouTube。
- 找不到真实链接的条目用占位符，交付时附《待补充素材清单》。
- 肖像照与书封用户尚未提供，先用灰色占位块。
- 联系邮箱 jodiewen@tsinghua.edu.cn 为规格中明确要求公开的联系方式，可写入页面；除此之外不要虚构或公开任何个人私密信息。

## 8. 部署

部署目标未定。唯一硬性要求：构建产物必须是**纯静态文件**，可部署到任意静态托管。不要添加任何依赖特定平台的服务端配置。
