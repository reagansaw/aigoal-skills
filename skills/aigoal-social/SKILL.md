---
name: aigoal-social
description: 用 app.aigoal.ai 的 social API 帮用户排程发片：把做好的影片 / 照片排到 Facebook 专页、Instagram（Reels）、TikTok，一次排一整个礼拜；也能查排程、改、取消、看已发帖的观看和留言，和设定「留言关键字自动私讯」（留言 GUIDE 就私讯落地页链接）。用户说「发片」「排程」「帮我发到 FB / IG / TikTok」「这礼拜一三五晚上 8 点发」「schedule post」「自动发帖」「留言自动私讯」「comment to DM」时用。不做影片本身（用 video-reverse / video-craft），不做落地页（用 aigoal-landing）。
---

# AIGOAL 排程发片 · Social skill

把做好的片交给 app.aigoal.ai，到时间它自己发到 FB 专页、IG、TikTok。你（Claude）负责：问清楚 → 列排程给用户看 → 用户说 OK → 上传、送进排程 → 回报。

**铁律：用户没看过排程和 caption、没说 OK，就不送。** 发出去的帖收不回，只能到专页删。

脚本：`<skill>/scripts/aigoal_social.py`（`<skill>` = 这份 SKILL.md 所在的文件夹，路径有空格要加引号）。只用 Python 标准库。

## 适合所有行业

发片的节奏一样，换掉的只是 caption 最后叫人做的那件事：

| 行业 | caption 最后一句（CTA） |
|---|---|
| 卖产品（零售、电商、餐饮） | 「留言 MENU 拿这礼拜的优惠」 |
| 本地服务（美容、养生、健身、汽车） | 「留言 BOOK 拿体验价 / 预约链接」 |
| 专业服务（房产、保险、融资） | 「留言 GUIDE 领免费指南」 |
| 课程 / 教练 | 「留言 FREE 拿免费讲座名额」 |

CTA 要接得上用户的 lead magnet 或落地页（aigoal-landing 做的那一页）。

## 0. 开工前，先确认 3 样

1. **钥匙**：请用户到 app.aigoal.ai →「整合中心」→「API 钥匙」→ 复制**整段**，贴给你。整段长这样：`BASE=…`、`TOKEN=…`、`TENANT=…` 几行。
   - 把整段原样存进 scratchpad 的一个暂存档（例如 `key.txt`），跑脚本时用 `--token-file key.txt`。脚本会自己读 TOKEN 和 TENANT，两个都带（TENANT 没带会打到别的户口或被拒）。
   - **不要写进 skill、README、posts.json、git，也不要印出来。**
   - 大约 1 小时过期。脚本回「钥匙过期」，就请用户回整合中心按「换一把新的」，再贴一次整段。
   - 不要自己去电脑里翻钥匙，只用用户贴给你的。
2. **专页连好了没有**：跑 `pages`。
   ```bash
   python3 "<skill>/scripts/aigoal_social.py" --token-file key.txt pages
   ```
   - 没有专页 → 请用户到「整合中心 → Facebook & Instagram」连 FB 专页。IG 要是专业账号，而且接在那个 FB 专页下面。
   - 显示「要重连」→ 以前连过、但没有发帖权限：请用户重连一次，授权页上「管理贴文 / 发布内容」要打勾。
   - TikTok 显示「没连」或「要重连」→ 整合中心 → TikTok 连一次（要给发帖权限）。
3. **Social Media 功能开了没有**：回 403 / 404 多半是这个户口还没开 Social Media，或用户不是管理层。请他问 AIGOAL 顾问，不要自己绕。

## 1. 问清楚（缺了就问，不要自己编）

1. **哪几支片 / 哪几张图**：本机档案路径。看一下长度和画幅（`ffprobe`），竖屏 9:16 最好。
2. **发去哪里**：FB、IG、TikTok 哪几个；连了不只一个专页就问哪一个。
3. **几时发**：哪几天、几点（马来西亚时间）。用户说「你看着办」就建议晚上 8–9 点、一个礼拜 3 支，并讲出来。
4. **caption 怎么写**：照片的内容写；问 CTA 是什么（留言关键字？链接？），链接要真的。
5. **要不要第一条留言**（first_comment，例如把落地页链接放在第一条留言）。
6. **要不要开「留言自动私讯」**（见第 5 节）。

## 2. 列排程，给用户看

写一张表，每帖一行：时间 · 平台 · 哪支片 · caption 开头。caption 全文放在表下面。

- caption 用马来西亚华人口语，不要 AI 腔（「赋能」「助力」不用）。
- **不编**：价钱、数字、见证、「保证」都只写用户给的。
- IG 最多 2,200 字、30 个 #hashtag；TikTok 影片文案最多 2,200 字。
- 用户说 OK 才往下。

## 3. 上传本机档案

本机的影片和照片要先变成公开网址：

```bash
python3 "<skill>/scripts/aigoal_social.py" --token-file key.txt upload "成片/第1支.mp4" "成片/第2支.mp4"
```

- 影片 MP4 / MOV，最大 300MB，会自动分块上传，断线会从断的地方接。
- 照片自动转 JPG（IG 只收 JPEG），最大 16MB。
- 印出来的 `https://app.aigoal.ai/avatars/…` 网址就填进 posts.json。这些档发完几天会自动清掉。
- 已经有公开 https 网址的（例如 studio 出片的网址）不用再上传，但要是**到发帖那一刻还打得开**的网址。

## 4. 写 posts.json → 检查 → 送

