---
name: aigoal-landing
description: AIGOAL 落地页做法：照 AIGOAL 的文案模板写字，用量好的排版出 HTML，换成你自己的品牌色，再放进 app.aigoal.ai。按 category 分：lead-magnet（免费领取电子书 / 指南 / 清单，Opt-in + Thank you 两页）和 webinar（免费讲座 / 线上课 / 几天的活动，报名 + VIP 升级 + 登记成功三页）。做落地页、领取页、lead magnet 页、opt-in、thank you 页、报名页、webinar 报名页时用。
---

# AIGOAL 落地页 · Landing page skill

一次出一组页：lead magnet 两页，webinar 三页。文案照 AIGOAL 的模板一块一块填，排版用量好的模板，只换字、图片和品牌色。

## 适合所有行业

一样的结构，换掉的只是「送什么」「办什么」「谁出面」：

| 行业 | lead magnet 可以送 | webinar / 活动可以是 | 「关于我们」放谁 |
|---|---|---|---|
| 卖产品（零售、电商、餐饮） | 选购清单、使用教学、食谱、试用券 | 新品发布 Live、试吃 / 试用会 | 创办人或店主 |
| 本地服务（美容、养生、健身、汽车） | 保养清单、前后对比指南、体验券 | 免费体验日、线上分享会 | 店主、主理人、技师 |
| 专业服务（房产、保险、融资、会计、律师） | 计算表、文件清单、市场报告 | 说明会、看房会、线上讲座 | 顾问本人 |
| 课程 / 教练 | 电子书、小测验、迷你课 | 免费讲座、几天的线上营 | 讲师 |

「关于我们」那一块写的是**为什么该信你**：卖产品就写品牌故事和真的销量 / 好评，做服务就写年资和真客人的结果。

## 0. 先选 category

| category | 用在哪 | 出几页 |
|---|---|---|
| **lead-magnet** | 免费领取一样东西（电子书、指南、清单），换名字 + WhatsApp + Email | **Opt-in 页**（填资料）+ **Thank you 页**（领取成功，下一步） |
| **webinar** | 免费讲座、线上课、几天的活动，报名后可以卖 VIP 升级 | **报名页** → **VIP 升级页**（没有 VIP 可以卖就跳过）→ **登记成功页** |

模板在 `templates/lead-magnet/` 和 `templates/webinar/`。

## 1. 做一组页的步骤

1. **先问品牌**（第一次做才问，之后照用）：品牌 / 公司名、负责人名字（老板 / 讲师 / 顾问 / 店主）、logo、**一个主色**（给色号最好，没有就说「深蓝」「墨绿」这样），照 `references/design.md` 第 1 节换好 `:root` 的颜色。
2. **问清楚内容**（缺了就问，不要自己编）：
   - Lead magnet 叫什么、里面有什么（照封面 / 目录写，不要加没有的内容）
   - 给谁：目标人群 + 他最痛的 3 件事
   - 封面图、负责人照片（一定用真的；AI 图只能当背景装饰）
   - 领取后他会收到什么、从哪里收到（WhatsApp / Email / 下载链接）
   - Thank you 页的下一步：加 Community？报名讲座？（链接要真的）
   - **webinar 另外要问**：活动日期、每天时间、线上还是现场（Zoom / 地点）；每一天真的会讲什么；有没有 VIP（价钱、每样特权和真的定价、要不要收 SST、付款链接）；WhatsApp 社群链接。
3. **写文案**：lead magnet 照 `references/copy-lead-magnet.md`，webinar 照 `references/copy-webinar.md`，一块一块填。数字、见证、头衔只用真的，没有就留【待补】。
4. **出 HTML**：复制模板到新文件夹，只改【】里的字、图片和 `:root` 最上面的品牌色。**其他 CSS 不要动**（排版数字在 `references/design.md`）。
5. **先出手机首屏截图给用户看**（390 宽），点头才写完整页。改字也是先截图看。
6. **自己检查**（第 4 节清单）。
7. **放进 app.aigoal.ai**：照 `references/aigoal-import.md`。上线前用手机真的填一次表，确认资料进 CRM、Thank you 页有出来。

