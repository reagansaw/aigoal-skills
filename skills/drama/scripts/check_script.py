#!/usr/bin/env python3
"""剧本自查：算时长、找书面词、数语气词。

用法：python3 check_script.py <剧本.md>

读剧本里「秒数 | 画面 | 台词」那张表，报告：
- 每一行的台词装不装得下（平常每秒 4 个字，最快 6 个）
- 全片总字数有没有超过上限（45 秒以内当短梗，80 字；更长的当大片，「秒数 × 3.5」）
- 第一句有没有超过 12 个字
- 台词里的中国讲法（照换词表）
- 语气词：一句超过一个、连续三行都带
- 可能把答案讲破的句式

只用标准库，不连网，不改文件。它只会算和找，讲不讲得通、好不好笑还是要人看。
"""
import re
import sys

RATE_MAX = 6.0      # 一行超过每秒 6 个字，一定讲不完
RATE_TIGHT = 5.0    # 超过每秒 5 个字，很赶
FILM_RATIO = 3.5    # 全片总字数 ÷ 总秒数 的上限
FIRST_MAX = 12      # 第一句最多几个字
SHORT_MAX_SEC = 45  # 表里最后一行在这之内，当短梗
SHORT_CHARS = 80    # 短梗全片字数上限

SWAP = {
    "空调": "冷气", "而已": "罢了", "出租车": "德士", "打车": "叫 Grab",
    "公交": "巴士", "摩托车": "摩多", "自行车": "脚车", "卡车": "罗里",
    "堵车": "塞车", "洗澡": "冲凉", "上班": "做工", "下班": "放工",
    "工资": "薪水 / 出粮", "请假": "拿假", "外卖": "打包 / tapau",
    "首付": "首期", "月供": "供屋 / 供车", "小区": "花园 / condo",
    "百分之": "巴仙", "干嘛": "做么", "咋": "怎样", "啥": "什么",
    "停水": "制水", "限水": "制水", "菜市场": "巴刹", "零钱": "散钱",
    "驾照": "礼申", "罚单": "saman", "大爷": "Uncle", "大妈": "Aunty",
    "小伙子": "年轻人", "房子": "屋子 / 屋", "一万": "十千", "购买": "买",
    "使用": "用", "非常": "很", "立刻": "马上",
}
PARTICLES = r"(?:啦|咯|咧|嘛|咩|啊|hor|lah|lor|leh|meh)"
SPOILERS = ["原来是因为", "原来他", "原来她", "也就是说", "换句话说",
            "其实是因为", "每次都会", "所以才会", "这就是为什么"]