```json
[
  {"page_id": "1234567890", "platforms": ["facebook", "instagram"], "type": "reel",
   "video_url": "https://app.aigoal.ai/avatars/sv-….mp4",
   "caption": "买房前没人告诉你的 5 个坑……\n\n留言「GUIDE」，我把整份指南私讯给你 👇",
   "publish_at": "2026-11-24T20:00:00+08:00"},
  {"platforms": ["tiktok"], "type": "reel", "video_url": "https://app.aigoal.ai/avatars/sv-….mp4",
   "caption": "…", "publish_at": "2026-11-24T20:30:00+08:00"}
]
```

```bash
python3 "<skill>/scripts/aigoal_social.py" check posts.json          # 本机检查，不连网
python3 "<skill>/scripts/aigoal_social.py" --token-file key.txt send posts.json
```

栏位规矩（系统会照这些挡，写错整批都不排）：

- **每帖都要 publish_at**。格式 `2026-11-24T20:00:00+08:00`；没写时区当马来西亚时间；马上发写 `"now"`。不能是过去的时间，最远 180 天。
- **platforms**：`facebook` / `instagram` / `tiktok`。不写的话：有图或片 → FB + IG（专页有连 IG 才加）；纯文字 → 只 FB。**TikTok 一定要写明才会发。**
- **type**：`reel`（直式短片，FB 只收 3–90 秒）/ `video`（FB 一般影片，IG 不收）/ `photo` / `carousel`（`media` 阵列 2–20 个）/ `story` / `text`（只有 FB）。不写系统会自己判断。
- 一帖只能一个 `video_url` 或一个 `image_url`；`link` 只能放纯文字帖，影片帖的链接写进 caption 或 `first_comment`。
- `first_comment`：发出去之后自动留第一条留言（FB / IG）。
- `ai_generated: true`：AI 做的片可以打上「AI 生成」标记（FB Reels、IG）。
- 栏位名字打错会被挡（例如写成 `scheduled_at`、`image`），照上面的名字写。

送出去之后：

- **同一帖、同专页、同时间不会排两次**：送到一半断线，再送一次是安全的（回「之前就排过了」）。
- 回 `needs_reconnect` → 专页没授权发帖，请用户重连（第 0 节），**整批都没排**。
- 回 `media_check_failed` → 有媒体网址抓不到（过期、要登入、不是 https），改好再送。
- 回 `warnings` 就照实转告用户（例如「FB Reels 只收 3–90 秒」「时间当马来西亚时间」）。

## 5. 送完之后

- 告诉用户：排了几帖、几时发，在 app.aigoal.ai →「Social Media」看得到、改得到、取消得到。
- **错过 2 小时就不补发**（例如服务器停了），会标「没发出去」，要重排。
- IG 每天有发帖额度（`pages` 看得到还剩几帖），满了会延后，超过 12 小时就不发。
- TikTok 每个号每天最多用 API 发 15 帖。TikTok 失败常见原因：没给发帖权限、媒体网址的网域没在 TikTok 后台验证过。失败时 `list` 会写 TikTok 的原话，照实转告。

管理：

```bash
python3 "<skill>/scripts/aigoal_social.py" --token-file key.txt list --status pending      # 还没发的
python3 "<skill>/scripts/aigoal_social.py" --token-file key.txt list --status failed       # 没发出去的和原因
python3 "<skill>/scripts/aigoal_social.py" --token-file key.txt cancel --group <group_id>   # 同一次排的 FB + IG 一起取消
python3 "<skill>/scripts/aigoal_social.py" --token-file key.txt stats --ids id1,id2         # 已发的：观看、赞、留言、分享
```

改 caption / 时间、同一帖多排几天，叫用户在 Social Media 页面点那一帖改，最直接；要用 API 改，接口是 `POST /api/social/schedule/update`（`id` + `caption` / `publish_at`）和 `POST /api/social/schedule/copy`（`id` 或 `group_id` + `times`），改之前一样先讲给用户听。

## 6. 留言关键字自动私讯（选做）

片的 caption 叫人留言「GUIDE」，有人留言就自动私讯他落地页链接，并在留言下回一句「PM 你了」。

1. 先看现在的设定：`comments`。
2. 写一个 `cfg.json`，**只写要改的栏位**，给用户看过再送：
   ```json
   {"enabled": true,
    "keywords": ["guide", "指南", "pm", "link"],
    "dm_tpl": "嗨 {name}！你要的《首购族 5 个大坑》在这里 👉 https://…（落地页）填个名字就送去你的 WhatsApp 😊",
    "pub_hit_tpl": "PM 你了 ✅ check inbox 哦"}
   ```
   ```bash
   python3 "<skill>/scripts/aigoal_social.py" --token-file key.txt comments-set cfg.json
   ```
3. **每一帖要个别打开**：帖子发出去之后，用 `{"post_id": "<那一帖的 post_id>", "post_on": true}` 再送一次（post_id 在 `list` 已发那一帖里），或叫用户在 Social Media 页面把那一帖打开。

规矩：

- 关键字不分大小写，留言里包含就算命中；预设已经有 pm、价钱、link 这些，加上用户 caption 里叫人留的那个字。
- 私讯是固定文案，不是 AI 写的。`{name}` 会换成留言的人的名字。
- 一个留言只回一次；每页每小时最多私讯 20 个（防封号）；Meta 只让私讯 7 天内的留言。
- 没命中关键字的留言，预设不公开回（`generic_on: false`），不要随便打开。

## 分寸

- 钥匙等于用户的户口：只用在这件事，用完提醒他不用了就不要再贴给别人。
- 不发别人的片、名人或品牌的素材；caption 不冒充别的品牌。
- 「马上发」（`now`）一送就发，送之前再跟用户确认一次。
- 系统接口有改的话，先看 `https://app.aigoal.ai/api/docs` 的 social 那一段。
