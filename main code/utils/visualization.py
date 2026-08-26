import os
import sys
import logging
from collections.abc import Sequence
from typing import Any

import matplotlib
import matplotlib.pyplot as plt

# Probe for a GUI backend that actually works (creating a figure loads the DLL);
# if none do, fall back to Agg and export the run to a file instead of a window.
INTERACTIVE_BACKEND = None
for _backend in ("TkAgg", "QtAgg", "Qt5Agg"):
    try:
        matplotlib.use(_backend, force=True)
        _probe = plt.figure()
        plt.close(_probe)
        INTERACTIVE_BACKEND = _backend
        break
    except Exception:
        continue

if INTERACTIVE_BACKEND is None:
    matplotlib.use("Agg", force=True)

import numpy as np
import matplotlib.animation as animation
from matplotlib.patches import Patch
from matplotlib.widgets import Button
from config import REWARDS

# Emoji glyphs need a fallback font on Windows (DejaVu Sans has none)
if sys.platform == "win32":
    plt.rcParams["font.family"] = ["DejaVu Sans", "Segoe UI Emoji", "Segoe UI Symbol"]

# Silence harmless findfont "bold not found" chatter from the emoji fonts
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

# ---------- Theme ----------
THEME = {
    "fig_bg":     "#0f172a",   # deep navy
    "panel_bg":   "#1e293b",   # slate
    "text":       "#e2e8f0",   # light slate
    "accent":     "#38bdf8",   # sky blue
    "goal":       "#22c55e",   # green
    "crater":     "#dc2626",   # red
    "lava":       "#f97316",   # orange
    "gas":        "#eab308",   # yellow
    "safe":       "#334155",   # dark slate cell
    "grid_line":  "#0f172a",
    "agent":      "#f43f5e",   # rose
}


def _calculate_reward_breakdown(
    env: Any, path: Sequence[tuple[int, int]]
) -> tuple[int, int, int, int]:
    """Calculate an additive mission-reward breakdown.

    Every movement costs ``REWARDS["step"]``. Hazard values are additional
    penalties, and the goal value is an additional completion reward.
    """
    total_steps = max(len(path) - 1, 0)
    step_costs = total_steps * int(REWARDS["step"])
    hazard_values = {
        REWARDS["crater"],
        REWARDS["lava_close"],
        REWARDS["gas"],
    }
    hazard_penalties = 0

    for x, y in path:
        cell_value = env.get_cell(x, y)
        if cell_value in hazard_values:
            hazard_penalties += int(cell_value)

    goal_reward = 0
    if path and env.get_cell(*path[-1]) == REWARDS["goal"]:
        goal_reward = int(REWARDS["goal"])

    total_reward = goal_reward + step_costs + hazard_penalties
    return goal_reward, step_costs, hazard_penalties, total_reward


