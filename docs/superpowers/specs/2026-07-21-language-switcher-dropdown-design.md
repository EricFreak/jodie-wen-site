# 语言切换器下拉化 — 设计规格

- 日期：2026-07-21
- 状态：设计已获用户批准（触发器形式、`<details>` 机制、移动端保持平铺均已逐项确认）
- 项目：`/Users/eric/kimi-projects/jodie-wen-site`（Astro 5 + Tailwind v4 静态站，三语 en/zh/ar）

## 1. 目标

桌面端导航的语言切换由平铺三链接（EN 中文 العربية）改为下拉选择，视觉更紧凑；移动端保持平铺不变。

## 2. 已确认的决策

| 决策点 | 结论 |
|---|---|
| 触发器 | 当前语言名 + ▾ 三角（展开时旋转 180°） |
| 面板内容 | 只列另外两个语言（当前语言已在触发器显示，不重复列出） |
| 实现机制 | 原生 `<details>/<summary>`，零客户端 JS |
| 点击外部关闭 | summary 在 `group-open` 时生成 `fixed inset-0` 透明幕布（纯 CSS） |
| 移动端（<md） | 保持现有平铺三链接（汉堡菜单内一键直达） |

## 3. 设计

仅改 `src/components/Nav.astro`，把现有语言 `<li>` 拆为两个：

- 桌面 `<li class="relative hidden md:block">`：
  - `<details class="group">` + `<summary>`（`list-none`、隐藏 `::-webkit-details-marker`）：`{langNames[locale]}` + ▾（`transition-transform group-open:rotate-180`）
  - 面板 `<ul>`：`absolute end-0 top-full z-20 mt-1 min-w-28 rounded-md border border-neutral-200 bg-white py-1 shadow-md`；每个目标语言一行链接（`block px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 hover:text-accent`），href 仍为 `localizePath(neutralPath, loc)`
  - 幕布：summary 加 `group-open:before:fixed group-open:before:inset-0 group-open:before:z-10 group-open:before:cursor-default group-open:before:content-['']`；面板 z-20 高于幕布
- 移动 `<li class="flex items-center gap-3 md:hidden">`：现有平铺渲染原样保留

## 4. 约束与边界

- 零客户端 JS（details 原生行为；summary 原生键盘可达）
- RTL：`end-0` 逻辑定位自动镜像；无 `rtl:` 变体、无 `[dir="rtl"]` CSS
- 三语字典、utils、路由均不动；23 条内容条目不受影响

## 5. 验证

1. `npm run build` + `npx astro check` 0 错误
2. dist 断言：24 页每页仍含两个目标语言 href（沿用既有切换断言脚本）
3. Playwright 截图：桌面 `/about` 下拉展开态；`/ar/about` 下拉展开（RTL 镜像、面板不溢出）；移动端 375px 汉堡菜单内三链接平铺无回归

## 6. 非目标（YAGNI）

- 不做 globe 图标、不做语言自动探测、不加键盘方向键导航增强
- 移动端不做下拉（保持平铺）