def count_chars(text):
    """一个汉字算 1，一个英文词或一个数字算 2，标点不算。"""
    han = len(re.findall(r"[一-鿿]", text))
    words = len(re.findall(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*|\d[\d,\.]*", text))
    return han + words * 2


def parse_range(cell):
    nums = re.findall(r"\d+(?:\.\d+)?", cell)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    return None


def find_tables(lines):
    """找出所有表头同时有「秒数」和「台词」的表（剧本分成几段写也可以），
    回传 [(秒数那一格, 台词那一格, 整行文字), ...]。"""
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "|" in line and "秒数" in line and "台词" in line:
            head = [c.strip() for c in line.strip().strip("|").split("|")]
            ci_time = next(k for k, h in enumerate(head) if "秒数" in h)
            ci_line = next(k for k, h in enumerate(head) if "台词" in h)
            i += 2
            while i < len(lines) and "|" in lines[i]:
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(row) > max(ci_time, ci_line):
                    out.append((row[ci_time], row[ci_line], "".join(row)))
                i += 1
        else:
            i += 1
    return out


def spoken_parts(cell):
    """台词格里讲出口的部分。优先取「」里的；没有引号就去掉「名字：」当成一句。"""
    cell = re.sub(r"【[^】]*】", "", cell)  # 标签（【可删】【后制配音】）不是台词
    quotes = re.findall(r"「([^」]*)」", cell)
    if quotes:
        return quotes
    bare = re.sub(r"[（(][^）)]*[）)]", "", cell).strip()
    if not bare or set(bare) <= set("—-–· "):
        return []
    bare = re.sub(r"^[^：:]{1,8}[：:]", "", bare).strip()
    return [bare] if bare else []


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    text = open(sys.argv[1], encoding="utf-8").read()
    rows = find_tables(text.splitlines())
    if not rows:
        print("找不到剧本表：表头要有「秒数」和「台词」两栏。")
        return 1

    problems, hints = [], []
    total_chars, end_max, n_lines = 0, 0.0, 0
    first_checked = False
    streak = 0

    for label, cell, whole in rows:
        span = parse_range(label)
        quotes = spoken_parts(cell)
        spoken = "".join(quotes)
        post = "后制配音" in cell

        if span:
            end_max = max(end_max, span[1])
        if not quotes:
            streak = 0
            continue

        n = count_chars(spoken)
        total_chars += n
        n_lines += len(quotes)

        if not first_checked:
            first_checked = True
            first_n = count_chars(quotes[0])
            if first_n > FIRST_MAX:
                problems.append(f"第一句有 {first_n} 个字（上限 {FIRST_MAX}）：「{quotes[0]}」")

        if span and not post:
            dur = span[1] - span[0]
            rate = n / dur if dur > 0 else 99
            if rate > RATE_MAX:
                problems.append(
                    f"{label} 秒：{n} 个字塞在 {dur:g} 秒里（每秒 {rate:.1f} 个），讲不完，"
                    f"至少要 {n / RATE_TIGHT:.1f} 秒。「{spoken[:24]}」")
            elif rate > RATE_TIGHT:
                hints.append(
                    f"{label} 秒：{n} 个字、{dur:g} 秒（每秒 {rate:.1f} 个），很赶。「{spoken[:24]}」")

        for q in quotes:
            for bad, good in SWAP.items():
                if bad in q:
                    hints.append(f"{label} 秒：「{bad}」→ {good}。「{q[:24]}」")
            for sent in re.split(r"[。！？!?…]+", q):
                found = re.findall(PARTICLES, sent)
                if len(found) > 1:
                    hints.append(f"{label} 秒：一句里有 {len(found)} 个语气词。「{sent[:24]}」")
            for s in SPOILERS:
                if s in q:
                    hints.append(f"{label} 秒：可能把答案讲破（「{s}」）。「{q[:24]}」")

        if re.search(PARTICLES, spoken):
            streak += 1
            if streak == 3:
                hints.append(f"到 {label} 秒为止，连续三行台词都带语气词，留一行不带。")
        else:
            streak = 0

    print(f"台词 {n_lines} 句，共 {total_chars} 个字；表里最后一行到第 {end_max:g} 秒。")
    if end_max and end_max <= SHORT_MAX_SEC:
        print(f"短梗（{end_max:g} 秒）：全片上限 {SHORT_CHARS} 字。")
        if end_max > 33:
            hints.append(f"短梗到第 {end_max:g} 秒，超过 33 秒。先删标了【可删】的行。")
        if total_chars > SHORT_CHARS:
            problems.append(
                f"短梗台词太满：{total_chars} 字，上限 {SHORT_CHARS}。删句子，不要把秒数改小。")
    elif end_max:
        ratio = total_chars / end_max
        print(f"大片：全片每秒 {ratio:.2f} 个字（上限 {FILM_RATIO}）。")
        if ratio > FILM_RATIO:
            problems.append(
                f"全片台词太满：{total_chars} 字 ÷ {end_max:g} 秒 = {ratio:.2f}。"
                f"要删到 {int(end_max * FILM_RATIO)} 字以内。")

    print()
    if problems:
        print(f"要改的（{len(problems)}）：")
        for p in problems:
            print("  - " + p)
    else:
        print("时长：每一行都装得下。")
    if hints:
        print(f"\n看一下的（{len(hints)}）：")
        for h in hints:
            print("  - " + h)
    print("\n这支脚本只会算和找。讲不讲得通、有没有讲破、好不好笑，还是要自己从头读一次。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