## 2. 文案铁律

- **首屏只放 4 样**：顶条一句戳痛 → 小标（多久 / 什么）→ 大字结果（短语，手机一行最多 6 个字）→ 一句点名「尤其是…的你」+ 一个按钮。
- **按钮全页同一句**（例：「立即免费领取」），不要每个按钮换字。
- **封面不放答案**：讲后果 + 悬念，答案在 lead magnet 里面。
- **痛点 3 个**：标题讲后果，内文讲画面，最后一句「不是你不够努力，是…」把人带到解决方法。
- **之前 / 之后**：一条对一条，灰色是过去，品牌色是之后。
- **关于我们**（讲师 / 老板 / 团队）：回答 4 题：你是谁、做了多久、突出成绩、现在怎么帮他得到一样的结果。
- 马来西亚华人口语、白话，不要 AI 腔（「赋能」「助力」「深度解析」这类不用）。
- **免费东西也要讲价值**：lead magnet 写「免费领取」；**原价只能写真的价钱**，没有就不写原价。

## 3. 设计铁律

全部数字在 `references/design.md`。最常被忘记的：
- 一种中文字体 **Noto Sans SC**（数字可以用 Inter），标题 900 粗。
- 大标题：手机 55px / 电脑 80px；首屏大字：手机 72px / 电脑 120px。
- 内文 16–17px，行高 1.75–1.8；小字 14px。
- 按钮：药丸形（999px 圆角），高 56px，17px 700，字距 .04em。
- 每一块上下 64px（手机）/ 96px（电脑），内容最宽 1180px，两边 20px。
- 底部固定报名条，手机电脑都在，body 底部留 124px。
- **颜色只改 `:root` 最上面的品牌色那几行**，不要在别的地方加新颜色。
- **中文标题按短语包 `<span class="g">…</span>`**（inline-block），换行才会落在短语之间；标点跟着前一个短语。首屏大字每个 `.g` 手机最多 4–5 个字。

## 4. 交件前检查

- [ ] 390 宽手机：没有横向卷动，大字没有一个字掉到下一行
- [ ] 首屏 4 样 + 1 个按钮，按钮在第一屏看得到
- [ ] 全页按钮同一句，点了都跳到表单
- [ ] 表单 3 栏：称呼、WhatsApp 号码（必填）、Email（选填）
- [ ] 没有 `<script>`（平台会剥掉）；没有编出来的数字 / 见证 / 原价
- [ ] Thank you 页：大大的「领取成功」+ 3 步下一步 + 真的链接
- [ ] 图片都是真的、有 alt，负责人的脸没有被字盖住
- [ ] 品牌色换好了：主色按钮上的白字看得清楚，首屏大字在主色卡上看得清楚
- [ ] webinar：日期 / 时间 / 方式在首屏、表单旁边、底部固定条三处都一样；议程跟用户对过
- [ ] webinar VIP 页：每样价值加起来等于总价值；有「不用了」链接去登记成功页；付款链接是真的

## 5. 档案

```
aigoal-landing/
  SKILL.md                         ← 这份
  references/copy-lead-magnet.md   ← lead magnet 文案 8 块 + Thank you 页，每块怎么填 + 范例句
  references/copy-webinar.md       ← webinar 3 页每块怎么填 + 范例句
  references/design.md             ← 品牌色怎么换 + 量好的字体大小、间距
  references/aigoal-import.md      ← 放进 app.aigoal.ai 的规矩
  templates/lead-magnet/optin.html ← 空白模板（改【】就好）
  templates/lead-magnet/thanks.html
  templates/webinar/optin.html     ← 报名页（多了活动资料、适合对象、议程、FAQ）
  templates/webinar/vip.html       ← VIP 升级页（进度条、价钱、特权清单、「不用了」链接）
  templates/webinar/thanks.html    ← 登记成功页（加社群、记日历、当天准备）
```

本机预览：`python3 -m http.server 8978 --directory <你的输出文件夹>`，打开 `http://localhost:8978/optin.html`，浏览器调成手机宽度看。
