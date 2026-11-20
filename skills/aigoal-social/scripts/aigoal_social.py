#!/usr/bin/env python3
"""用 app.aigoal.ai 的 social API 排程发片到 FB 专页 / Instagram / TikTok。

用法（钥匙放环境变量 AIGOAL_TOKEN，或 --token-file 指一个只放钥匙的暂存档）:
    python3 aigoal_social.py pages                       # 连了哪些专页、能不能发、IG 今天还剩几帖
    python3 aigoal_social.py upload 第1支.mp4 封面.jpg     # 上传本机影片 / 照片 → 印出公开网址
    python3 aigoal_social.py check posts.json            # 只在本机检查，不连网、不发
    python3 aigoal_social.py send posts.json             # 真的送进排程（会先检查一次）
    python3 aigoal_social.py list [--status pending]     # 排程清单
    python3 aigoal_social.py cancel --id <id> | --group <group_id>
    python3 aigoal_social.py stats --ids id1,id2         # 已发的帖：观看 / 赞 / 留言
    python3 aigoal_social.py comments                    # 看「留言自动私讯」现在的设定
    python3 aigoal_social.py comments-set cfg.json       # 改「留言自动私讯」（只送 cfg.json 里写的栏位）

posts.json：一个阵列，每一帖一个物件，例如
    [{"page_id": "1234", "platforms": ["facebook", "instagram"], "type": "reel",
      "video_url": "https://app.aigoal.ai/avatars/sv-….mp4",
      "caption": "…", "publish_at": "2026-11-24T20:00:00+08:00"}]

只用 Python 标准库。钥匙不要写进任何档案、不要印出来。
"""
import argparse
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("AIGOAL_APP_URL", "https://app.aigoal.ai").rstrip("/")
POST_KEYS = {"page_id", "ig_id", "platforms", "platform", "type", "caption", "message", "image_url", "video_url", "link",
             "publish_at", "cover_url", "share_to_feed", "title", "alt_text", "external_ref", "allow_duplicate", "media",
             "first_comment", "comments_off", "thumb_offset_ms", "audio_name", "collaborators", "location_id",
             "user_tags", "trial", "ai_generated"}
TYPES = {"text", "photo", "video", "reel", "carousel", "story"}
CHUNK = 8 * 1024 * 1024
VIDEO_MAX = 300 * 1024 * 1024
IMAGE_MAX = 16 * 1024 * 1024


def token(args):
    t = ""
    if getattr(args, "token_file", None):
        t = open(os.path.expanduser(args.token_file), encoding="utf-8").read()
    t = (t or os.environ.get("AIGOAL_TOKEN") or os.environ.get("AIGOAL_API_KEY") or "").strip()
    m = re.search(r"Bearer\s+(\S+)", t)  # 整段从「整合中心 → API 钥匙」复制来的也认
    t = m.group(1) if m else t.split()[-1] if t else ""
    if not t:
        sys.exit("没有钥匙。请用户到 app.aigoal.ai →「整合中心」→「API 钥匙」→ 复制，贴给你；"
                 "你放进环境变量 AIGOAL_TOKEN（或 --token-file 暂存档），不要写进任何档案。")
    return t


def call(args, method, path, body=None, raw=None, ctype="application/json"):
    data = raw if raw is not None else (json.dumps(body, ensure_ascii=False).encode() if body is not None else None)
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token(args))
    if data is not None:
        req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            j = json.loads(e.read() or b"{}")
        except ValueError:
            j = {"error": f"http_{e.code}"}
        if e.code == 401:
            j.setdefault("message", "钥匙过期或不对：请用户回「整合中心 → API 钥匙」按「换一把新的」再贴一次")
        if e.code in (403, 404) and path.startswith("/api/social"):
            j.setdefault("message", "这个户口可能还没开 Social Media 功能，或没有管理层权限：请问你的 AIGOAL 顾问")
        return e.code, j


def show(status, j):
    print(json.dumps(j, ensure_ascii=False, indent=2))
    if status >= 400 or j.get("ok") is False:
        sys.exit(1)


# ---------- pages ----------

