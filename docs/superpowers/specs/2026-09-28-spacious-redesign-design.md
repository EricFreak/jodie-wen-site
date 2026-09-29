# 全站「大气化」改版（容器放宽 + Hero 升级 + 页底联系带）—— 设计规格

日期：2026-09-28
状态：已获用户批准（2026-09-28，用户确认首页设计稿并要求二级页面一起调整、风格统一）

## 1. 背景与目标

用户反馈整站「布局太紧凑、不够大气」，并提供 barinkayaoglu.com 作为参考。经对比分析，问题集中在布局尺度而非视觉风格：正文容器 `max-w-3xl`（768px）比导航还窄、版块间距仅 56px、Hero 只是内嵌小版块、页脚单薄。本次改版在**保留品牌资产**（深青 `#0F766E`、Georgia/Songti 衬线标题、系统字体、零客户端 JS）的前提下，全站 8 页 × 3 语统一调整空间尺度，并在每页底部新增「Get in Touch」联系带。

高保真设计稿：`docs/prototypes/spacious-home/`（`index.html` + `styles.css` + 桌面/移动截图），已获用户确认。设计稿中的 CSS 数值为实施的唯一尺度依据。

**非目标**（本次明确不做）：

- 不改信息架构、路由、导航标签、内容模型（collections schema 不动）
- 不引入任何客户端 JS、不引入新依赖
- 不改配色体系与字体栈（联系带的深色 `#115e59` 为 teal-800，属品牌色延伸）
- 不做暗色模式、不加动画特效（仅保留现有 hover 过渡）
- barinkayaoglu.com 只借鉴空间尺度，不借鉴其模板样式

## 2. 决策记录（来自与用户的确认）

| 问题 | 结论 |
| --- | --- |
| 调整范围 | 全部 8 页 × 3 语一起调整，与首页风格统一 |
| Hero 文案 | 去掉 "She is the"，改名词短语开头（`hero.bio` 已同步改 `src/i18n/ui.ts`） |
| Hero 构图 | 左文右图（英文 F 型动线，姓名先被看到），不按参考站的左图右文 |
| 联系带颜色 | 深青 teal-800（`#115e59`）通栏，白字 |
| 联系带适用范围 | 全站每页底部统一出现（2026-09-28 追加表单后含 `/contact` 页；见 §7 附录） |
| 页脚 | 深色（neutral-900）、居中：logo + 导航链接行 + 版权 |

## 3. 设计令牌（以设计稿 `styles.css` 为准）

| 令牌 | 值 | Tailwind 对应 |
| --- | --- | --- |
| 内容容器 | 1152px，左右 padding 24px | `max-w-6xl px-6`（导航与正文统一） |
| 版块纵向间距 | 96–104px（移动端 64px） | `py-24`（`md:py-24 py-16`） |
| 版块标题 | 衬线 40px bold，下边距 48px（移动端 30px / 32px） | `text-4xl` / `mb-12`（`md:text-4xl text-3xl`） |
| 标题下装饰线 | 56×3px 深青 | `h-[3px] w-14 bg-accent` |
| Hero | 浅灰底带（neutral-50）通栏，上下 96px，姓名 64px 衬线，肖像最大 420px | `py-24`、`md:text-[64px]` |
| 全宽色带 | neutral-50 背景 + 上下 1px neutral-200 边线 | `bg-neutral-50 border-y border-neutral-200` |
| 圆角系统 | 统一 8px（卡片、按钮、图片） | `rounded-lg` |
| 正文长文限宽 | 保持 72ch（`.measure` 不变） | 只作用于散文段落，不作用于页面外框 |

## 4. 结构改动

### 4.1 BaseLayout 全宽化

`main` 不再承担宽度约束（去掉 `max-w-3xl px-4`），改为全宽 `flex-1`；各页面/组件内部用 `mx-auto max-w-6xl px-6` 容器包裹内容。这样 Hero、Activities 色带、联系带可以全宽通栏。`body` 加 `overflow-x-clip` 防横向滚动条。

### 4.2 Hero（首页）

`Hero.astro` 重写为通栏版块：外层 `bg-neutral-50 border-b border-neutral-200`，内层容器 grid 两列（左 1.25fr 文 / 右 1fr 图，移动端单列、图在上），依次为：kicker（深青 15px semibold）→ 姓名（衬线 64px）→ tagline（20px，限宽 30ch）→ bio（16px，`.measure`）→ 资历徽章（白底带边框小 pill，4 枚）→ CTA 行（The Book 实心 + Get in Touch 描边 + 社媒圆点图标）。肖像带柔和投影。阿语 RTL 用逻辑属性自动翻转（左文右图变为右文左图）。

### 4.3 联系带 ContactBand（新组件）

