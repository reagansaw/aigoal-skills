#!/usr/bin/env python3
"""给粗剪上字幕（和字卡），出一支可以直接发的竖屏片，外加一份 .srt。

    python3 add_captions.py <反推结果.md 或 分镜.md> <粗剪.mp4>
    python3 add_captions.py <md> <粗剪.mp4> --card "18-22.5=KAW/洗一次就干净"   # 加字卡（可以多个，/ 是换行）
    python3 add_captions.py <md> <粗剪.mp4> --lang ms        # 告诉 whisper 是什么语言（en / ms / zh），不写就自己猜
    python3 add_captions.py <md> <粗剪.mp4> --no-whisper     # 不听写，直接用 md 里写的秒数

字从哪里来：md「后制清单」里的「**字幕**」列表（- 0.0–3.5「…」），没有的话就拿剧本表里「某某：「…」」那一栏。
时间从哪里来：本机有 whisper 就把影片听写一次，一句一句对上稿子，用听到的时间；字一律用稿子的（听写会听错字）。
对不上的句子用 md 的秒数，最后会列出来，请用户自己看那几句。

不用 libass：字先用 PIL 画成透明图，再用 ffmpeg 的 overlay 叠上去，哪台电脑的 ffmpeg 都能跑。
画面放大到 1080×1920；字幕放在画面约 2/3 的高度，避开抖音 / Reels 底下的按钮和文案。
同时出一份 .srt，想在剪映里改字、换字体，就把它拖进剪映（文本 → 本地字幕）。
"""
import argparse, difflib, json, os, re, shutil, subprocess, sys, tempfile, unicodedata

W, H = 1080, 1920
SUB_BOTTOM = 1300      # 字幕最下面一行的底边（安全区：底下约 1/3 会被平台按钮挡）
CARD_TOP = 260


# ---------- 稿子 ----------
def parse_lines(md):
    t = open(md, encoding="utf-8").read()
    out = []
    m = re.search(r"\*\*字幕\*\*.*?\n((?:\s*-\s*[\d.]+\s*[–-]\s*[\d.]+.*\n?)+)", t)
    if m:
        for a, b, s in re.findall(r"-\s*([\d.]+)\s*[–-]\s*([\d.]+)\s*「(.+?)」", m.group(1)):
            out.append([float(a), float(b), s.strip()])
        return out
    # 剧本表：| 拍 | 秒数 | 画面 | 台词 |
    for row in t.splitlines():
        if not row.startswith("|") or "：「" not in row or "后制" in row:
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        tm = next((re.match(r"([\d.]+)\s*[–-]\s*([\d.]+)", c) for c in cells if re.match(r"[\d.]+\s*[–-]\s*[\d.]+$", c)), None)
        for s in re.findall(r"：「(.+?)」", cells[-1]):
            a, b = (float(tm.group(1)), float(tm.group(2))) if tm else (0, 0)
            out.append([a, b, s.strip()])
    return out


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[\W_]+", "", s)


# ---------- 听写对时间 ----------
def whisper_segments(video, lang, tmp):
    exe = shutil.which("whisper")
    if not exe:
        return None
    cmd = [exe, video, "--model", "small", "--output_format", "json", "--output_dir", tmp, "--verbose", "False"]
    if lang:
        cmd += ["--language", lang]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    js = os.path.join(tmp, os.path.splitext(os.path.basename(video))[0] + ".json")
    if not os.path.exists(js):
        return None
    return [(s["start"], s["end"], s["text"]) for s in json.load(open(js))["segments"]]


def align(lines, segs):
    """稿子一句一句往后找听写的段（可以合并两段、或一段拆给两句），分数够才用听到的时间。"""
    miss, j = [], 0
    for i, ln in enumerate(lines):
        best = (0, None)
        for k in range(j, min(j + 4, len(segs))):
            for span in (1, 2):
                if k + span > len(segs):
                    continue
                txt = "".join(segs[x][2] for x in range(k, k + span))
                r = difflib.SequenceMatcher(None, norm(ln[2]), norm(txt)).ratio()
                if r > best[0]:
                    best = (r, (k, span))
        if best[0] >= 0.45:
            k, span = best[1]
            ln[0], ln[1] = segs[k][0], segs[k + span - 1][1]
            j = k + span
        else:
            miss.append(ln[2])
    for a, b in zip(lines, lines[1:]):          # 不重叠
        if a[1] > b[0]:
            a[1] = b[0]
    return miss


