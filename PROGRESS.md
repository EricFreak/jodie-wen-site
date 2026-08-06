# 项目进度存档 — Jodie Wen 个人宣传网站

> 最后更新：2026-08-06。本文档用于跨工具交接，继续工作时请先读它。

## 当前状态

**网站已上线**：`https://jodie-wen.vercel.app`（Vercel，8 页 × 3 语言共 24 路由，图片资源正常）。

- 2026-08-06（三轮）：Media 页视频卡缩略图改垂直居中；29 条 media 外链全部经真实浏览器复验可达（SCMP 反爬 curl 但浏览器 200，无死链移除；SCMP 3/24 条目标题按官网现标题修正）；社媒挂载 LinkedIn / X（@JingWenOxford）/ 微博（uid 1969913095，昵称「文晶Talk」）三个已核实账号，页脚图标同步加微博
- 2026-08-06（二轮）：Media 页重构——① 首页媒体标签楼层删除，标签移到 Media 页升级为**纯 CSS radio 筛选器**（按媒体过滤三个区域，标签自动生成带计数，零 JS）；② CGTN 视频通过官方 API（`api.cgtn.com/website/api/live/channel/replay/{id}/info`）取 m3u8 + ffmpeg 截真实关键帧做封面（`public/images/media/` 5 张，填入 `cover` 字段；凤凰卫视无流可取，保留渐变占位）；③ Media 页视频改横向卡片（左封面右标题+简介+日期），media schema 加 `summaryEn`/`summaryZh`；④ 视频区默认 4 条、采访区默认 10 条紧凑单行，超出纯 CSS 展开（筛选时自动全显）；新组件 `MediaBrowser`/`MediaRow`，新数据文件 `src/data/outlets.ts`
- 2026-08-06：媒体版块改版 + Social Media 页上线（规格：[`docs/superpowers/specs/2026-08-05-media-social-redesign-design.md`](docs/superpowers/specs/2026-08-05-media-social-redesign-design.md)）：① 首页 Media 改为 3 张视频卡片（latest 逻辑：featured 优先、日期倒序取前 3，封面卡片挂外链，不下载视频）+ 保留媒体墙小标签；② 首页底部新增「More about Jodie」照片墙（新 `gallery` 集合，无照片显示空态）；③ `/talk` 改名 `/social`（社媒平台卡片，数据在 `src/data/socials.ts`，无链接平台先隐藏；旧 `talk.astro`×3 与 `TalkIntro.astro` 已删）；④ 页脚加社媒图标（点击进 `/social`）；⑤ Media 页拆为 视频卡片网格 / 文字采访 / 媒体引用 三段。同日：materials 素材工作流建立（`materials/视频` + `materials/文字` 分目录归档，脚本 `scripts/ingest-2026-h1-media.py`），2026 上半年采访 docx 解析入库 22 条（media +21、publications +1），与现有条目去重 5 条；另修复 Safari 肖像变形（`w-fit`→`w-auto`，Safari 对 fit-content 不按宽高比换算，已上线 `5fde24b`）
- 2026-07-21：新增阿拉伯语第三语言（`/ar/`，RTL），已 push 部署并线上复验（`/ar/`、`/ar/about` 200，`lang="ar" dir="rtl"` 生效，英中页无回归）；桌面端语言切换改为 `<details>` 下拉（触发器=当前语言，面板列另两种语言），移动端汉堡菜单内保持平铺。**阿语文案为 AI 翻译，待用户校对**；终审遗留小项：ar 版 `hero.kicker` 跟随中文版含中国论坛职务（英文版无，校对时确认是否对齐）、book 页 h1→h3 标题层级为三语共有结构、favicon.ico 缺失 404（可入 pending-assets）
- 2026-07-21（下午）：修复移动端肖像被 flex stretch 挤压变形（`w-auto`→`w-fit`，Hero + 三语 about 页，已上线 `90cbbe4`）；移动端 UI 优化：首页 Hero 整体居中、About 肖像居中（桌面端不变，已上线 `18801e4`）
- **进行中（明天继续）**：内容上传工具 `/studio`——手机聊天框贴链接 → Kimi API 解析 → 按现有卡片样式预览 → 确认后自动提交上线。设计规格已写：[`docs/superpowers/specs/2026-07-21-content-studio-design.md`](docs/superpowers/specs/2026-07-21-content-studio-design.md)，状态「待用户最终确认」。继续时说「读 content-studio 规格继续」；届时需用户配三个 Vercel 环境变量（`MOONSHOT_API_KEY`、`STUDIO_PASSCODE`、`GITHUB_TOKEN`）

