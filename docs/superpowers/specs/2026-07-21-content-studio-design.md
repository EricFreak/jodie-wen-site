# 内容上传工具（/studio 聊天录入）— 设计规格

- 日期：2026-07-21
- 状态：**设计已呈现，待用户最终确认**（用户 2026-07-21 暂停，约定 07-22 继续；下述决策点均已逐项获用户选择确认，仅整体批准未做）
- 项目：`/Users/eric/kimi-projects/jodie-wen-site`（Astro 5 + Tailwind v4，三语静态站，Vercel 部署）

## 1. 目标

用户（非技术）在手机上把一条链接粘贴进聊天框，AI 解析链接并按现有 UI 生成内容条目（发表/媒体/活动），预览确认后自动提交上线。免除手写 frontmatter 的负担。

## 2. 已确认的决策（逐项经用户选择）

| 决策点 | 结论 |
|---|---|
| 使用场景 | 手机端可操作 |
| 形态 | 站内工具页 `/studio` + Vercel 云函数（不用 GitHub Actions 表单） |
| 交互 | 聊天式气泡界面，可对话修正；**零客户端 JS 红线仅此页豁免**，公众页面保持零 JS |
| LLM | Moonshot/Kimi API（OpenAI 兼容接口，key 由用户创建后配 Vercel env） |
| 预览 | 确认前按现有卡片样式渲染预览，满意才提交 |

## 3. 架构

### 3.1 渲染模式

- `astro.config.mjs`：`output: 'static'` → `'hybrid'` + `@astrojs/vercel` adapter
- 24 个公众页面仍全部静态预渲染（构建产物不变）；仅 `/api/*` 两个端点走 serverless function

### 3.2 新增文件

- `src/pages/studio.astro`：工具页，静态预渲染；`noindex,nofollow`；不进导航；内联聊天脚本
- `src/pages/api/parse.ts`（POST）：口令校验 → 抓取链接（YouTube oEmbed / B站 API / OG 标签 / GBK 编码处理）→ Kimi API 生成结构化条目（titleEn/titleZh/type/outlet/date/platform/embedUrl）→ zod 校验（复用 `content.config.ts` schema）→ 返回 `{ entry, previewHtml }`
- `src/pages/api/commit.ts`（POST）：口令校验 → 最终字段 zod 校验 → GitHub Contents API 写 `src/content/<collection>/YYYY-slug.md` 提交到 main → Vercel 检测到 push 自动重新部署（约 1 分钟生效）

### 3.3 聊天流程

1. 打开 `/studio` 输口令（sessionStorage 记忆）
2. 粘贴链接发送 → 聊天流返回预览卡片（复用现有 PublicationList/MediaCard 的样式类）
3. 不满意 → 对话修正（修正指令 + 当前 entry 回传 parse 端点重生成）；满意 → 「确认上线」
4. commit 端点提交，聊天流返回成功提示与线上生效说明

### 3.4 安全

- 三个 Vercel 环境变量（用户手动配置）：`MOONSHOT_API_KEY`、`STUDIO_PASSCODE`（口令）、`GITHUB_TOKEN`（fine-grained PAT，仅本仓库 Contents:write）
- 两个 API 端点统一校验口令，失败 401

## 4. 验证

1. 本地 `astro dev` 调通 parse/commit（commit 先指向测试分支验证后改回 main）
2. 构建回归：`npm run build` + `npx astro check` 0 错误，24 路由与现在一致
3. 上线后用一条真实链接走完整流程（新增 → 线上可见 → 删除测试条目）

## 5. 非目标（YAGNI）

- 只做新增，不做条目的修改/删除
- 只接受链接，不收文件上传
- 聊天历史不持久化
- 不做多用户/账号系统（单口令）
