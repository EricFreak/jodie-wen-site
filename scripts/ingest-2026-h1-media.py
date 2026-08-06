#!/usr/bin/env python3
"""一次性脚本：将 materials docx 解析结果落盘 + 生成网站 collection 条目。
数据源：materials/20260805 26上半年采访.docx（27 条，人工转录为本脚本数据）。
已去重：The Point 3/30、中新网 3/3、澎湃 5/7、FT中文网 6/28、Global Watch 3/1（见 pending-assets.md）。
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (date, outlet, outletZh, url, titleEn, titleZh, kind, summary)
# kind: video / interview / article(署名文章→publications)
E = [
    # ---------- 视频/音频 ----------
    ("2026-03-01", "CGTN", "CGTN", "https://www.cgtn.com/tv/replay?id=CcdbJIA",
     "CGTN Global Watch interview: the situation after Khamenei's death",
     "CGTN Global Watch 采访：哈梅内伊之死后的伊朗政局", "video",
     "文晶3月1日接受CGTN采访时指出，哈梅内伊之死确实对伊朗国内局势产生了重大影响，但伊朗政治架构并非单极——总统作为国家元首，在国内治理和外交事务中同样扮演着关键角色。此外，革命体系内的其他重要人物也将在后续阶段发挥重要作用，各方力量共同决定着伊朗未来的走向。"),
    ("2026-03-30", "CGTN", "CGTN", "https://www.cgtn.com/tv/replay?id=CdHIfAA",
     "The Point with Liu Xin: Middle East tensions and the US-Israel-Iran war",
     "CGTN《欣视点》：解读中东局势与美以伊战争动向", "video",
     "文晶3月30日接受CGTN采访时认为，美伊冲突不会有真正的赢家。美国的主要目标是推动伊朗政权更迭、摧毁其核设施和导弹能力，但截至目前，伊朗政治依然稳定，核设施仅约三分之一受损，导弹力量也未遭根本性打击，美国并未达成预期目标。"),
    ("2026-03-30", "CGTN Radio", "CGTN 广播", "https://radio.cgtn.com/podcast/news/1/Whats-the-key-to-peaceful-development-of-cross-Strait-ties/600624",
     "CGTN radio interview: four weeks into the US-Iran war",
     "CGTN 广播采访：美伊战争进入第四周", "video",
     "3月30日，清华大学CISS研究员文晶在接受CGTN采访时提出：战争已持续四周多，美伊双方都面临压力，均有达成协议的意愿；巴基斯坦、土耳其、埃及、沙特四国外长会议具有意义；美国提出的15点停火建议难以被伊朗接受；伊朗有能力控制霍尔木兹海峡，商业航运面临较高安全风险；以色列倾向于让冲突持续更久。"),
    ("2026-04-10", "CGTN", "CGTN", "https://www.cgtn.com/tv/replay?id=CdacbEA",
     "CGTN interview: US-Iran divisions over reparations and strait control",
     "CGTN 采访：美伊在战争赔偿与海峡控制权上的分歧", "video",
     "4月10日，文晶在接受CGTN采访时提出，美伊分歧巨大，伊朗要求战争赔偿且不放弃对海峡的控制，美国难以接受；以色列试图通过黎巴嫩问题在美伊之间施加杠杆；战争已使全球能源和经济受到严重影响，美国将尽力推动海峡重新开放。"),
    ("2026-04-14", "CGTN", "CGTN", "https://www.cgtn.com/tv/replay?id=CdcABAA",
     "CGTN interview: Abu Dhabi crown prince's China visit signals Gulf recalibration",
     "CGTN 采访：阿布扎比王储访华释放海湾转向信号", "video",
     "4月14日，文晶在接受CGTN采访时提出，阿布扎比王储此次访问“意义重大”，冲突进一步削弱了海湾国家对美国的信心，促使它们扩大与中国的合作；中国的外交被形容为“安静、低调但务实”，在伙伴请求支持时采取行动。"),
    ("2026-04-25", "CGTN", "CGTN", "https://www.cgtn.com/tv/replay?id=CdfAJIA",
     "CGTN interview: US-Iran conflict shifts to a contest of wills",
     "CGTN 采访：美伊冲突转向意志之争", "video",
     "4月25，文晶在接受CGTN采访时提出：战争已从全面轰炸转向意志之争，双方都不愿回到暴力冲突；伊朗排除直接谈判是外交信号，意在利用霍尔木兹海峡作为筹码；美国部署三艘航母主要是威慑；海峡僵局持续时间越长，对全球经济影响越严重。"),
    # ---------- 文字采访 ----------
    ("2026-02-28", "South China Morning Post", "南华早报", "https://www.scmp.com/news/world/article/3344963/israel-launches-preemptive-strike-against-iran-saying-it-seeks-remove-threats",
     "Israel launches preemptive strike against Iran, saying it seeks to remove threats",
     "以色列对伊朗发动先发制人打击（南华早报采访）", "interview",
     "文晶2月28日接受南华早报采访指出，周六的袭击是一场直接战争，涉及中东两大地区强国伊朗和以色列，以及域外大国美国。战争已经开启，对中国在伊朗及整个中东地区的利益而言，这将是一个重大变局。"),
    ("2026-03-09", "Berlingske", "贝林时报", "https://www.berlingske.dk/internationalt/de-har-regnet-ham-ud-i-beijing-trumps-krig-er-ikke-genial--den-er-banal",
     "Trump's Middle East war is not genius — it is banal (Berlingske interview)",
     "贝林时报采访：特朗普的中东行动并非“四维象棋”式大战略", "interview",
     "文晶3月9日接受贝林时报采访指出，外界将特朗普的外交政策解读为针对中国的“四维象棋”式大战略，是一种过度复杂化的误解。特朗普在中东的行动动机更为直接和传统——即让中东重回美国的完全控制之下。"),
    ("2026-03-10", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3346134/why-china-sees-stability-hardliner-mojtaba-khameneis-rise-lead-iran",
     "Why China sees stability in hardliner Mojtaba Khamenei's rise to lead Iran",
     "中国为何认为强硬派穆杰塔巴·哈梅内伊继位有利于稳定（南华早报采访）", "interview",
     "文晶3月10日接受南华早报采访指出，由于伊朗地位削弱，哈梅内伊（或新最高领袖）可能被迫将重点转向国内事务，并对西方采取温和立场。战争形势已经改变，伊朗领导的“抵抗轴心”整体实力有所下降。"),
    ("2026-03-12", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3346263/why-war-iran-not-trumps-end-will-israel-fan-flames?display=plus",
     "Why war with Iran is not Trump's endgame; will Israel fan the flames?",
     "为何对伊战争不是特朗普的终局；以色列会火上浇油吗（南华早报采访）", "interview",
     "文晶3月12日接受南华早报采访指出，除非美伊立即重返谈判桌并达成协议，否则冲突至少还将持续两周。高强度冲突难以长期维持，美国原本预期速胜，但伊朗的报复可能超出特朗普预期。"),
    ("2026-03-24", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3347742/are-efforts-broker-peace-deal-between-iran-and-us-doomed-fail?display=plus",
     "Are efforts to broker a peace deal between Iran and US doomed to fail?",
     "斡旋美伊和平协议的努力注定失败吗（南华早报采访）", "interview",
     "文晶3月24日接受南华早报采访指出，美伊即使愿意谈判，结果也很大程度上取决于双方的核心诉求——伊朗的要求对美国而言毫无商量余地，反之伊朗也不可能满足美方关于恢复霍尔木兹海峡自由航行等要求。"),
    ("2026-03-27", "China Review News", "中评社", "https://gb.crntt.com/doc/1071/8/0/4/107180436.html?coluid=7&kindid=0&docid=107180436",
     "US-Iran deadlock: energy crisis hits the AI industry (CRNTT interview)",
     "美伊僵局难破 文晶：能源危机冲击AI产业（中评社采访）", "interview",
     "文晶3月27日接受中评社采访时指出，美伊虽仍有对话意愿，但僵局根源在于双方要价彼此难以接受。美以动武的三大诉求是打击伊核设施、推动伊朗政权更迭及遏制“什叶派之弧”；美以利益出发点存在差异。海湾国家偏好地区平衡，令局势更趋复杂。"),
    ("2026-03-28", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3348265/1-month-2-straits-more-strikes-how-long-will-us-israeli-war-iran-last?display=plus",
     "1 month, 2 straits, more strikes: how long will the US-Israeli war on Iran last?",
     "一个月、两条海峡、更多空袭：美以对伊战争还会持续多久（南华早报采访）", "interview",
     "文晶3月28日接受南华早报采访表示，美伊冲突预计将持续约六周。特朗普虽有权指挥军队，但无权宣战；根据联邦法律，总统启动军事行动后须在48小时内通知国会，若未获批准，军队部署不得超过60天，因此60天是关键门槛。"),
    ("2026-04-01", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3348700/what-does-china-pakistan-plan-iran-crisis-mean-post-war-order",
     "What does the China-Pakistan plan for the Iran crisis mean for the post-war order?",
     "中巴伊朗危机方案对战后秩序意味着什么（南华早报采访）", "interview",
     "4月1日，文晶在《南华早报》采访时提出，海湾国家正寻求中国和巴基斯坦等外部力量来平衡地区局势，中国有能力且可信，但不会军事介入，而是通过外交、政治和道德层面发挥作用。"),
    ("2026-04-02", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3348571/china-pledges-strategic-coordination-pakistan-help-end-us-war-iran",
     "China pledges strategic coordination with Pakistan to help end the US war on Iran",
     "中国承诺与巴基斯坦战略协调以助力结束美伊战争（南华早报采访）", "interview",
     "4月2日，文晶就中巴联合五点计划及美伊战争接受《南华早报》采访时提出，海湾国家因依赖美国安全保障而感到脆弱；中国作为外部大国越来越被视为必要力量，伊朗不信任美国、巴基斯坦分量不足，因此需要一个大国来扮演保证人角色。"),
    ("2026-04-09", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3349534/strait-hormuz-closed-again-end-iran-us-ceasefire",
     "Strait of Hormuz closed again: end of the Iran-US ceasefire?",
     "霍尔木兹海峡再度关闭：美伊停火终结？（南华早报采访）", "interview",
     "4月9日，文晶在接受《南华早报》采访时提出，美伊谈判虽会充满曲折但不太可能滑向全面战争，双方存在共同利益；而以色列是主要变数，美国副总统万斯或能影响特朗普的对以决策。"),
    ("2026-04-15", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3350081/xi-jinpings-meeting-abu-dhabi-crown-prince-highlights-gulf-turn-towards-china",
     "Xi Jinping's meeting with Abu Dhabi crown prince highlights Gulf turn towards China",
     "习近平会见阿布扎比王储凸显海湾转向中国（南华早报采访）", "interview",
     "4月15日，文晶在《南华早报》采访时提出，此次访问“意义重大”，冲突进一步削弱了海湾国家对美国的信心，促使它们扩大与中国的合作；阿联酋在当前时刻派未来领导人访华并非偶然，表明其寻求更可靠的安全与经济伙伴。"),
    ("2026-04-27", "South China Morning Post", "南华早报", "https://sc.mp/w4057?utm_source=copy-link&utm_campaign=3351608&utm_medium=share_widget",
     "Iran holds the cards in the Hormuz 'cold conflict' (SCMP interview)",
     "霍尔木兹“冷冲突”中牌在伊朗手里（南华早报采访）", "interview",
     "4月27日，文晶在接受《南华早报》采访时提出，当前局势对伊朗有利，这是一场低强度的“冷冲突”，伊朗因靠近霍尔木兹海峡而能以较低成本施加影响；同时局势仍然“具有爆炸性”，僵局难以持续。"),
    ("2026-05-18", "Berlingske", "贝林时报", "https://www.berlingske.dk/internationalt/trump-har-ingen-trumf-nu-vil-xi-have-en-indroemmelse-den-vil-faa-stillehavet-til-at-skaelve",
     "Trump has no trump card: Xi seeks a concession (Berlingske interview)",
     "贝林时报采访：中美元首会晤与中美关系走向", "interview",
     "5月18日，文晶在接受贝林时报采访中指出中美关系是世界上非常重要的关系，这两个国家是世界上最大的经济体。"),
    ("2026-05-31", "Institute for Peace & Diplomacy", "加拿大和平外交研究所（IPD）", "https://peacediplomacy.org/2026/05/13/trump-meets-xi-where-u-s-china-relations-go-next-and-where-they-take-the-world/",
     "Trump meets Xi: where U.S.-China relations go next, and where they take the world",
     "文晶在加拿大和平外交研究所（IPD）就中美元首会晤发表评论", "interview",
     "5月31日文晶在加拿大和平外交研究所（IPD）就中美元首会晤发表评论，指出两国元首举行战略沟通有助于增进互信、维持双边关系总体平稳；双方围绕中东热点问题展开高层对话，对于防止冲突扩大、维护中东整体稳定具有关键作用。"),
    ("2026-06-22", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3357857/blockade-lifted-assets-be-returned-iran-swiss-talks-breakthrough?display=plus",
     "Blockade lifted, assets to be returned: Iran's Swiss talks breakthrough",
     "封锁解除、资产返还：伊朗瑞士谈判取得突破（南华早报采访）", "interview",
     "文晶6月22日接受南华早报采访认为，美方最新声明更多是一种危机管理手段，本质上是意图宣示，但这一意图至关重要。此次谈判同意建立沟通机制和工作组，是重要的进展——而这在4月首次美伊和谈中并未出现。"),
    ("2026-07-15", "South China Morning Post", "南华早报", "https://www.scmp.com/news/china/diplomacy/article/3360711/us-iran-war-trump-falling-vietnam-quagmire?display=plus",
     "US-Iran war: is Trump falling into a Vietnam-style quagmire?",
     "美伊战争：特朗普正陷入越南式泥潭吗（南华早报采访）", "interview",
     "文晶7月15日接受南华早报采访指出，美方相关言论既是向伊朗释放强硬信号，也是在11月中期选举前安抚国内选民；美国虽军事优势巨大，但不愿深陷泥潭，且至今未能将优势转化为决定性胜利。"),
    ("2026-07-25", "China Review News", "中评社", "http://hk.crntt.tw/touch/detail.jsp?coluid=92&kindid=0&docid=10721671",
     "Iran's spillover-effect tactics challenge US relative power (CRNTT interview)",
     "文晶：伊朗采用溢出效应战术挑战美国的相对实力（中评社采访）", "interview",
     "文晶7月25日接受中评社采访时指出，美伊当前是战略博弈，全面战争可能性低；伊朗采用“溢出战术”打击民用设施，意在施压美国盟友，美方已因此软化对伊立场。短期停火可行但长期和平难，低强度冲突将持续。"),
    # ---------- 署名文章（→ publications）----------
    ("2026-02-10", "China-US Focus", "中美聚焦", "https://cn.chinausfocus.com/foreign-policy/20260210/44164.html",
     "US-Iran Talks: Historical Roots, Status Quo and Prospects",
     "美伊谈判历史根源、现状和前景", "article",
     "文晶2月10日于中美聚焦发表文章。文章指出，美伊战争已持续四周多，双方均有达成协议的意愿；巴基斯坦、土耳其、埃及、沙特四国外长会具有斡旋意义。美国提出的15点停火建议难以被伊朗接受，美方采取“胡萝卜加大棒”策略。"),
    # ---------- 已收录条目的 docx 副本（仅入 materials 归档，不进 collection）----------
    ("2026-03-03", "China News Service", "中国新闻网", "https://www.chinanews.com.cn/gj/2026/03-03/10580191.shtml",
     "US-Israel strikes on Iran: acting together or dragged in?",
     "美以对伊朗动武：主动联手，还是被拖下水？", "interview",
     "文晶3月3日接受中新网采访时指出，美以对伊朗动武并非单纯“以色列把美国拖下水”，双方在战略目标上部分一致：都将伊朗视为中东威胁，担忧其60%丰度铀浓缩的核风险，并希望遏制伊朗影响力扩张。"),
    ("2026-05-07", "The Paper", "澎湃新闻", "https://www.thepaper.cn/newsDetail_forward_33105399",
     "The UAE's Exit from OPEC: Strategic Considerations",
     "阿联酋退出OPEC：为霍尔木兹海峡恢复通航提前布局？", "article",
     "文晶与樊若晨在分析中指出，阿联酋退出OPEC虽在意料之外，却在情理之中，根源在于其产能扩张与OPEC配额限制之间的长期结构性矛盾。阿联酋选择在霍尔木兹海峡受冲击之际退出，实为利用自身绕开海峡的出口优势提前进行战略布局。"),
    ("2026-06-28", "FT Chinese", "FT中文网", "https://cn.ft.com/story/001110172",
     "Summer Davos Observations: Why the Middle East Will Become an Important Arena for Global Scaled Innovation",
     "夏季达沃斯观察：为何中东将成为全球规模化创新的重要场域？", "article",
     "文晶在夏季达沃斯论坛后指出，全球竞争的本质正从地缘政治转向可持续的经济增长，而增长的引擎是创新的规模化和产业化。中东正跳出“全球地缘冲突和能源供给中心”的单一标签，成为全球规模化创新浪潮里的落地试验场。"),
]

# 与现有 collection 重复的（url 或同文转载），只入 materials 归档，不进 collection
SKIP_COLLECTION = {
    "https://www.cgtn.com/tv/replay?id=CdHIfAA",       # The Point 3/30 已收录
    "https://www.cgtn.com/tv/replay?id=CcdbJIA",       # Global Watch 3/1 与已收录条目同天同节目
    "https://www.chinanews.com.cn/gj/2026/03-03/10580191.shtml",  # 已收录
    "https://www.thepaper.cn/newsDetail_forward_33105399",        # 与 CISS 2026-05-08 条目同文
    "https://cn.ft.com/story/001110172",                          # 与 CISS 2026-07-06 条目同文
}

PLATFORM = {"CGTN": "cgtv", "CGTN Radio": "cgtv"}

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60].strip("-")

def yq(s):  # yaml double-quoted scalar
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

def main():
    n_mat = n_col = 0
    for (date, outlet, outletZh, url, titleEn, titleZh, kind, summary) in E:
        sub = "视频" if kind == "video" else "文字"
        mat_dir = os.path.join(ROOT, "materials", sub)
        os.makedirs(mat_dir, exist_ok=True)
        name = f"{date}-{slug(outlet)}-{slug(titleEn)[:40]}.md"
        mat = (
            "---\n"
            f"title: {yq(titleZh)}\n"
            f"titleEn: {yq(titleEn)}\n"
            f"outlet: {yq(outletZh)}\n"
            f"date: {date}\n"
            f"url: {yq(url)}\n"
            f"kind: {kind}\n"
            "---\n\n"
            f"{summary}\n"
        )
        with open(os.path.join(mat_dir, name), "w", encoding="utf-8") as f:
            f.write(mat)
        n_mat += 1

        if url in SKIP_COLLECTION:
            continue
        if kind == "article":
            col_dir = os.path.join(ROOT, "src", "content", "publications")
            body = (
                "---\n"
                f"titleEn: {yq(titleEn)}\n"
                f"titleZh: {yq(titleZh)}\n"
                f"outlet: {yq(outlet)}\n"
                f"date: {date}\n"
                f"url: {yq(url)}\n"
                "lang: \"zh\"\n"
                "---\n"
            )
        else:
            col_dir = os.path.join(ROOT, "src", "content", "media")
            body = (
                "---\n"
                f"titleEn: {yq(titleEn)}\n"
                f"titleZh: {yq(titleZh)}\n"
                f"type: \"{kind}\"\n"
                f"outlet: {yq(outlet)}\n"
                f"date: {date}\n"
                f"url: {yq(url)}\n"
                f"platform: \"{PLATFORM.get(outlet, 'other')}\"\n"
                "---\n"
            )
        os.makedirs(col_dir, exist_ok=True)
        with open(os.path.join(col_dir, name), "w", encoding="utf-8") as f:
            f.write(body)
        n_col += 1
    print(f"materials 归档 {n_mat} 条；新建 collection 条目 {n_col} 条")

if __name__ == "__main__":
    main()