def _style_axis(ax):
    """Apply dark theme styling to an axis"""
    ax.set_facecolor(THEME["panel_bg"])
    ax.tick_params(colors=THEME["text"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(THEME["text"])
        spine.set_alpha(0.3)
    ax.xaxis.label.set_color(THEME["text"])
    ax.yaxis.label.set_color(THEME["text"])
    ax.title.set_color(THEME["text"])


def _center_window(fig):
    """Center the figure window on the screen (Tk and Qt backends)"""
    try:
        mgr = fig.canvas.manager
        backend = plt.get_backend().lower()
        if 'tk' in backend:
            win = mgr.window
            win.update_idletasks()
            sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
            w, h = win.winfo_width(), win.winfo_height()
            win.geometry(f"+{max((sw - w) // 2, 0)}+{max((sh - h) // 2, 0)}")
        elif 'qt' in backend:
            win = mgr.window
            frame = win.frameGeometry()
            frame.moveCenter(win.screen().availableGeometry().center())
            win.move(frame.topLeft())
    except Exception:
        pass  # unknown backend — window stays at default position


def _open_file(path):
    """Open a saved file in the OS default viewer"""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')
    except Exception:
        pass


def _save_gif(fig, out):
    """Render the stashed animation to a GIF with a long first-frame hold."""
    from PIL import Image

    update = fig._anim_update
    n = fig._anim_move_frames
    hold_start_s, hold_end_s = fig._anim_hold
    fast_ms = max(1, int(round(1000.0 / fig._anim_fps)))

    target_w = 900           # cap width so the GIF stays a reasonable size
    frames, durations = [], []
    for i in range(n):
        update(i)
        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(buf, "RGBA").convert("RGB")
        if img.width > target_w:
            h = int(img.height * target_w / img.width)
            img = img.resize((target_w, h), Image.LANCZOS)
        frames.append(img)
        durations.append(fast_ms)

    durations[0] = int(hold_start_s * 1000)     # 5 s pause before it starts
    durations[-1] = int(hold_end_s * 1000)      # linger on the finished path

    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=2)


def _export_and_prompt(fig, path, animate):
    """No GUI backend: render to a file, open it, and ask about rerunning."""
    out_dir = os.getcwd()
    out = None

    # Prefer an animated GIF; fall back to a static PNG if the GIF writer fails
    if animate and path is not None and len(path) > 1 and hasattr(fig, "_anim_update"):
        try:
            gif = os.path.join(out_dir, "simulation.gif")
            _save_gif(fig, gif)
            out = gif
        except Exception:
            out = None

    if out is None:
        try:
            png = os.path.join(out_dir, "simulation.png")
            fig.savefig(png, dpi=110, facecolor=fig.get_facecolor())
            out = png
        except Exception as e:
            print(f"\n⚠️  Could not save the visualization: {e}")
            plt.close(fig)
            return 'no'

    plt.close(fig)
    print("\n" + "-" * 60)
    print("🖼️  The interactive window is blocked on this machine")
    print("    (the Tk GUI backend is disabled by an Application Control policy).")
    print(f"    Saved the result instead → {out}")
    print("    (Opening it in your default viewer now.)")
    print("-" * 60)
    _open_file(out)

    try:
        answer = input("\nRun another simulation? (y/N): ").strip().lower()
        return 'yes' if answer in ('y', 'yes') else 'no'
    except Exception:
        return 'no'


def _hex_to_rgb(h):
    h = h.lstrip('#')
    return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]


