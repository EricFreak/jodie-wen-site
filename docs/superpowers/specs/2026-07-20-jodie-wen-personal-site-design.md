# Jodie Wen 个人宣传网站 — 设计规格

- 日期：2026-07-20
- 状态：设计已获用户批准，待规格审阅
- 项目目录：`/Users/eric/kimi-projects/jodie-wen-site/`

## 1. 目标与受众

为文晶（Jodie Wen，清华大学战略与安全研究中心研究员、中国论坛国际传播主任）建立一个个人宣传网站，集中展示：

- 学术身份与履历（清华大学 CISS Fellow、北大中东研究博士、牛津访问学者）
- 专著《美国的中东政策研究（2009-2017）》
- 公开发表的文章与评论
- 媒体采访视频与采访链接（NYT、BBC、SCMP、CGTN、凤凰卫视、China-US Focus 等）
- 个人自媒体品牌「文晶Talk」
- 国际论坛与中美中东二轨对话活动经历

受众：国际学术界与政策圈、中外媒体、会议邀请方。成功标准：访客能在 1 分钟内了解她的身份与专长，能找到文章/视频/联系方式；中英双语完整对应。

## 2. 已确认的决策（来自需求澄清）

| 决策点 | 结论 |
|---|---|
| 语言 | 中英双语切换 |
| 内容版块 | 参考 bilal-y-saab.com：首页 / 关于 / 著作 / 发表 / 媒体 / 活动 / 文晶Talk / 联系 |
| 素材来源 | 由实现方联网搜集公开文章与采访链接；找不到的用占位符并给补充清单 |
| 采访视频 | 全部为在线视频（嵌入或外链，不自行托管） |
| 部署 | 先本地构建，部署目标以后再定；产物必须是纯静态文件 |
| 视觉风格 | 现代简约国际感（不参考 bilal-y-saab.com 的视觉） |
| 架构 | 静态站点生成器（用户明确选择，非单页方案） |

## 3. 技术栈

- **Astro 5**（本机已有 Node v26.3.1 + npm 11.16.0，无需额外安装运行时）
- **Tailwind CSS**（@tailwindcss/vite 集成）
- TypeScript（Astro 默认配置）
- 输出：`output: 'static'`，构建产物为纯静态 HTML/CSS/JS，可部署到任意静态托管
- 不引入任何前端框架组件（React/Vue 等），保持零运行时 JS 依赖（语言切换靠路由，不靠客户端 JS）

## 4. 架构

### 4.1 双语路由

- Astro 内置 i18n 路由：`defaultLocale: 'en'`（国际受众优先），`locales: ['en', 'zh']`
- 路由形式：英文 `/about`，中文 `/zh/about`（`prefixDefaultLocale: false`）
- 导航栏固定语言切换链接（EN ⇄ 中文），指向当前页面对应的另一语言路径
- UI 字符串（导航、按钮、标签）集中在 `src/i18n/ui.ts` 字典，按 locale 取用

### 4.2 页面（双语一一对应）

| 路由（英文） | 中文路由 | 内容 |
|---|---|---|
| `/` | `/zh/` | Hero（姓名、头衔、肖像占位、一句话定位、CTA）+ 各版块精选入口（著作、最新文章、媒体墙） |
| `/about` | `/zh/about` | 完整履历：bio 全文、教育经历、职业经历时间线、研究领域 |
| `/book` | `/zh/book` | 《美国的中东政策研究（2009-2017）》：封面占位、简介、出版信息、购买/出版社链接 |
| `/publications` | `/zh/publications` | 发表文章列表：按年份分组静态展示（不做交互过滤，YAGNI）；每条含标题、媒体、日期、外链 |
| `/media` | `/zh/media` | 采访视频（嵌入）+ 采访/引用链接列表 + 合作媒体墙 |
| `/activities` | `/zh/activities` | 国际论坛、二轨对话、演讲等活动列表 |
| `/talk` | `/zh/talk` | 「文晶Talk」品牌介绍 + 代表内容链接 |
| `/contact` | `/zh/contact` | 邮箱 jodiewen@tsinghua.edu.cn、机构信息；不做联系表单（静态站需第三方服务，YAGNI） |

### 4.3 内容模型（Astro Content Collections）

`src/content.config.ts` 定义三个集合，条目统一为 Markdown 文件（frontmatter 携带中英双字段）：

