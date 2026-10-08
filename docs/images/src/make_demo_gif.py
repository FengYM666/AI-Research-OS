#!/usr/bin/env python3
# 生成 README 演示 GIF：真实检索记录的终端重放（数据来自 2026-10-08 OpenAlex 实查，非编造）
# 用法: python make_demo_gif.py   （输出到上级目录 demo-anti-hallucination.gif）
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 880, 560
FPS = 10
BG = (20, 20, 31)
BAR = (30, 30, 46)
FG = (214, 214, 224)
DIM = (139, 139, 158)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
CYAN = (103, 232, 249)
YELLOW = (250, 204, 21)
PURPLE = (167, 139, 250)

F_CN = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 17)
F_URL = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 15)
F_SYM = ImageFont.truetype(r"C:\Windows\Fonts\seguisym.ttf", 17)

# 每行 = [(text, font, color), ...]；出现时机由 SCENES 控制
PROMPT = "帮我找 3D Gaussian Splatting 压缩方向的顶会论文，要有代码的"

L_QUERY = [("  query: ", F_CN, DIM), ('"3D Gaussian Splatting compression"', F_URL, CYAN),
           ("  → 6 条真实记录命中", F_CN, DIM)]
L_BLOCK = [("✗ ", F_SYM, RED), ("拦截：记忆候选 ", F_CN, RED), ('"Compact3DGS"', F_URL, DIM),
           (" 不在本轮结果中 → 不采信", F_CN, RED)]
L_R1 = [("✓ ", F_SYM, GREEN), ("HAC: Hash-Grid Assisted Context for 3DGS Compression", F_URL, FG)]
L_R1M = [("     Chen, Wu, Lin, Harandi, Cai · 2024 · 被引 108", F_CN, DIM)]
L_R1U = [("     doi.org/10.1007/978-3-031-72667-5_24", F_URL, CYAN)]
L_R2 = [("✓ ", F_SYM, GREEN), ("FCGS: Fast Feedforward 3DGS Compression", F_URL, FG)]
L_R2M = [("     Chen, Wu, Li, Lin, Harandi, Cai · arXiv 2410.08017 · 有代码", F_CN, DIM)]
L_R2U = [("     github.com/YihangChen-ee/FCGS", F_URL, CYAN)]
L_R3 = [("✓ ", F_SYM, GREEN), ("3DGS.zip: A Survey on 3DGS Compression Methods", F_URL, FG)]
L_R3M = [("     Bagdasarian et al. · CGF 2025 · 被引 41", F_CN, DIM)]
L_R3U = [("     doi.org/10.1111/cgf.70078", F_URL, CYAN)]
L_FIN = [("✓ ", F_SYM, GREEN), ("五要素同源核对：标题 / 作者 / 年份 / venue / 链接", F_CN, GREEN)]
L_FIN2 = [("  检索式已附上 · 查不到就明说，绝不凭记忆编造", F_CN, DIM)]

LH = 30          # 行高
X0, Y0 = 36, 76

def draw_frame(shown, spinner_char, cursor):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # 终端标题栏
    d.rectangle([0, 0, W, 40], fill=BAR)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([18 + i * 26, 13, 30 + i * 26, 25], fill=c)
    d.text((W // 2 - 120, 9), "agent — paper-search", font=F_CN, fill=DIM)
    y = Y0
    for line, flag in shown:
        x = X0
        for text, font, color in line:
            d.text((x, y), text, font=font, fill=color)
            x += int(d.textlength(text, font=font))
        if flag == "cursor":
            d.rectangle([x + 2, y + 2, x + 12, y + 24], fill=FG)
        y += LH
    if spinner_char:
        d.text((X0, y), spinner_char, font=F_CN, fill=YELLOW)
    return img

frames, durations = [], []

def hold(n, shown, spinner=None, cursor=False, ms=100):
    for _ in range(n):
        frames.append(draw_frame(shown, spinner, cursor))
        durations.append(ms)

# 场景 1：逐字输入提问
partial = []
for i in range(4, len(PROMPT) + 1, 3):
    partial.append([([("❯ ", F_SYM, PURPLE), (PROMPT[:i], F_CN, FG)], "cursor")])
    hold(1, partial[-1], cursor=True)
hold(8, partial[-1], cursor=True)

# 场景 2：检索中（spinner 转动，└─ 单独一行）
prompt_line = partial[-1][0][0]
searching = [(prompt_line, None), ([("└─ paper-search MCP · OpenAlex 检索中…", F_CN, DIM)], None)]
for sp in ["|", "/", "-", "\\"] * 2:
    hold(1, searching, spinner=sp)

# 场景 3：命中 + 拦截
shown = searching + [(L_QUERY, None)]
hold(8, shown)
shown = shown + [(L_BLOCK, None)]
hold(10, shown)

# 场景 4：三条真实结果逐块出现
for blk in [[L_R1, L_R1M, L_R1U], [L_R2, L_R2M, L_R2U], [L_R3, L_R3M, L_R3U]]:
    shown = shown + [(l, None) for l in blk]
    hold(9, shown)

# 场景 5：结尾核对 + 光标闪烁
shown = shown + [(L_FIN, None), (L_FIN2, None)]
hold(6, shown)
hold(6, shown, cursor=True)
hold(6, shown)
hold(6, shown, cursor=True)

out = Path(__file__).resolve().parent.parent / "demo-anti-hallucination.gif"
frames[0].save(
    out, save_all=True, append_images=frames[1:], duration=durations, loop=0,
    optimize=True,
)
size_kb = out.stat().st_size / 1024
print(f"OK {out}  {len(frames)} frames  {size_kb:.0f} KB")
