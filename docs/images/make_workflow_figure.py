# 生成 README 的科研工作流全景图（浅色 + 深色双版本）
# 运行：python make_workflow_figure.py
# 输出：research-workflow-light.png / research-workflow-dark.png
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patheffects as pe

plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["font.monospace"] = "Consolas"

STAGES = [
    ("定方向",   "TOPIC",      "/phd-skills:gaps"),
    ("查文献",   "LITERATURE", "paper-search MCP"),
    ("复现",     "REPRODUCE",  "reproduce"),
    ("跑实验",   "EXPERIMENTS", "launch · compare · debug"),
    ("画图",     "VISUALIZE",  "scientific-visualization"),
    ("写论文",   "WRITE",      "research-paper-writing"),
    ("投稿防守", "DEFEND",     "fortify · factcheck"),
]

# 靛→紫的七色渐进
HUES = ["#5B6ABF", "#4C8DDA", "#3FA7A3", "#5FA55A", "#D9A441", "#D47B4C", "#9B6BB3"]


def mix(hex_color, target, t):
    """按 t 比例向 target 混色（t=0 原色，t=1 target）。"""
    c = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    tg = [int(target[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a + (b - a) * t):02X}" for a, b in zip(c, tg))


def draw(theme):
    light = theme == "light"
    bg = "#FFFFFF" if light else "#0D1117"
    text_main = "#1F2328" if light else "#E6EDF3"
    text_sub = "#6E7781" if light else "#9DA7B3"
    arrow_color = "#8B949E" if light else "#6E7681"

    fig, ax = plt.subplots(figsize=(14.6, 3.55), dpi=200)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 24)
    ax.axis("off")

    bw, bh, y0 = 12.0, 13.0, 5.0
    gap = (100 - 7 * bw) / 8.0
    cy = y0 + bh / 2

    for i, ((zh, en, tool), hue) in enumerate(zip(STAGES, HUES)):
        x = gap + i * (bw + gap)
        cx = x + bw / 2

        if light:
            fill, edge, num_fg = mix(hue, "#FFFFFF", 0.86), hue, "#FFFFFF"
        else:
            fill, edge, num_fg = mix(hue, "#0D1117", 0.72), mix(hue, "#FFFFFF", 0.35), "#0D1117"

        # 柔和投影
        shadow = FancyBboxPatch(
            (x + 0.35, y0 - 0.5), bw, bh,
            boxstyle="round,pad=0,rounding_size=1.4",
            facecolor="#000000", edgecolor="none", alpha=0.10 if light else 0.25, zorder=1,
        )
        ax.add_patch(shadow)

        box = FancyBboxPatch(
            (x, y0), bw, bh,
            boxstyle="round,pad=0,rounding_size=1.4",
            facecolor=fill, edgecolor=edge, linewidth=1.6, zorder=2,
        )
        ax.add_patch(box)

        # 顶部序号圆
        num_bg = edge if light else mix(hue, "#FFFFFF", 0.35)
        ax.add_patch(Circle((cx, y0 + bh), 1.75, facecolor=num_bg, edgecolor=bg,
                            linewidth=1.6, zorder=4))
        ax.text(cx, y0 + bh, str(i + 1), ha="center", va="center",
                fontsize=11, fontweight="bold", color=num_fg, zorder=5)

        ax.text(cx, cy + 2.6, zh, ha="center", va="center", fontsize=15,
                fontweight="bold", color=text_main, zorder=5)
        ax.text(cx, cy - 0.5, en, ha="center", va="center", fontsize=8.5,
                color=text_sub, zorder=5)
        ax.text(cx, cy - 3.6, tool, ha="center", va="center", fontsize=7.2,
                family="monospace", color=text_sub, zorder=5)

        if i < 6:
            ax.add_patch(FancyArrowPatch(
                (x + bw + 0.25, cy), (x + bw + gap - 0.25, cy),
                arrowstyle="-|>", mutation_scale=17, linewidth=1.8,
                color=arrow_color, connectionstyle="arc3,rad=-0.18", zorder=3,
            ))

    fig.savefig(f"research-workflow-{theme}.png", facecolor=bg,
                bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print(f"research-workflow-{theme}.png done")


if __name__ == "__main__":
    draw("light")
    draw("dark")
