# AIGOAL Skills

AIGOAL 学员用的 Claude skills。装好之后，在 Claude 里打 `/` 选，或直接用一句话叫它做。

| skill | 做什么 | 怎么叫它 |
|---|---|---|
| `video-reverse` | 给一条爆款视频，逐镜头看懂，换成你的人物、产品、场景，写出可以直接贴进 Seedance 2.0 的分段提示词 | 「反推这条」「做同款」 |
| `character-sheet` | 人物角色卡：一人一张 16:9 三格图（脸部特写 / 正面全身 / 背面全身），文字生成或用你的照片做，出片前先锁住脸和衣服 | 「做角色卡」「定妆」 |
| `aigoal-landing` | 落地页：lead magnet（Opt-in + Thank you）或 webinar（报名 + VIP + 登记成功），换成你的品牌色，放进 app.aigoal.ai | 「帮我做领取页」「做 webinar 报名页」 |
| `aigoal-whatsapp` | WhatsApp 讯息：活动前 7 条预热、webinar 报名后提醒、lead magnet 领取后跟进，附配图 | 「写预热讯息」「写报名后提醒」 |

适合所有行业：卖产品、本地服务（美容、养生、汽车）、专业服务（房产、保险、融资）、课程教练都能用。`aigoal-landing` 和 `aigoal-whatsapp` 里有各行业怎么用的对照表；`video-reverse` 换的是你自己的人物、产品、场景，本来就不限行业。

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
| Python 3 | video-reverse | `brew install python` | `winget install Python.Python.3.12` |
| whisper（可选，听写台词、出片后对稿） | video-reverse | `uv tool install openai-whisper` | `uv tool install openai-whisper` |
| yt-dlp（可选，下载链接） | video-reverse | `brew install yt-dlp` | `winget install yt-dlp.yt-dlp` |

`aigoal-landing` 和 `aigoal-whatsapp` 不用装工具。

## studio 钥匙（可选）

`video-reverse` 有 studio.aigoal.ai 的钥匙时，会拿最新的提示词指南，也能直接帮你搭 studio 画布；没有钥匙就用内置的离线版本。钥匙设成环境变量 `AIGOAL_STUDIO_KEY`，**不要贴进任何档案**。

## 版本

0.2.0 · 2026-11-20
