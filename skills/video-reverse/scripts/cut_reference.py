#!/usr/bin/env python3
"""贴原片模式用：把原片照分段切成一段一段的参考视频（@video1），顺便抽出整条原声。

用法:
    python3 cut_reference.py <原片> --cuts "0-13.5,13.5-27,27-38.2" --out <输出文件夹>/素材
    python3 cut_reference.py <原片> --cuts "0-13.5,13.5-27" --out <素材文件夹> --keep-audio   # 参考片段保留声音（卡点片）

出来的档案:
    原片-第1段.mp4、原片-第2段.mp4 …   每段 2–15 秒、MP4（H.264）、长边不超过 1280、默认静音
    原片-原声.m4a                       整条原片的声音，粗剪时用 assemble.py --audio 贴回去

切点用镜头表的秒数，切在镜头和镜头之间，不要切在一句话或一个动作中间。
只用 Python 标准库 + ffmpeg。
"""
import argparse
import os
import shutil
import subprocess
import sys

MIN_SEC, MAX_SEC = 2.0, 15.0


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path, entries, stream=None):
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream]
    cmd += ["-show_entries", entries, "-of", "csv=p=0", path]
    return run(cmd).stdout.strip()


def parse_cuts(text):
    cuts = []
    for part in text.replace("，", ",").split(","):
        part = part.strip().replace("–", "-").replace("—", "-")
        if not part:
            continue
        try:
            a, b = (float(x) for x in part.split("-"))
        except ValueError:
            sys.exit(f"看不懂这一段：「{part}」。写法是 起-止（秒），例如 0-13.5,13.5-27")
        cuts.append((a, b))
    if not cuts:
        sys.exit("没有给切点。例：--cuts \"0-13.5,13.5-27\"")
    return cuts


def main():
    ap = argparse.ArgumentParser(description="把原片切成每段一个参考视频")
    ap.add_argument("video")
    ap.add_argument("--cuts", required=True, help="每段的起止秒数，逗号分开：0-13.5,13.5-27")
    ap.add_argument("--out", help="输出文件夹，默认 <原片所在文件夹>/素材")
    ap.add_argument("--keep-audio", action="store_true", help="参考片段保留声音（默认静音，声音在粗剪时贴回）")
    a = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"找不到 {tool}。请先安装 ffmpeg：\n  Mac:     brew install ffmpeg\n  Windows: winget install Gyan.FFmpeg")
    src = os.path.abspath(os.path.expanduser(a.video))
    if not os.path.isfile(src):
        sys.exit(f"找不到原片：{src}")
    try:
        total = float(probe(src, "format=duration"))
    except ValueError:
        sys.exit(f"读不到影片长度：{src}")
    out = os.path.abspath(os.path.expanduser(a.out)) if a.out else os.path.join(os.path.dirname(src), "素材")
    os.makedirs(out, exist_ok=True)

    cuts = parse_cuts(a.cuts)
    problems = []
    for i, (s, e) in enumerate(cuts, 1):
        if e > total + 0.05:
            problems.append(f"第 {i} 段到 {e} 秒，但原片只有 {total:.1f} 秒")
        if not MIN_SEC <= e - s <= MAX_SEC:
            problems.append(f"第 {i} 段 {e - s:.1f} 秒，参考视频一段要 {MIN_SEC:.0f}–{MAX_SEC:.0f} 秒")
        if i > 1 and abs(s - cuts[i - 2][1]) > 0.05:
            problems.append(f"第 {i} 段从 {s} 秒开始，上一段停在 {cuts[i - 2][1]} 秒，中间{'重叠' if s < cuts[i - 2][1] else '漏了'} {abs(s - cuts[i - 2][1]):.1f} 秒")
    if problems:
        print("切点有问题，改了再跑：")
        for p in problems:
            print("  - " + p)
        sys.exit(1)

    vf = "scale='if(gt(iw,ih),min(1280,iw),-2)':'if(gt(iw,ih),-2,min(1280,ih))',setsar=1,fps=30,format=yuv420p"
    for i, (s, e) in enumerate(cuts, 1):
        dst = os.path.join(out, f"原片-第{i}段.mp4")
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{e - s:.3f}", "-i", src, "-vf", vf,
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
        cmd += ["-c:a", "aac", "-b:a", "128k"] if a.keep_audio else ["-an"]
        cmd += ["-movflags", "+faststart", dst]
        r = run(cmd)
        if r.returncode != 0:
            sys.exit(f"切第 {i} 段时出错：\n{r.stderr[-600:]}")
        mb = os.path.getsize(dst) / 1e6
        print(f"  第 {i} 段：{s:g}–{e:g} 秒（{e - s:.1f} 秒，{mb:.1f} MB）→ {dst}")

    if probe(src, "stream=index", "a"):
        aud = os.path.join(out, "原片-原声.m4a")
        r = run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-c:a", "aac", "-b:a", "160k", aud])
        if r.returncode == 0:
            print(f"  原声：{aud}（粗剪时用 assemble.py --audio 贴回去）")
    else:
        print("  原片没有声音，不抽原声。")
    covered = sum(e - s for s, e in cuts)
    print(f"\n共 {len(cuts)} 段，合计 {covered:.1f} 秒（原片 {total:.1f} 秒）。")
    print("在素材清单里把这些档列成「片A、片B…」，每段写「接视频：@video1 = 片A」。")


if __name__ == "__main__":
    main()
