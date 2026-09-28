# 运营投递后台（极简投递页 + 云端自动入库）设计规格

- 日期：2026-08-09（v2，闭环审计后修订）
- 状态：待用户批准
- 关联：`docs/content-operations-sop.md`（人工版流程，本规格落地后需更新）、`AGENTS.md` §8（纯静态约束的例外说明）

## 1. 背景与目标

网站进入持续运营期，内容更新工作要移交他人。已确认的前提：

- **运营人员只接受傻瓜网页**，不碰 Git，不填中英双字段；工作方式为「投素材（链接 / 照片+图注）」。
- **AI 解析入库必须脱离开发者电脑**，在云端自动完成。
- **需要审核环节**，审核人（文晶指定）在 GitHub 网页上审 PR、合并即发布。
- 部署：GitHub 托管代码 + Vercel 构建发布。

目标：运营打开一个网页，粘贴链接或上传照片，系统自动解析、翻译、归类、生成内容条目并开 PR；审核人合并 PR 后自动上线。开发者电脑不参与日常流程。

非目标（YAGNI）：

- 用户体系 / 多角色权限（只有一个共享密码）
- 内容的编辑、删除界面（改错走 GitHub 网页编辑 PR 文件）
- 草稿箱、定时发布
- 前台页面的任何改动（24 个路由保持纯静态）

## 2. 总体架构

**计算全部放在 GitHub Actions，Vercel 函数只当门卫。** 早期版本把解析管线放 Vercel 函数，闭环审计发现 60s 时限会制造无报告的半截状态，且 ffmpeg、密钥管理分散；v2 起 Vercel 侧只做鉴权与转交。

```
运营浏览器           Vercel（门卫）                GitHub（所有计算）
┌────────┐ 密码登录 ┌────────────────────────┐
│ /admin │ ───────▶ │ /api/intake/*          │  ① 建分支 intake/<ts>
│ 投递表单│ 提交素材 │ - 校验 cookie           │  ② 写入 .intake/request.json（+照片）
│ 投递记录│ ◀─────── │ - 触发 workflow_dispatch│─▶ ③ dispatch
└────────┘ 受理回执  └────────────────────────┘        │
                                                        ▼
                              ┌──────────────────────────────────────┐
                              │ Action A: intake-pipeline             │
                              │ 抓元数据 → LLM 分类/翻译 → 查重        │
                              │ （本仓库文件 + open PR）→ 生成 MD → 开PR│
                              │ Action B: cover-candidates            │
                              │ 视频条目截 4 张候选封面 → PR 评论贴图    │
                              │ Action C: cover-command               │
                              │ 评论「封面 N」选定 /「换一批」重截       │
                              └──────────────────────────────────────┘
                                 审核人审 PR（预览构建绿才合并）→ Vercel 发布
```

- Astro `output: 'static'` 保持不变，安装 `@astrojs/vercel` adapter；仅 `/admin` 与 `/api/*` 标记 `export const prerender = false`，其余 24 个路由照常预渲染为纯静态 HTML。
- LLM 密钥放 GitHub Secrets（不放 Vercel）；Vercel 侧只需一个能写分支和触发 dispatch 的 GitHub PAT。

## 3. 页面与表单（`/admin`）

单一页面，中文界面，不加导航链接、`noindex` + `X-Robots-Tag: noindex`。

- **登录**：一个密码框。校验通过后种签名 cookie（HMAC-SHA256，密钥为环境变量）。无注册、无找回。暴力破解属已接受风险（强密码 + 页面不公开传播），不做速率限制。
- **链接投递表单**：
  - 多行文本框：一行一个 URL，单次最多 10 条（Action 时限充裕，不再受 60s 约束）
  - 类型覆盖下拉：`自动判断 / 文章 / 视频 / 采访（含音频）/ 活动`——运营知道素材性质时手动钉死，以人工指定为准
  - 可选备注（写进 PR 描述供审核人参考）
- **照片投递表单**（More about Jodie 照片墙）：文件选择，客户端 canvas 压缩到长边 ≤2000px JPEG；图注一行（中或英皆可）；可选日期。
- **受理回执**：提交后页面显示「已受理」与分支名，**不承诺即时逐条结果**——结果以 PR 为准。
- **最近投递状态区**（页面下半部分，`GET /api/status` 提供数据）：列出最近的 intake 分支/PR 及其处理运行状态（处理中 / 成功（附 PR 链接）/ 失败（附 Action 日志链接））。管线整个崩掉时运营能在这里看到「失败」，杜绝静默丢失。

视觉沿用现有黑白灰 + 深青 `#0F766E`。零客户端 JS 原则在此页面放宽——表单交互、图片压缩、状态区轮询用少量原生 JS（不引入框架）。

## 4. 受理与处理管线

### 4.0 Vercel 门卫（`POST /api/intake/links`、`POST /api/intake/photo`）