# ---------- 画字 ----------
def find_font(size):
    from PIL import ImageFont
    tries = []
    try:
        p = subprocess.run(["fc-list", ":family=PingFang SC", "file"], capture_output=True, text=True).stdout.split(":")[0].strip()
        if p:
            tries.append(p)
    except FileNotFoundError:
        pass
    tries += ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc", "/Library/Fonts/Arial Unicode.ttf",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"]
    for p in tries:
        if not os.path.exists(p):
            continue
        faces = []
        for idx in range(0, 40):
            try:
                faces.append(ImageFont.truetype(p, size, index=idx))
            except Exception:
                break
        for want in ("Semibold", "Medium", "Bold"):
            for f in faces:
                fam, style = f.getname()
                if style == want and (fam.endswith(" SC") or "CJK" in fam or "Hei" in fam):
                    return f
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


NO_START = set("，。、！？；：,.!?;:…）」』”’)")


def wrap(text, font, maxw, draw):
    if "/" in text:                      # 字卡可以用 / 自己断行
        return [r.strip() for p in text.split("/") for r in wrap(p.strip(), font, maxw, draw)]
    cjk = sum(1 for c in text if ord(c) > 0x2E80) > len(text) / 3
    units = list(text) if cjk else text.split(" ")
    sep = "" if cjk else " "
    lines, cur = [], ""
    for u in units:
        t = (cur + sep + u) if cur else u
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = u
    if cur:
        lines.append(cur)
    for n in range(1, len(lines)):       # 标点不放在行首
        while lines[n] and lines[n][0] in NO_START:
            lines[n - 1] += lines[n][0]
            lines[n] = lines[n][1:]
    return [l for l in lines if l]


def render(text, path, kind):
    from PIL import Image, ImageDraw
    size = 66 if kind == "sub" else 76
    font = find_font(size)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rows = wrap(text, font, 920, d)[:3]
    lh = int(size * 1.3)
    y0 = SUB_BOTTOM - lh * len(rows) if kind == "sub" else CARD_TOP
    if kind == "card":
        bw = max(d.textlength(r, font=font) for r in rows) + 80
        d.rounded_rectangle([(W - bw) / 2, y0 - 30, (W + bw) / 2, y0 + lh * len(rows) + 20], 28, fill=(0, 0, 0, 170))
    for n, r in enumerate(rows):
        x = (W - d.textlength(r, font=font)) / 2
        fill = (255, 255, 255) if kind == "sub" else (255, 214, 64)
        d.text((x, y0 + n * lh), r, font=font, fill=fill, stroke_width=7 if kind == "sub" else 0, stroke_fill=(0, 0, 0))
    img.save(path)


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--card", action="append", default=[], help="起-止=文字，/ 是换行，例 18-22.5=KAW/洗一次就干净")
    ap.add_argument("--lang")
    ap.add_argument("--no-whisper", action="store_true")
    a = ap.parse_args()

    lines = parse_lines(a.md)
    if not lines:
        sys.exit("md 里找不到字幕：后制清单要有「**字幕**」列表，或剧本表里有「某某：「…」」。")
    tmp = tempfile.mkdtemp(prefix="captions_")
    miss = []
    segs = None if a.no_whisper else whisper_segments(a.video, a.lang, tmp)
    if segs:
        miss = align(lines, segs)
    else:
        print("没有用 whisper 对时间：用 md 里写的秒数（可能差一点，出片后看一遍）。")

    cards = []
    for c in a.card:
        m = re.match(r"\s*([\d.]+)\s*-\s*([\d.]+)\s*=\s*(.+)", c)
        if m:
            cards.append((float(m.group(1)), float(m.group(2)), m.group(3)))

    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.video)), "成片-字幕.mp4")
    srt = os.path.splitext(out)[0] + ".srt"
    with open(srt, "w", encoding="utf-8") as f:
        for n, (s, e, t) in enumerate(lines, 1):
            f.write(f"{n}\n{srt_time(s)} --> {srt_time(e)}\n{t}\n\n")

    inputs, chain, last = [], [f"[0:v]scale={W}:{H}:flags=lanczos,setsar=1[v0]"], "v0"
    items = [(s, e, t, "sub") for s, e, t in lines] + [(s, e, t, "card") for s, e, t in cards]
    for n, (s, e, t, kind) in enumerate(items, 1):
        png = os.path.join(tmp, f"{n}.png")
        render(t, png, kind)
        inputs += ["-i", png]
        chain.append(f"[{last}][{n}:v]overlay=0:0:enable='between(t,{s:.2f},{e:.2f})'[v{n}]")
        last = f"v{n}"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", a.video, *inputs, "-filter_complex", ";".join(chain),
           "-map", f"[{last}]", "-map", "0:a?", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "copy", out]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)

    print(f"出片：{out}")
    print(f"字幕档：{srt}（要在剪映改字，把它拖进剪映：文本 → 本地字幕）")
    for s, e, t in lines:
        print(f"  {s:5.1f}–{e:5.1f}  {t}")
    if miss:
        print("这几句听写对不上，用的是 md 的秒数，请看一遍：")
        for t in miss:
            print("  ·", t)


if __name__ == "__main__":
    main()