def plot_grid(env, path=None, animate=False, value_func=None, policy=None):
    """Enhanced visualization with policy arrows, value heatmap and smooth animation"""
    grid = env.grid
    fig = plt.figure(figsize=(18, 7.5))
    fig.set_facecolor(THEME["fig_bg"])

    fig.suptitle('🌋 Volcano Grid World — MDP Value Iteration',
                 fontsize=17, fontweight='bold', y=0.97, color=THEME["text"])

    # ---------- Middle panel: Grid world with policy ----------
    ax = plt.subplot(1, 3, 2)
    _style_axis(ax)

    colored_grid = np.zeros((env.size, env.size, 3))
    for i in range(env.size):
        for j in range(env.size):
            val = grid[i][j]
            if val == REWARDS["goal"]:
                colored_grid[i, j] = _hex_to_rgb(THEME["goal"])
            elif val == REWARDS["crater"]:
                colored_grid[i, j] = _hex_to_rgb(THEME["crater"])
            elif val == REWARDS["lava_close"]:
                colored_grid[i, j] = _hex_to_rgb(THEME["lava"])
            elif val == REWARDS["gas"]:
                colored_grid[i, j] = _hex_to_rgb(THEME["gas"])
            else:
                colored_grid[i, j] = _hex_to_rgb(THEME["safe"])

    ax.imshow(colored_grid)

    # Crisp cell borders
    ax.set_xticks(np.arange(-.5, env.size, 1), minor=True)
    ax.set_yticks(np.arange(-.5, env.size, 1), minor=True)
    ax.grid(which='minor', color=THEME["grid_line"], linewidth=1.6)
    ax.tick_params(which='minor', length=0)

    # Hazard / goal icons
    for i in range(env.size):
        for j in range(env.size):
            val = grid[i][j]
            if val == REWARDS["goal"]:
                ax.text(j, i, '🎯', ha='center', va='center', fontsize=13)
            elif val == REWARDS["crater"]:
                ax.text(j, i, '💥', ha='center', va='center', fontsize=13)
            elif val == REWARDS["lava_close"]:
                ax.text(j, i, '🔥', ha='center', va='center', fontsize=13)
            elif val == REWARDS["gas"]:
                ax.text(j, i, '☁️', ha='center', va='center', fontsize=11)

    legend_elements = [
        Patch(facecolor=THEME["goal"],   label=f'🎯 Goal  +{REWARDS["goal"]}'),
        Patch(facecolor=THEME["crater"], label=f'💥 Crater  {REWARDS["crater"]}'),
        Patch(facecolor=THEME["lava"],   label=f'🔥 Lava  {REWARDS["lava_close"]}'),
        Patch(facecolor=THEME["gas"],    label=f'☁️ Gas  {REWARDS["gas"]}'),
        Patch(facecolor=THEME["safe"],   label=f'Safe Step  {REWARDS["step"]}'),
    ]
    leg = fig.legend(handles=legend_elements, loc='lower center',
                     bbox_to_anchor=(0.5, 0.115), ncol=5, fontsize=10,
                     facecolor=THEME["panel_bg"], edgecolor=THEME["accent"],
                     framealpha=0.9, columnspacing=1.6, handlelength=1.4)
    leg.get_frame().set_linewidth(0.8)
    for t in leg.get_texts():
        t.set_color(THEME["text"])

    # Policy arrows on safe cells
    if policy is not None:
        arrow_labels = {0: '↑', 1: '↓', 2: '←', 3: '→'}
        hazard_vals = [REWARDS["goal"], REWARDS["crater"], REWARDS["lava_close"], REWARDS["gas"]]
        for i in range(env.size):
            for j in range(env.size):
                if grid[i][j] not in hazard_vals:
                    ax.text(j, i, arrow_labels[policy[i][j]], ha='center', va='center',
                            fontsize=13, fontweight='bold', color=THEME["accent"], alpha=0.75)

    ax.set_title('Grid World — Optimal Policy', fontsize=12, fontweight='bold',
                 pad=10, loc='center', color=THEME["text"])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    # ---------- Right panel: Value heatmap ----------
    if value_func is not None:
        ax2 = plt.subplot(1, 3, 3)
        _style_axis(ax2)

        heatmap = np.copy(value_func)

        im2 = ax2.imshow(heatmap, cmap='RdYlGn', interpolation='nearest')
        for i in range(env.size):
            for j in range(env.size):
                ax2.text(j, i, f'{heatmap[i, j]:.0f}',
                         ha="center", va="center", color="black", fontsize=7)

        ax2.set_title('Value Function Heatmap', fontsize=12, fontweight='bold',
                      pad=10, color=THEME["text"])
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        cbar = plt.colorbar(im2, ax=ax2)
        cbar.set_label('Value', color=THEME["text"])
        cbar.ax.tick_params(colors=THEME["text"])
        cbar.outline.set_edgecolor(THEME["text"])
        cbar.outline.set_alpha(0.3)

    # ---------- Left panel: Performance summary ----------
    if path is not None:
        ax3 = plt.subplot(1, 3, 1)
        ax3.axis('off')

        start_pos = path[0]
        end_pos = path[-1]
        total_steps = len(path) - 1

        end_cell_value = env.get_cell(end_pos[0], end_pos[1])
        mission_status = "✓ Completed" if end_cell_value == REWARDS["goal"] else "✗ Failed"

        goal_reward, step_costs, hazard_penalties, total_reward = (
            _calculate_reward_breakdown(env, path)
        )

        goal_pos = None
        for i in range(env.size):
            for j in range(env.size):
                if env.get_cell(i, j) == REWARDS["goal"]:
                    goal_pos = (i, j)
                    break

        summary_text = f"""
OVERALL PERFORMANCE
{'─' * 24}

Start Position:
   ({start_pos[0]}, {start_pos[1]})

Goal Position:
   {f"({goal_pos[0]}, {goal_pos[1]})" if goal_pos else "Unknown"}

Total Steps (Path Length):
   {total_steps} steps

Reward Breakdown:
   • Goal Reward:      +{goal_reward}
   • Step Cost:        {step_costs}
   • Hazard Penalty:   {hazard_penalties}
   • Total Reward:     {total_reward}

Mission Status:
   {mission_status}
"""
        ax3.text(0.05, 0.92, summary_text, transform=ax3.transAxes,
                 fontsize=11, verticalalignment='top', fontfamily='monospace',
                 color=THEME["text"],
                 bbox=dict(boxstyle='round,pad=0.8', facecolor=THEME["panel_bg"],
                           edgecolor=THEME["accent"], linewidth=1.2, alpha=0.95))

    if path is None:
        plt.tight_layout()
        if not INTERACTIVE_BACKEND:
            return _export_and_prompt(fig, None, False)
        _center_window(fig)
        plt.show()
        return None

    # ---------- Smooth animation ----------
    if animate and len(path) > 1:
        FRAMES_PER_STEP = 3      # sub-frames per cell move (fewer = faster)
        MOVE_INTERVAL = 18       # ms between movement frames (smaller = faster)
        FAST_FPS = 32            # GIF playback speed of the movement
        HOLD_START_S = 5.0       # pause on the start state before moving
        HOLD_END_S = 2.5         # linger on the finished path before looping

        n_moves = len(path) - 1
        move_frames = n_moves * FRAMES_PER_STEP + 1

        trail, = ax.plot([], [], color=THEME["accent"], linewidth=3, alpha=0.9,
                         solid_capstyle='round', zorder=4)
        halo, = ax.plot([], [], 'o', markersize=24, color=THEME["agent"],
                        alpha=0.25, zorder=5)
        agent, = ax.plot([], [], 'o', markersize=12, color=THEME["agent"],
                         markeredgecolor='white', markeredgewidth=1.5, zorder=6)
        step_text = ax.text(1.0, 1.02, '', transform=ax.transAxes, fontsize=10,
                            fontweight='bold', color=THEME["accent"],
                            va='bottom', ha='right')

        def update(frame):
            seg = min(frame // FRAMES_PER_STEP, n_moves - 1)
            t = (frame - seg * FRAMES_PER_STEP) / FRAMES_PER_STEP
            t = min(t, 1.0)
            t = t * t * (3 - 2 * t)  # ease in-out for smooth start/stop

            x0, y0 = path[seg]
            x1, y1 = path[seg + 1]
            cx = x0 + (x1 - x0) * t
            cy = y0 + (y1 - y0) * t

            xs = [p[1] for p in path[:seg + 1]] + [cy]
            ys = [p[0] for p in path[:seg + 1]] + [cx]
            trail.set_data(xs, ys)
            agent.set_data([cy], [cx])
            halo.set_data([cy], [cx])
            step_text.set_text(f'Step {seg + (1 if t >= 1 else 0)} / {n_moves}')
            return trail, agent, halo, step_text

        # Stash what the GIF exporter needs to rebuild the animation
        fig._anim_update = update
        fig._anim_move_frames = move_frames
        fig._anim_fps = FAST_FPS
        fig._anim_hold = (HOLD_START_S, HOLD_END_S)

        update(0)  # draw the start state (held for HOLD_START_S)

        if INTERACTIVE_BACKEND:
            hold_frames = int(HOLD_START_S * 1000 / MOVE_INTERVAL)

            def update_with_hold(frame):
                return update(max(0, frame - hold_frames))  # hold, then move

            fig._ani = animation.FuncAnimation(
                fig, update_with_hold,
                frames=hold_frames + move_frames,
                interval=MOVE_INTERVAL, blit=False, repeat=False
            )
        plt.tight_layout()

    else:
        xs = [p[1] for p in path]
        ys = [p[0] for p in path]
        ax.plot(xs, ys, color=THEME["accent"], linewidth=2.5, label='Path')
        ax.plot(xs[0], ys[0], 'o', color=THEME["goal"], markersize=12, label='Start')
        ax.plot(xs[-1], ys[-1], '*', color=THEME["agent"], markersize=20, label='End')
        plt.tight_layout()

    plt.subplots_adjust(top=0.87, bottom=0.20)

    # No GUI backend → export to a file and prompt on the console instead.
    if not INTERACTIVE_BACKEND:
        return _export_and_prompt(fig, path, animate)

    # ---------- Restart / Exit buttons (interactive window) ----------
    restart_choice = {'value': None}

    def on_restart(event):
        restart_choice['value'] = 'yes'
        plt.close()

    def on_exit(event):
        restart_choice['value'] = 'no'
        plt.close()

    ax_restart = plt.axes([0.3, 0.04, 0.15, 0.06])
    ax_exit = plt.axes([0.55, 0.04, 0.15, 0.06])

    btn_restart = Button(ax_restart, '🔄 Restart', color=THEME["accent"], hovercolor='#7dd3fc')
    btn_exit = Button(ax_exit, '❌ Exit', color=THEME["agent"], hovercolor='#fb7185')
    btn_restart.label.set_fontweight('bold')
    btn_exit.label.set_fontweight('bold')

    btn_restart.on_clicked(on_restart)
    btn_exit.on_clicked(on_exit)

    _center_window(fig)
    plt.show()
    return restart_choice['value']