1. 校验 cookie，无效一律 401。
2. 从 main 建分支 `intake/<timestamp>`，写入 `.intake/request.json`（链接清单、类型覆盖、备注；照片单则含图注、日期），照片以压缩后 JPEG 一并提交到 `.intake/`。
3. 触发 `workflow_dispatch`（输入：分支名），秒级返回受理回执。

### 4.1 Action A：intake-pipeline（核心管线，Node 脚本）

检出该分支，读 `.intake/request.json`，逐条处理、逐条隔离失败：

1. **抓取元数据**：GET 页面，提取 `<title>`、og 标签、发布时间；失败（403/超时）时仅保留 URL，交由 LLM 凭 URL 判断并标记低置信度。
2. **分类**（人工未指定时），LLM 依据显式判定清单：
   - 署名文章 → `publications`
   - 识别到真实视频播放器/嵌入（YouTube、B站、CGTN 视频页特征）→ `media` + `type: video`
   - 音频/录音/播客/电台特征 → `media` + `type: interview`（**严禁因「多媒体页」笼统归 video**）
   - 采访、对话、发言报道 → `media` + `type: interview`；仅被提及 → `mention`
   - 论坛、对话活动 → `activities`
   - **拿不准一律向保守分类降级**（video/interview 之争选 interview；收不收之争选收并标注「请审核人确认」）
3. **翻译与摘要**：LLM 补齐中英双字段；media 视频类生成 `summaryEn/summaryZh`；gallery 图注补译三语（`captionEn/captionZh/captionAr`，阿语为 AI 初稿待校对）。
4. **查重**（双源，堵部署滞后与未合并 PR 两个漏洞）：
   - 扫描本地检出的 `src/content/**/*.md` frontmatter 中的 `url`
   - 调 GitHub API 列出 open PR 的变更文件内容，提取 `url`
   - URL 相同判定重复，跳过并列入 PR 报告
5. **生成条目**：按集合 schema 生成 Markdown（文件名 `YYYY-MM-DD-slug.md`），zod 校验，不过列入失败清单；照片从 `.intake/` 移入 `public/images/gallery/`。
6. **开 PR**：提交全部条目（`.intake/` 随提交清理），PR 描述为审核清单表格：标题 / 链接 / 判定结果 / 判定依据一句话 / 状态（含失败与跳过项）。**任何提交都不静默丢弃。**
7. **管线自身崩溃**（LLM key 失效等）：Action 以失败状态结束，运营在「最近投递」看到失败与日志链接；分支上的 `.intake/request.json` 仍在，修复后手动重跑（re-run workflow）即可，素材不丢。

### 4.2 Action B/C：视频封面（候选 + 评论指令）

视频条目（`media` + `type: video`）需关键帧封面。ffmpeg/yt-dlp 在 Actions runner 现成可用：

1. **PR 打开/更新时（Action B）**：扫描 PR 新增的 video 条目，逐条生成 4 张候选：
   - YouTube：直接取官方多帧缩略图（`maxresdefault`、`hq1/2/3.jpg`），不下载视频
   - B站 / CGTN / 直链 mp4：yt-dlp 解析视频流地址，ffmpeg 在时长 10%/30%/50%/70% 截帧
2. **候选入库与贴图**：候选图提交到 PR 分支 `.cover-candidates/<slug>/`（仓库根，不进 `public/`，不部署）；Action 在 PR 发**一条汇总评论**，全 PR 统一编号贴出所有候选图（`blob/<branch>?raw=true` 链接，私有仓库登录可见）——消掉多视频时「封面 N」的歧义。
3. **评论指令（Action C，仅响应 OWNER/MEMBER/COLLABORATOR）**：
   - 「封面 3」（兼容「用第3张」）→ 全局第 3 张复制为 `public/images/media/<slug>.jpg`（沿用现有封面路径约定），更新对应条目 `cover` 字段，清理该条候选目录，回评确认；全部选定后删除汇总评论中的已选项
   - 「换一批」→ 为所有**未选定**的视频换一组时间戳（5%/25%/45%/65% 与 15%/35%/55%/75% 轮换）重截，更新汇总评论；可无限轮直至满意
   - 直接合并不选 → 条目无 `cover`，前台沿用渐变占位，不算故障
4. 视频下载/截帧失败（需登录、解析不了）：汇总评论中该条标注失败原因，条目照常保留，可评论「换一批」重试或之后人工补封面。

## 5. 大模型选型

- 默认 **Moonshot Kimi API**（`https://api.moonshot.cn/v1`，OpenAI 兼容协议），模型 `kimi-k2-0905-preview`。
- 通过 GitHub Secrets `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` 配置，可换成任何 OpenAI 兼容端点，代码不绑定厂商。
- 用量预估：每条内容 1–2 次调用，月成本几元量级。
- 调用方式：原生 `fetch`，JSON 结构化输出，不引 SDK。

## 6. GitHub 集成与密钥

**Vercel 环境变量**：

| 变量 | 用途 |
|------|------|
| `ADMIN_PASSWORD` | 后台登录密码 |
| `ADMIN_COOKIE_SECRET` | cookie HMAC 签名密钥 |
| `GH_INTAKE_TOKEN` | fine-grained PAT：本仓库 Contents 读写 + Actions 读写（建分支、写 `.intake/`、dispatch、查状态） |
| `GH_REPO` | `owner/name` |

