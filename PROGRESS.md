# 项目进度存档 — Jodie Wen 个人宣传网站

> 最后更新：2026-07-20。本文档用于跨工具交接，继续工作时请先读它。

## 当前状态

**网站已上线**：`https://jodie-wen.vercel.app`（Vercel，2026-07-20，16 路由复验全部 200，图片资源正常）。

- 部署方式：Vercel 连接 GitHub 仓库 `EricFreak/jodie-wen-site`，push 到 main 自动构建部署（Astro 零配置）；PR 分支有预览链接
- Vercel Authentication（部署保护）已关闭，站点公开可访问
- 注意：`*.vercel.app` 国内访问不稳定；将来可绑自有域名彻底解决
- 本地：`npm run dev` 预览；`npm run build` + `npx astro check` 验证（全部通过）

终验结果（2026-07-20）：16 路由全部可达、语言切换链接成对正确、坏数据被 content schema 拦截、24 条外链经代理抽查全部可达。
待补充素材完整清单：[`docs/pending-assets.md`](docs/pending-assets.md)。

## 规格文档

完整设计规格：[`docs/superpowers/specs/2026-07-20-jodie-wen-personal-site-design.md`](docs/superpowers/specs/2026-07-20-jodie-wen-personal-site-design.md)

实施前请完整阅读。核心决策：

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