def cmd_pages(args):
    st, j = call(args, "GET", "/api/social/schedule/pages")
    if st >= 400:
        show(st, j)
    if j.get("paused"):
        print("⚠️ 系统的自动发帖现在暂停中：排了会留着，恢复后照发。")
    pages = j.get("pages") or []
    if not pages:
        print("还没有连 FB 专页：请用户到「整合中心 → Facebook & Instagram」连专页。")
    for p in pages:
        fb = (p.get("facebook") or {}).get("can_publish")
        ig = p.get("instagram")
        q = (ig or {}).get("quota") or {}
        print(f"- {p.get('page_name') or p.get('name') or ''}  page_id={p.get('page_id')}"
              f"  FB 发帖：{'可以' if fb else '要重连' if fb is False else '不确定'}"
              f"  IG：{'没连' if not ig else ('可以' if ig.get('can_publish') else '要重连' if ig.get('can_publish') is False else '不确定')}"
              + (f"（今天已用 {q.get('used')}/{q.get('total')}）" if q.get('total') else ""))
    tt = j.get("tiktok") or {}
    print(f"- TikTok：{'没连' if not tt.get('connected') else ('可以发 @' + tt.get('username', '') if tt.get('can_publish') else '要重连（没给发帖权限）')}")


# ---------- upload ----------

def to_jpeg(path):
    """IG 照片只收 JPEG：PNG / HEIC 先用 Mac 的 sips 转。"""
    out = os.path.splitext(path)[0] + ".upload.jpg"
    if os.system(f'sips -s format jpeg "{path}" --out "{out}" >/dev/null 2>&1') != 0 or not os.path.exists(out):
        sys.exit(f"{path} 不是 JPG，转档失败：请先存成 .jpg 再上传")
    return out


def upload_video(args, path):
    size = os.path.getsize(path)
    ext = os.path.splitext(path)[1].lower()
    mime = {".mp4": "video/mp4", ".mov": "video/quicktime", ".m4v": "video/mp4"}.get(ext)
    if not mime:
        sys.exit(f"{path}：影片只收 MP4 / MOV")
    if size > VIDEO_MAX:
        sys.exit(f"{path}：{size / 1048576:.0f}MB，超过 300MB，先压缩")
    st, j = call(args, "POST", "/api/social/video-upload/start", {"size": size, "mime": mime})
    if st >= 400 or not j.get("ok"):
        show(st, j)
    uid, step = j["id"], int(j.get("chunk") or CHUNK)
    with open(path, "rb") as f:
        off = 0
        while off < size:
            buf = f.read(step)
            q = urllib.parse.urlencode({"id": uid, "offset": off})
            st, r = call(args, "PUT", f"/api/social/video-upload/chunk?{q}", raw=buf, ctype="application/octet-stream")
            if st == 409 and "have" in r:  # 断线重送：从服务器已经收到的地方接
                off = int(r["have"])
                f.seek(off)
                continue
            if st >= 400 or not r.get("ok"):
                call(args, "POST", "/api/social/video-upload/cancel", {"id": uid})
                show(st, r)
            off += len(buf)
            print(f"  {os.path.basename(path)}：{off * 100 // size}%", file=sys.stderr)
    st, j = call(args, "POST", "/api/social/video-upload/finish", {"id": uid})
    if st >= 400 or not j.get("ok"):
        show(st, j)
    return urllib.parse.urljoin(BASE + "/", j["url"].lstrip("/"))


def upload_image(args, path):
    if os.path.splitext(path)[1].lower() not in (".jpg", ".jpeg"):
        path = to_jpeg(path)
    if os.path.getsize(path) > IMAGE_MAX:
        sys.exit(f"{path}：超过 16MB，先缩小")
    import base64
    data = "data:image/jpeg;base64," + base64.b64encode(open(path, "rb").read()).decode()
    st, j = call(args, "POST", "/api/attach/upload", {"data": data})
    if st >= 400 or not j.get("ok"):
        show(st, j)
    return urllib.parse.urljoin(BASE + "/", j["url"].lstrip("/"))