**GitHub Secrets**（供 Actions 使用）：`LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL`，以及 `INTAKE_PAT`（与 Vercel 的 `GH_INTAKE_TOKEN` 同一 fine-grained PAT）。开 PR 必须用 PAT 而非 `GITHUB_TOKEN`——`GITHUB_TOKEN` 触发的 pull_request 事件不会再触发工作流（GitHub 防递归限制），否则 cover-candidates 不会自动跑。其余提交、回评用自带 `GITHUB_TOKEN`。

**工作流文件**：

- `.github/workflows/intake-pipeline.yml`（workflow_dispatch）
- `.github/workflows/cover-candidates.yml`（pull_request: opened/synchronize，仅 intake/* 分支）
- `.github/workflows/cover-command.yml`（issue_comment，校验作者是协作者且所在 PR 是 intake PR）

**审核人操作守则**（写进 SOP）：

- **只在 Vercel 预览构建绿色时合并**——坏 frontmatter 会在预览构建阶段拦下，进不了 main；即使误合并，线上站点也停在上一版，不会挂
- 小错（类型、日期、翻译）：GitHub 网页直接编辑 PR 中的 Markdown
- 整条不该收：网页删除该文件，或关闭 PR 让运营重投
- 封面不满意：评论「换一批」；选定：评论「封面 N」

## 7. 代码改动范围

新增：

- `src/pages/admin.astro`（`prerender = false`；登录 + 两个表单 + 最近投递状态区 + 少量原生 JS）
- `src/pages/api/login.ts`、`src/pages/api/intake/links.ts`、`src/pages/api/intake/photo.ts`、`src/pages/api/status.ts`（均 `prerender = false`）
- `src/lib/admin/`：`auth.ts`（cookie 签验）、`github.ts`（建分支/写文件/dispatch/查状态，原生 fetch）
- `scripts/intake-pipeline.mjs`（Action A 主体：抓取/分类/翻译/查重/生成/开 PR）
- `scripts/lib/`：`llm.mjs`、`classify-prompt.mjs`（判定清单）、`fetch-meta.mjs`、`entry-writer.mjs`（zod 校验 + Markdown 生成）
- `scripts/extract-cover-frames.mjs`（Action B/C 复用的截帧逻辑）
- `.github/workflows/` 三个工作流（见 §6）
- `src/lib/schemas.ts`：从 `src/content.config.ts` 抽出四个集合的 zod schema，`content.config.ts` 与 `entry-writer.mjs` 共用

修改：

- `astro.config.mjs`：加 `@astrojs/vercel` adapter
- `package.json`：新增依赖 `@astrojs/vercel`、`zod`（显式声明，供 scripts/ 下的 Node 脚本使用）
- `AGENTS.md` §8：纯静态约束补充例外说明；`docs/content-operations-sop.md`：改为新流程（含审核人守则）
- `.gitignore`：确认 `.env` 已忽略

不改动：现有 24 个前台路由、组件、内容条目。早期版本中的 `url-index.json` 静态查重端点已废弃（查重改在 Action 内双源进行）。

## 8. 错误处理

- 单条：抓取失败 / LLM 失败 / schema 校验失败 / GitHub API 失败——逐条记录原因进 PR 报告，不影响同批其他条目；LLM 输出非预期 JSON 重试一次。
- 重复 URL：跳过并注明「已存在」或「在 PR #N 待审」。
- 整批：全失败仍开 PR（只含失败报告），审核人知情；管线崩溃见 §4.1-7。
- 照片压缩后仍 >4MB：前端拦截提示。
- 封面指令执行失败（分支冲突等）：回评报错原因，不静默。
- cookie 无效：API 一律 401，页面回登录态。

## 9. 验收标准

1. `npm run build` 成功、`npx astro check` 无类型错误；24 个前台路由产物仍为纯静态 HTML。
2. 未登录访问 `/admin` 与 `/api/*` 被拦截；错误密码无法登录。
3. 投递一条真实文章链接 → 数分钟内生成 PR，条目字段过 schema 校验，Vercel 预览构建绿。
4. 投递时手动指定类型 → 以指定为准；投一条音频采访链接（自动判断）→ 归 `interview` 而非 `video`。
5. 投递与某 open PR 重复的 URL → 标注「在 PR #N 待审」，不生成重复条目。
6. 投递一条坏链接 → 进入 PR 失败清单，不影响同批其他条目。
7. 上传照片 → PR 含压缩后图片与 gallery 条目，三语图注齐全。
8. 模拟管线失败（无效 LLM key）→ `/admin` 最近投递区显示失败，分支上素材未丢。
9. 投递两条视频链接 → PR 汇总评论统一编号贴出 8 张候选；评论「封面 3」→ 正确条目获得封面；评论「换一批」→ 未选定项重截。
10. 无权限账号评论封面指令 → Action 不响应。
