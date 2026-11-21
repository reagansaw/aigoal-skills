# AIGOAL Skills

AIGOAL 学员用的 Claude skills。装好之后，在 Claude 里打 `/` 选，或直接用一句话叫它做。

| skill | 做什么 | 怎么叫它 |
|---|---|---|
| `thai-ad` | 泰式搞笑广告：只要讲卖什么、品牌名、一个卖点，用逆向演绎法反推出 3 个点子，写成 30 秒剧本和 Seedance 2.5 分镜，直接搭好 studio 画布 | 「帮我想一支泰国广告」「写广告剧本」 |
| `hook` | 开头 3 秒的钩子：讲卖什么、给谁看，用「8 个按钮 × 一个具体细节」出 10 条不同路线的钩子，再写成 60 秒口播稿，或「一段正文配 3 个钩子」的广告测试组 | 「帮我想开头」「写口播稿」「广告钩子」 |
| `video-reverse` | 给一条爆款视频，逐镜头看懂，换成你的人物、产品、场景，写出可以直接贴进 Seedance 2.0 的分段提示词 | 「反推这条」「做同款」 |
| `character-sheet` | 人物角色卡：一人一张 16:9 三格图（脸部特写 / 正面全身 / 背面全身），文字生成或用你的照片做，出片前先锁住脸和衣服 | 「做角色卡」「定妆」 |
| `aigoal-landing` | 落地页：lead magnet（Opt-in + Thank you）或 webinar（报名 + VIP + 登记成功），换成你的品牌色，放进 app.aigoal.ai | 「帮我做领取页」「做 webinar 报名页」 |
| `aigoal-social` | 排程发片：把做好的片排到 FB 专页、IG、TikTok，一次排一个礼拜；查排程、取消、看观看数；设定留言关键字自动私讯 | 「这礼拜一三五晚上 8 点发」「帮我发到 FB IG」 |
| `aigoal-whatsapp` | WhatsApp 讯息：活动前 7 条预热、webinar 报名后提醒、lead magnet 领取后跟进，附配图 | 「写预热讯息」「写报名后提醒」 |

适合所有行业：卖产品、本地服务（美容、养生、汽车）、专业服务（房产、保险、融资）、课程教练都能用。`aigoal-landing` 和 `aigoal-whatsapp` 里有各行业怎么用的对照表；`video-reverse` 换的是你自己的人物、产品、场景，本来就不限行业；`thai-ad` 有 13 个行业例子；`hook` 问的是你自己生意的真细节，哪一行都能写。

剪辑另外装 **video-craft**（口播剪出网感）：<https://github.com/reagansaw/jingjian>

## 安装

在 Claude Code 里打这两行：

```
/plugin marketplace add reagansaw/aigoal-skills
/plugin install aigoal-skills@aigoal-skills
```

装好后**新开一个对话**再用。

剪辑 skill：

```
/plugin marketplace add reagansaw/jingjian
/plugin install video-craft@video-craft
```

### 手动安装

把 `skills/` 里面的文件夹（每个里面都有 `SKILL.md`）整个复制到：

- Mac：`~/.claude/skills/`（你的个人文件夹里的 `.claude/skills`，Finder 按 Command + Shift + 句号 显示隐藏文件夹）
- Windows：`C:\Users\你的名字\.claude\skills\`

然后重开 Claude。

## 要先装的工具

| 工具 | 哪个 skill 要 | Mac | Windows |
|---|---|---|---|
| ffmpeg | video-reverse | `brew install ffmpeg` | `winget install Gyan.FFmpeg` |
| Python 3 | video-reverse、thai-ad（搭画布） | `brew install python` | `winget install Python.Python.3.12` |
| whisper（可选，听写台词、出片后对稿） | video-reverse | `uv tool install openai-whisper` | `uv tool install openai-whisper` |
| yt-dlp（可选，下载链接） | video-reverse | `brew install yt-dlp` | `winget install yt-dlp.yt-dlp` |

`hook`、`aigoal-landing`、`aigoal-whatsapp`、`aigoal-social` 不用装工具（`aigoal-social` 要 Python 3）。

## studio 钥匙（可选）

`video-reverse` 有 studio.aigoal.ai 的钥匙时，会拿最新的提示词指南，也能直接帮你搭 studio 画布；没有钥匙就用内置的离线版本。`thai-ad` 有钥匙才能直接搭画布，没有就只交分镜。钥匙设成环境变量 `AIGOAL_STUDIO_KEY`，**不要贴进任何档案**。

## 版本

0.5.0 · 2026-11-21