`src/components/ContactBand.astro`，放在 BaseLayout 中 `</main>` 之后、Footer 之前；Contact 页通过 prop 关闭。内容居中：`contactband.title`（衬线 44px 白）→ `contactband.subtitle`（白 78%）→ 白色邮箱按钮（mailto，深青文字）→ 四个社媒圆点（半透明白边框，点击进本站 Social 页，与 Footer 现有行为一致）→ 单位地址小字（复用 `contact.affiliation.value`，白 55%）。`src/i18n/ui.ts` 新增三语词条 `contactband.title` / `contactband.subtitle`（阿语为 AI 翻译待校对）。

### 4.4 Footer

深色 `bg-neutral-900 text-neutral-400`，居中纵向排列：logo-mark（40px 高）→ 导航链接行（与主导航同 8 项，13.5px，hover 变白）→ 社媒圆点（沿用现有样式改深底适配）→ 版权行。上下 padding 56px。

### 4.5 首页各版块

- 各 section 由 `mt-14` 节奏改为 `py-24`（移动端 `py-16`）各自撑开，SectionHeader `mb-12`
- The Book：书封放大到 340px 高带投影，grid 两列（移动端单列），最大限宽 900px
- Latest Publications：行距加大（条目 `py-7`，标题 19px semibold，顶部分隔线）
- In the Media：三列网格 `gap-8`，封面 16:9，hover 轻微放大（纯 CSS transition，保留现有零 JS）
- Activities：整个版块（含标题与轮播）包进全宽 neutral-50 色带；轮播组件本体逻辑不动，仅间距适配
- More about Jodie：照片墙容器随 max-w-6xl 放宽，4 列（移动端 2 列）

### 4.6 二级页面

| 页面 | 调整 |
| --- | --- |
| About | 内容包进 `max-w-6xl` 容器；散文部分保持 `.measure`；TimelineItem 条目间距随新尺度放大 |
| Book | 与首页 Book 版块同构：书封 340px + 右侧文字 grid（移动端单列） |
| Publications | 列表行距与首页 `pub-item` 一致（`py-7`、标题 19px）；年份分组标题放大 |
| Media | `MediaBrowser` 卡片间距、筛选标签间距适配宽容器；视频横向卡片保持左封面右简介 |
| Activities | `ActivityList` 条目间距放大 |
| Social | 平台卡片网格在宽容器下 `lg:grid-cols-3`；卡片 padding 加大 |
| Contact | 页头风格统一；页面底部不再出现联系带（BaseLayout prop 关闭） |

## 5. 多语言与 RTL

- 所有新增 UI 字符串进 `src/i18n/ui.ts` 三语字典；阿语为 AI 翻译待用户校对（与既有约定一致）
- 方向相关样式一律 Tailwind 逻辑属性（`ms-/me-/ps-/pe-/start-/end-`），不用物理方向类
- Hero 在 RTL 下自然镜像（grid 列顺序不变，由 dir 决定排布）

## 6. 验证

1. `npm run build` 成功、`npx astro check` 无类型错误
2. 浏览器走查 24 路由中代表性页面：首页（en/zh/ar）、Publications、Media、About、Contact，桌面 1280px + 移动 375px 截图核对
3. 阿语首页 RTL 下 Hero 镜像正确、联系带与页脚不错位
4. 联系带在 Contact 页不出现、其余页面均出现
5. 外链仍可 `target="_blank" rel="noopener"`；零客户端 JS 未被破坏

## 7. 附录：联系带改为表单（2026-09-28 追加，用户已确认）

用户参照 barinkayaoglu.com 页底「Get In Touch」（Name / Email Address / Message + Send Message 表单）要求联系带改为同样的表单实现，推翻原规格「不做联系表单」的非目标约定。

- `ContactBand` 内嵌纯 HTML 表单（零 JS），`POST` 到 `https://formsubmit.co/wangkejay88@gmail.com`，由 FormSubmit 转发邮件到该邮箱（转发目标变更记录：jodiewen@tsinghua.edu.cn 收不到激活邮件 → 2026-09-29 改 15110183152@126.com，灰名单延迟严重 → 同日改 wangkejay88@gmail.com 测试；页面公开展示邮箱始终为 jodiewen@tsinghua.edu.cn）；`_template=table`、`_honey` 蜜罐防垃圾、`_subject` 按 locale 取三语词条
- **首次提交后 FormSubmit 会向 jodiewen@tsinghua.edu.cn 发一封激活确认邮件，需她点击确认一次**，之后表单才正式转发（上线后需提醒她处理）
- 表单词条三语进 `ui.ts`（`contactband.form.*`，阿语 AI 翻译待校对）；提交后跳回站内三语感谢页 `/thanks`（`_next` 指向生产域名 `https://jodiewen.com`，2026-09-28 用户确认）
- mailto 邮箱按钮降级为表单下方的文字链接（备用通道），社媒圆点与单位行保留
- 联系带改为**全站所有页面**显示（含 `/contact`），`BaseLayout` 的 `showContactBand` prop 随之移除