- `publications`：`titleEn`、`titleZh`、`outlet`、`date`、`url`、`lang`（原文语种标记）
- `media`：`titleEn`、`titleZh`、`type`（video/interview/mention）、`outlet`、`date`、`url`、`embedUrl`（可选，视频嵌入地址）、`platform`（youtube/bilibili/cgtv/other）
- `activities`：`titleEn`、`titleZh`、`event`、`location`、`date`、`url`（可选）

长文内容（bio 全文、书籍简介、文晶Talk 介绍）不用集合，直接写在对应页面的 Astro 模板里（英文页写英文，`/zh/` 页写中文），因为这些内容每语言只有一份且结构各异。

### 4.4 组件

`src/components/` 下的小型单职责组件：

- `BaseLayout.astro`（HTML 骨架、字体、SEO meta、lang 属性）
- `Nav.astro`（导航 + 语言切换，当前页高亮）
- `Footer.astro`（版权、邮箱）
- `Hero.astro`（首页 Hero 区）
- `SectionHeader.astro`（版块标题统一样式）
- `TimelineItem.astro`（履历时间线条目）
- `PublicationList.astro`（文章列表，按年份分组）
- `MediaCard.astro`（视频/采访卡片，按 platform 渲染嵌入或链接卡片）
- `ActivityList.astro`、`TalkIntro.astro`、`ContactBlock.astro`

页面只组装组件与数据，不写业务逻辑。

## 5. 视觉设计

- 风格：现代简约国际感——大留白、黑白灰 + 单一点缀色
- 点缀色：深青 teal（`#0F766E`），hover/链接/强调使用
- 字体：系统字体栈——英文 `-apple-system, "Segoe UI", Roboto, "Helvetica Neue"`；中文 `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei"`；标题用衬线 `"Georgia", "Songti SC", serif` 增加学术感。不使用网络字体（避免国内访问问题）
- 布局：移动优先响应式；正文最大宽度约 72ch；导航在移动端用纯 CSS checkbox 方案折叠为汉堡菜单（零客户端 JS）
- 不做暗色模式（YAGNI）
- 肖像照与书封：用户尚未提供，先用灰色占位块，交付时列入待补充清单

## 6. 素材搜集计划

实现阶段先联网搜索公开素材并整理为内容集合数据：

- 搜索关键词：`Jodie Wen Tsinghua`、`文晶 清华`、`文晶Talk`、`Wen Jing CISS`、`文晶 CGTN`、`文晶 凤凰卫视` 等
- 目标来源：CGTN、凤凰卫视、China-US Focus、SCMP、NYT、清华 CISS 官网、中国论坛活动页
- 视频嵌入差异化：中文页优先嵌入国内平台（B站/CGTN），英文页优先 YouTube（YouTube 国内不可见、B站海外加载慢）
- 每条素材记录来源 URL；找不到真实链接的条目用占位符并在交付时提供《待补充素材清单》

## 7. 错误处理与边界

- 外链全部 `target="_blank" rel="noopener"`；构建后抽查主要外链可达性
- 视频 `embedUrl` 缺失时降级为链接卡片（不渲染 iframe）
- 内容集合 frontmatter 由 Astro 的 schema（zod）校验，缺字段构建期即报错
- 无素材的版块正常渲染空态文案（如「内容整理中」），不报错

## 8. 验证

- `npm run build` 成功，`astro check` 无类型错误
- `npm run dev` 本地预览，逐页人工检查：8 个页面 × 2 语言路由全部可达
- 语言切换链接在每个页面指向对应的另一语言同页
- 移动宽度（375px）与桌面宽度（1280px）布局检查
- 内容集合中缺字段的条目能被 schema 拦截（构造一条坏数据验证一次，随后删除）

## 9. 非目标（YAGNI）

- 联系表单、评论、搜索功能
- 博客/文章详情页（文章一律外链到原媒体）
- 暗色模式、动画特效库
- CMS 接入
- 部署配置（部署目标未定，产物保证通用静态文件即可）

## 10. 待用户补充的素材（实现后列出完整清单）

- 肖像照（首页 Hero 与 About 页）
- 《美国的中东政策研究（2009-2017）》封面图
- 书籍购买/出版社链接
- 文晶Talk 的平台与代表内容链接
- 任何联网搜集未找到的采访/文章链接