- 部署方式：Vercel 连接 GitHub 仓库 `EricFreak/jodie-wen-site`，push 到 main 自动构建部署（Astro 零配置）；PR 分支有预览链接
- Vercel Authentication（部署保护）已关闭，站点公开可访问
- 注意：`*.vercel.app` 国内访问不稳定；将来可绑自有域名彻底解决
- 本地：`npm run dev` 预览；`npm run build` + `npx astro check` 验证（全部通过）

终验结果（2026-07-20）：16 路由全部可达、语言切换链接成对正确、坏数据被 content schema 拦截、24 条外链经代理抽查全部可达。
待补充素材完整清单：[`docs/pending-assets.md`](docs/pending-assets.md)。

## 规格文档

完整设计规格：[`docs/superpowers/specs/2026-07-20-jodie-wen-personal-site-design.md`](docs/superpowers/specs/2026-07-20-jodie-wen-personal-site-design.md)

增量规格（2026-07-21）：

- 阿拉伯语第三语言：[`docs/superpowers/specs/2026-07-21-arabic-locale-design.md`](docs/superpowers/specs/2026-07-21-arabic-locale-design.md)（实施计划同名文件在 `docs/superpowers/plans/`）
- 语言切换下拉化：[`docs/superpowers/specs/2026-07-21-language-switcher-dropdown-design.md`](docs/superpowers/specs/2026-07-21-language-switcher-dropdown-design.md)

原始规格核心决策：

- **技术栈**：Astro 5 + Tailwind CSS，静态输出（本机已有 Node v26.3.1）
- **双语**：Astro i18n 路由，英文为默认（`/about`），中文在 `/zh/` 前缀下；导航有 EN⇄中文 切换
- **页面**：首页 / about / book / publications / media / activities / talk（文晶Talk）/ contact，中英一一对应
- **内容**：Astro Content Collections（publications / media / activities 三个集合，frontmatter 中英双字段）
- **视觉**：现代简约国际感，黑白灰 + 深青点缀色 `#0F766E`，系统字体栈（不用网络字体）
- **素材**：实施时联网搜集公开文章/采访链接；视频全在线（中文页优先国内平台嵌入，英文页优先 YouTube）；找不到的留占位符 + 交付《待补充素材清单》

## 素材源文件

- Bio：`/Users/eric/Downloads/Jodie WEN' s Bio.docx`（文件名含 Unicode 撇号 U+2019，用通配符 `Jodie*Bio.docx` 访问；中英双语 bio 全文已摘录在规格思考的对话中，实施时可重新用 `textutil -convert txt -stdout` 提取）
- 参考结构：https://bilal-y-saab.com （仅参考版块结构，不参考视觉）

## 环境注意

- 远程仓库：`https://github.com/EricFreak/jodie-wen-site`（Public，2026-07-20 首次推送，origin/main 跟踪 main）
- **GitHub 直连不通**，需走本地代理 `http://127.0.0.1:7890`（curl 加 `-x`；本仓库已设 `git config http.proxy http://127.0.0.1:7890`，push/pull 直接可用；gh 命令需 `HTTPS_PROXY` 环境变量）
- npm  registry 直连是否正常未验证；若慢可换国内镜像
- superpowers 插件仓库在 `~/.kimi-code/superpowers`（已配 git 代理）

## 待用户补充的素材

以 [`docs/pending-assets.md`](docs/pending-assets.md) 为权威完整清单。肖像照与书封图已接入完毕；剩余：文晶Talk 代表文章链接、采访视频嵌入 ID、SCMP 可读替代链接、未核实到的文章/采访/活动线索。书籍购买链接已解决（当当网，见 Book 页）。

## 如何继续

1. VSCode 打开本目录：`/Users/eric/kimi-projects/jodie-wen-site/`
2. 用 Kimi Code（或其他 agent）时说：「读 PROGRESS.md 继续这个项目」
3. 补充素材：把文件/链接交给 agent，按 `docs/pending-assets.md` 逐项接入；改完 push 到 main 即自动部署上线
