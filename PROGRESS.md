# 项目进度存档 — Jodie Wen 个人宣传网站

> 最后更新：2026-07-20。本文档用于跨工具交接，继续工作时请先读它。

## 当前状态

**网站已实现并构建通过**（分支 `feat/site-implementation`，Task 1–12 完成，16 页 × 中英双语全部落地）。

验证命令（全部通过）：

```bash
npm run build        # 构建 16 页纯静态产物
npx astro check      # 0 errors / 0 warnings / 0 hints
```

终验记录（16 路由可达、语言切换链接成对、坏数据 schema 拦截、外链抽查）见 `.superpowers/sdd/task-12-report.md`。
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

- **GitHub 直连不通**，需走本地代理 `http://127.0.0.1:7890`（curl/git 加 `-x` / `http.proxy`）
- npm  registry 直连是否正常未验证；若慢可换国内镜像
- superpowers 插件仓库在 `~/.kimi-code/superpowers`（已配 git 代理）

## 待用户补充的素材

以 [`docs/pending-assets.md`](docs/pending-assets.md) 为权威完整清单（肖像照、书封图、文晶Talk 平台链接、未核实到的文章/采访/活动链接）。书籍购买链接已在实施中解决（当当网，见 Book 页），不再需要补充。

## 如何继续

1. VSCode 打开本目录：`/Users/eric/kimi-projects/jodie-wen-site/`
2. 用 Kimi Code（或其他 agent）时说：「读 PROGRESS.md 和 docs/superpowers/specs/ 下的规格」
3. 补充素材：按 `docs/pending-assets.md` 逐项替换占位；补充后 `npm run build` 验证
