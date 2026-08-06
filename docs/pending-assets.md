# 待补充素材清单

> 交付时由用户补充；每条注明在网站中的位置。

说明：书籍购买链接已在实施中解决（当当购买页 + 世界知识出版社 + ISBN 9787501269600 已写入 Book 页），不在本清单。`src/content/` 三个集合中无 placeholder URL——凡未能核实链接的条目一律未收录（不虚构原则），缺口以「待补条目」形式列在下方。

## 图片

- [x] 肖像照（首页 Hero、About 页）— 已提供并接入（`public/images/portrait.jpg`，426×640/41KB；Hero 方形裁切 `object-cover object-top`，About 页 h-64 w-48 展示）2026-07-20
- [x] 《美国的中东政策研究（2009-2017）》书封图（首页、Book 页）— 已提供并接入（`public/images/book-cover.jpg`，源自白底高清 3D 渲染图，836×1200/81KB；首页 h-72、Book 页 h-96 展示，flex `items-center` 垂直居中，纯 CSS checkbox 点击放大查看（无锚点、不改变滚动位置））2026-07-20

## 链接

- [ ] 文晶Talk 本号代表文章（Social 页「文晶Talk 精选」）— 用户 2026-08-06 提供的 3 条微信链接经核实均为**第三方账号**发布的署名文章（理想国/北大人文交流基地/中国政治传播研究），已转入 publications 集合；「文晶Talk」公众号本号的代表文章链接（`mp.weixin.qq.com/s/...`）仍待提供，拿到后填入三语 `social.astro` 的 `links` 数组
- [ ] 社媒平台账号链接（Social 页 + 页脚图标）— LinkedIn（`linkedin.com/in/jodie-wen-文晶-1a2606387`）、X（`x.com/JingWenOxford`）、微博（`weibo.com/u/1969913095`）已于 2026-08-06 核实接入；视频号 / B站 / YouTube 卡片因无链接**当前隐藏**，提供链接后填入 `src/data/socials.ts` 对应平台的 `url` 字段即自动显示
- [ ] 「More about Jodie」生活照片（首页底部照片墙）— 伊朗调研、达沃斯论坛等照片待提供；照片放入 `public/images/gallery/` 并在 `src/content/gallery/` 建条目（image + captionEn/captionZh/captionAr + date 可选），无照片时首页显示空态文案（2026-08-06）
- [ ] 凤凰卫视《一虎一席谈》（2024-10-19）视频封面 — 该条目链接为 CISS 官网页面、无视频流可截帧，当前为渐变占位；提供截图后放入 `public/images/media/` 并在条目填 `cover` 字段（其余 5 条 CGTN 视频封面已于 2026-08-06 通过回放 API + ffmpeg 截帧生成）
- [ ] CGTN Global Watch 2026-03-01 回放 ID 冲突待确认 — 已收录条目用 `CcdIEAA`，用户 docx 用 `CcdbJIA`，两个链接均返回 200（SPA 无法程序判定），已保留已收录条目、跳过 docx 副本；请人工打开确认哪个是正确的 3/1 期节目（2026-08-06）
- [ ] SCMP 2026-04-09 条目 URL 经修正（docx 原文含空格断行，已按连字符补全 `strait-hormuz-closed-again-end-iran-us-ceasefire`），如打不开请提供正确链接（2026-08-06）
- [ ] 采访视频嵌入 ID（Media 页）— YouTube/B站 embed ID 未核实到（CGTN《欣视点》2026-03-30 期在 YouTube 有超过 6 万播放但视频 ID 未能确认，B站搜索被反爬）；当前全部为封面卡片/链接卡片降级、无 iframe；提供视频 ID 后填入对应 `src/content/media/*.md` 的 `embedUrl` 字段即可启用嵌入
- [ ] SCMP 已收录条目（`src/content/media/2023-scmp-blinken-saudi-arabia.md` 等 13 条）直接链接有付费墙（SCMP Plus），读者可能需要订阅才能读全文；链接本身已全部通过浏览器复验可达（2026-08-06，curl 被反爬但真实浏览器全部 200），无需移除；如有本人存档（公众号转载等）可替换为免费链接

## 内容缺口

以下条目在搜集中未能核实到可引用链接，均未收录，待用户提供线索后补录。

### 署名文章（Publications 页）

- [ ] NYT / BBC / SCMP / CGTN / 凤凰 等媒体的署名文章 — bio 佐证其为这些媒体撰稿或提供评论，但未能核实到具体文章链接（媒体站内搜索为 JS 渲染、通用搜索引擎被反爬）；当前仅收录 China-US Focus 2 条英文 + CISS 6 条中文，首页与 Media 页媒体墙保留这些机构名称

### 媒体采访（Media 页）

- [ ] NYT / BBC 具体采访条目 — bio 佐证存在，但未能核实到具体 URL
- [ ] 东方卫视美伊冲突采访 — CISS 综述（`https://ciss.tsinghua.edu.cn/info/new_communication_iqt/2000000009048`）佐证存在，但无直接可引用 URL
- [ ] 「CISS 专家就中美元首峰会接受多家媒体采访」（2026-05-15，文晶在列）— CISS 通告 `https://ciss.tsinghua.edu.cn/info/new_communication_iqt/2000000009244`，原媒体报道链接未取得
- [x] 中评社采访「美伊僵局难破：能源危机冲击AI产业」（2026-03-27）— 已通过 materials 素材补录（`src/content/media/2026-03-27-china-review-news-*.md`，2026-08-06）

### 活动（Activities 页）

- [ ] 北京香山论坛 — bio 佐证多次参加，但无日期化公开报道佐证，未收录
- [ ] 中美中东二轨对话 — 同上（bio 佐证参加，无具体场次的公开报道）
- [ ] （可选补录）战略与安全论坛第 50 期「阿富汗的现状与未来」研讨会（2022-10-12，仅列席，`https://ciss.tsinghua.edu.cn/info/new_communication_iqt/2000000005345`）；第七期/第八期及更早「中国论坛·专家媒体面对面」（栏目列表 `https://ciss.tsinghua.edu.cn/column/new_ChinaForumhdmt`）