def cmd_upload(args):
    for p in args.files:
        if not os.path.isfile(p):
            sys.exit(f"找不到档案：{p}")
        kind = (mimetypes.guess_type(p)[0] or "").split("/")[0]
        url = upload_video(args, p) if kind == "video" or p.lower().endswith((".mp4", ".mov", ".m4v")) else upload_image(args, p)
        print(f"{p}\t{url}")


# ---------- check / send ----------

def check_posts(posts):
    """本机先挡最常见的错；服务器还会再检查一次（例如媒体网址抓不抓得到、权限）。"""
    problems, notes = [], []
    if not isinstance(posts, list) or not posts:
        return ["posts.json 要是一个阵列，至少一帖"], notes
    if len(posts) > 100:
        problems.append("一次最多 100 帖，分几批送")
    for i, p in enumerate(posts, 1):
        at = f"第 {i} 帖"
        if not isinstance(p, dict):
            problems.append(f"{at}要是一个物件")
            continue
        bad = sorted(set(p) - POST_KEYS)
        if bad:
            problems.append(f"{at}有不认识的栏位：{', '.join(bad)}（时间写 publish_at，影片写 video_url，照片写 image_url）")
        if not p.get("publish_at"):
            problems.append(f"{at}没写 publish_at（马上发写 \"now\"）")
        elif p["publish_at"] != "now" and not re.search(r"(Z|[+-]\d{2}:?\d{2})$", str(p["publish_at"])):
            notes.append(f"{at}的时间没写时区，系统当马来西亚时间（+08:00）")
        plats = p.get("platforms", p.get("platform"))
        plats = [plats] if isinstance(plats, str) else (plats or [])
        plats = [{"fb": "facebook", "ig": "instagram", "tt": "tiktok"}.get(str(x).lower(), str(x).lower()) for x in plats]
        t = str(p.get("type") or "").lower()
        if t and t not in TYPES:
            problems.append(f"{at}的 type 只能是 {' / '.join(sorted(TYPES))}")
        has_video, has_image = bool(p.get("video_url")), bool(p.get("image_url"))
        for k in ("video_url", "image_url", "cover_url", "link"):
            if p.get(k) and not str(p[k]).startswith("https://"):
                problems.append(f"{at}的 {k} 要是 https:// 公开网址（本机档案先用 upload 上传）")
        if "instagram" in plats:
            if not (has_video or has_image or p.get("media")):
                problems.append(f"{at}：IG 不能发纯文字")
            if t == "video":
                problems.append(f"{at}：IG 的影片一律是 Reel，type 写 reel")
            cap = str(p.get("caption") or "")
            if len(cap) > 2200:
                problems.append(f"{at}：IG 文案最多 2,200 字（现在 {len(cap)}）")
            if len(re.findall(r"(^|\s)#[^\s#]+", cap)) > 30:
                problems.append(f"{at}：IG 最多 30 个 #hashtag")
        if "tiktok" in plats:
            if not (has_video or has_image):
                problems.append(f"{at}：TikTok 只能发影片或照片")
            if len(str(p.get("caption") or "")) > (2200 if has_video else 4000):
                problems.append(f"{at}：TikTok 文案太长")
            notes.append(f"{at}：TikTok 每个号每天最多用 API 发 15 帖")
        if "facebook" in plats and (t == "reel" or (not t and has_video)):
            notes.append(f"{at}：FB Reels 只收 3–90 秒直式影片；更长的片 FB 那边 type 写 video")
        if p.get("link") and (has_video or has_image):
            problems.append(f"{at}：link 只能放在纯文字帖；影片帖把链接写进 caption 或 first_comment")
        if p.get("publish_at") == "now":
            notes.append(f"{at}写了 now：一送出去就发")
    return problems, notes


def load_posts(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"读不了 {path}：{e}")


def cmd_check(args):
    problems, notes = check_posts(load_posts(args.file))
    for n in notes:
        print("· " + n)
    if problems:
        print("\n有问题，先改：")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("本机检查通过。真的要排，再跑 send。")


def cmd_send(args):
    posts = load_posts(args.file)
    problems, notes = check_posts(posts)
    if problems:
        print("有问题，没有送：")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    body = {"posts": posts}
    if args.skip_media_check:
        body["skip_media_check"] = True
    st, j = call(args, "POST", "/api/social/schedule", body)
    if st >= 400 or not j.get("ok"):
        if j.get("error") == "needs_reconnect":
            print("专页还没授权发帖：请用户到「整合中心 → Facebook & Instagram」重连，授权页上「管理贴文 / 发布内容」要打勾。整批没有排。")
        show(st, j)
    made = j.get("created") or []
    again = j.get("already_scheduled") or []
    print(f"已排 {len(made)} 条" + (f"，{len(again)} 条之前就排过了（没有重复排）" if again else "") + "。")
    for r in made:
        print(f"  - {r.get('publish_at')}  {r.get('platform')}  id={r.get('id')}  group={r.get('group_id')}")
    for w in j.get("warnings") or []:
        print("· " + str(w))
    if j.get("paused"):
        print("⚠️ 系统的自动发帖现在暂停中：排了会留着，恢复后照发。")
    print("在 app.aigoal.ai →「Social Media」看得到。")


# ---------- manage ----------

def cmd_list(args):
    q = {k: v for k, v in (("status", args.status), ("limit", args.limit)) if v}
    st, j = call(args, "GET", "/api/social/schedule" + ("?" + urllib.parse.urlencode(q) if q else ""))
    if st >= 400:
        show(st, j)
    for r in j.get("posts") or j.get("rows") or []:
        print(f"- {r.get('publish_at')}  {r.get('platform'):<9}  {r.get('status'):<10}  id={r.get('id')}  "
              f"{str(r.get('caption') or '')[:40].replace(chr(10), ' ')}"
              + (f"  ✗ {r.get('message') or r.get('error')}" if r.get("status") in ("failed", "unknown") else "")
              + (f"  {r.get('permalink')}" if r.get("permalink") else ""))


def cmd_cancel(args):
    if not (args.id or args.group):
        sys.exit("要给 --id 或 --group")
    show(*call(args, "POST", "/api/social/schedule/cancel", {"id": args.id} if args.id else {"group_id": args.group}))


def cmd_stats(args):
    show(*call(args, "GET", "/api/social/schedule/stats?" + urllib.parse.urlencode({"ids": args.ids})))


def cmd_comments(args):
    st, j = call(args, "GET", "/api/social/config")
    show(st, {"comments": j.get("comments"), "status": j.get("status")} if st < 400 else j)


def cmd_comments_set(args):
    cfg = load_posts(args.file)
    allowed = {"enabled", "generic_on", "keywords", "dm_tpl", "pub_hit_tpl", "pub_generic_tpl", "hourly_cap",
               "dm_quick", "dm_buttons", "post_id", "post_on"}
    bad = sorted(set(cfg) - allowed)
    if bad:
        sys.exit(f"不认识的栏位：{', '.join(bad)}（可以用的：{', '.join(sorted(allowed))}）")
    show(*call(args, "POST", "/api/social/comments-config", cfg))


def main():
    ap = argparse.ArgumentParser(description="app.aigoal.ai social API：排程发片")
    ap.add_argument("--token-file", help="只放钥匙的暂存档（不给就读环境变量 AIGOAL_TOKEN）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pages")
    u = sub.add_parser("upload"); u.add_argument("files", nargs="+")
    c = sub.add_parser("check"); c.add_argument("file")
    s = sub.add_parser("send"); s.add_argument("file"); s.add_argument("--skip-media-check", action="store_true")
    li = sub.add_parser("list"); li.add_argument("--status"); li.add_argument("--limit")
    ca = sub.add_parser("cancel"); ca.add_argument("--id"); ca.add_argument("--group")
    stt = sub.add_parser("stats"); stt.add_argument("--ids", required=True)
    sub.add_parser("comments")
    cs = sub.add_parser("comments-set"); cs.add_argument("file")
    a = ap.parse_args()
    {"pages": cmd_pages, "upload": cmd_upload, "check": cmd_check, "send": cmd_send, "list": cmd_list,
     "cancel": cmd_cancel, "stats": cmd_stats, "comments": cmd_comments, "comments-set": cmd_comments_set}[a.cmd](a)


if __name__ == "__main__":
    main()
