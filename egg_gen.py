import colorsys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation


def fast_hurwitz_zeta(s, q, terms=30):
    s = np.asarray(s, dtype=complex)
    output = np.zeros_like(s, dtype=complex)
    n = np.arange(terms)[:, None]
    q_expanded = q + n
    output = np.sum(1.0 / (q_expanded ** s[None, :]), axis=0)
    return output


def generate_rainbow_zeta_egg(
        egg_size=1.0, dpi=150, save_path=None, bgcolor="white", text_str=None, text_color="auto"
):
    if (
            isinstance(bgcolor, str)
            and len(bgcolor) == 6
            and all(c in "0123456789abcdefABCDEF" for c in bgcolor)
    ):
        bgcolor = "#" + bgcolor

    L = 14.0 * egg_size
    B = 9.5 * egg_size
    a = 0.2
    res = 500

    x_bound = 7.0 * egg_size
    y_bound = 6.0 * egg_size

    y_lower_bound = y_bound + (2.0 * egg_size if text_str else 0.0)

    x = np.linspace(-x_bound, x_bound, res)
    y = np.linspace(-y_bound, y_bound, res)
    X, Y = np.meshgrid(x, y)

    inside = np.abs(X) <= L / 2
    Y_edge = np.zeros_like(X)
    Y_edge[inside] = (B / 2) * np.sqrt(1 - (2 * X[inside] / L) ** 2) * (
            1 + a * (X[inside] / (L / 2))
    )
    mask = np.abs(Y) <= Y_edge

    Sigma = X / egg_size
    Time = Y / egg_size
    q_param = 0.35

    Z_complex = np.zeros(X.shape, dtype=complex)
    complex_pts = Sigma[mask] + 1j * Time[mask]

    Z_complex[mask] = fast_hurwitz_zeta(complex_pts, q_param)

    bg_rgb = np.array(plt.cm.colors.to_rgb(bgcolor))

    img_rgba = np.ones((res, res, 4))
    img_rgba[:, :, :3] = bg_rgb

    phase = np.angle(Z_complex[mask])

    H = (phase + np.pi) / (2 * np.pi)
    S = np.ones_like(H)
    V = np.ones_like(H)

    distance_ratio = np.abs(Y[mask]) / (Y_edge[mask] + 1e-5)
    alpha = 1.0 - (distance_ratio ** 3)
    alpha = np.clip(alpha, 0.0, 1.0)

    rgb_colors = np.array(
        [colorsys.hsv_to_rgb(h, s, v) for h, s, v in zip(H, S, V)]
    )

    img_rgba[mask, :3] = (
            rgb_colors * alpha[:, None] + bg_rgb * (1.0 - alpha[:, None])
    )

    fig, ax = plt.subplots(figsize=(8, 8), facecolor="white", dpi=dpi)
    fig.patch.set_facecolor(bgcolor)
    ax.set_facecolor(bgcolor)

    ax.imshow(
        img_rgba,
        extent=[-x_bound, x_bound, -y_bound, y_bound],
        origin="lower",
        interpolation="bilinear",
        zorder=1,
    )

    if text_str:
        if text_color == "auto":
            brightness = 0.299 * bg_rgb[0] + 0.587 * bg_rgb[1] + 0.114 * bg_rgb[2]
            final_text_color = "black" if brightness > 0.5 else "white"
        else:
            final_text_color = text_color

        # 關鍵修改：字型大小 (fontsize) 會隨著 egg_size 縮放，14 是預設的基礎字級大小
        dynamic_fontsize = 20 * egg_size

        ax.text(
            0, -y_bound - (1.2 * egg_size), text_str,
            color=final_text_color, fontsize=dynamic_fontsize, fontweight="bold",
            ha="center", va="top", zorder=2
        )

    ax.set_xlim(-x_bound, x_bound)
    ax.set_ylim(-y_lower_bound, y_bound)
    ax.set_aspect("equal")
    ax.axis("off")

    if save_path:
        plt.savefig(
            save_path,
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.2 if text_str else 0,
            facecolor=bgcolor,
        )
        print(f"Successfully saved high-resolution art to: {save_path}")

    plt.show()


def generate_zeta_egg_gif(
    egg_size=1.0,
    dpi=100,
    save_path="zeta_egg_animation.gif",
    bgcolor="white",
    text_str=None,
    text_color="auto",
    frames=60,
):
    if (
        isinstance(bgcolor, str)
        and len(bgcolor) == 6
        and all(c in "0123456789abcdefABCDEF" for c in bgcolor)
    ):
        bgcolor = "#" + bgcolor

    L = 14.0 * egg_size
    B = 9.5 * egg_size
    a = 0.2
    res = 400

    x_bound = 7.0 * egg_size
    y_bound = 6.0 * egg_size
    y_lower_bound = y_bound + (2.0 * egg_size if text_str else 0.0)

    x = np.linspace(-x_bound, x_bound, res)
    y = np.linspace(-y_bound, y_bound, res)
    X, Y = np.meshgrid(x, y)

    inside = np.abs(X) <= L / 2
    Y_edge = np.zeros_like(X)
    Y_edge[inside] = (B / 2) * np.sqrt(1 - (2 * X[inside] / L) ** 2) * (
        1 + a * (X[inside] / (L / 2))
    )
    mask = np.abs(Y) <= Y_edge

    Sigma = X / egg_size
    Time = Y / egg_size
    q_param = 0.35

    Z_complex = np.zeros(X.shape, dtype=complex)
    complex_pts = Sigma[mask] + 1j * Time[mask]
    Z_complex[mask] = fast_hurwitz_zeta(complex_pts, q_param)

    bg_rgb = np.array(plt.cm.colors.to_rgb(bgcolor))
    phase_base = np.angle(Z_complex[mask])

    distance_ratio = np.abs(Y[mask]) / (Y_edge[mask] + 1e-5)
    alpha = 1.0 - (distance_ratio**3)
    alpha = np.clip(alpha, 0.0, 1.0)

    fig, ax = plt.subplots(figsize=(6, 6), facecolor=bgcolor, dpi=dpi)
    ax.set_facecolor(bgcolor)

    img_rgba = np.ones((res, res, 4))
    img_rgba[:, :, :3] = bg_rgb
    im = ax.imshow(
        img_rgba,
        extent=[-x_bound, x_bound, -y_bound, y_bound],
        origin="lower",
        interpolation="bilinear",
        zorder=1,
    )

    if text_str:
        if text_color == "auto":
            brightness = 0.299 * bg_rgb[0] + 0.587 * bg_rgb[1] + 0.114 * bg_rgb[2]
            final_text_color = "black" if brightness > 0.5 else "white"
        else:
            final_text_color = text_color
        dynamic_fontsize = 12 * egg_size
        ax.text(
            0,
            -y_bound - (1.2 * egg_size),
            text_str,
            color=final_text_color,
            fontsize=dynamic_fontsize,
            fontweight="bold",
            ha="center",
            va="top",
            zorder=2,
        )

    ax.set_xlim(-x_bound, x_bound)
    ax.set_ylim(-y_lower_bound, y_bound)
    ax.set_aspect("equal")
    ax.axis("off")

    # 動態更新影格的函式
    def update(frame):
        # 計算這一格的時間偏移量（平滑分攤 2*pi 以達成無縫循環）
        time_shift = 2.0 * np.pi * (frame / frames)
        shifted_phase = (phase_base + time_shift + np.pi) % (2 * np.pi) - np.pi

        H = (shifted_phase + np.pi) / (2 * np.pi)
        S = np.ones_like(H)
        V = np.ones_like(H)

        rgb_colors = np.array(
            [colorsys.hsv_to_rgb(h, s, v) for h, s, v in zip(H, S, V)]
        )

        frame_rgba = np.ones((res, res, 4))
        frame_rgba[:, :, :3] = bg_rgb
        frame_rgba[mask, :3] = (
            rgb_colors * alpha[:, None] + bg_rgb * (1.0 - alpha[:, None])
        )
        frame_rgba[~mask, 3] = 0.0

        im.set_data(frame_rgba)
        return [im]

    print("正在生成動畫影格並導出 GIF，請稍候...")
    ani = animation.FuncAnimation(
        fig, update, frames=frames, interval=50, blit=True
    )

    # 儲存為 GIF 檔案（電腦必須安裝 pillow 庫，通常已有內建）
    ani.save(save_path, writer="pillow", fps=20, savefig_kwargs={"facecolor": bgcolor})
    print(f"動態彩虹蛋已成功儲存至: {save_path}")
    plt.close()




if __name__ == "__main__":
    egg_size = 1.0
    dpi = 300
    text_str = "Project L'atelier"
    colors = ["white", "black", "#1e1e24", "#1e1e24", "#141419", "#2a2a33", "#3a3a45", "#2f3542"]
    for color in colors:
        file_name = f"eggsize_{egg_size}_dpi_{dpi}_bg_{color}.png"
        generate_rainbow_zeta_egg(
            egg_size=egg_size, dpi=dpi, bgcolor=color, save_path=file_name
        )
    # generate_zeta_egg_gif(
    #     egg_size=1.0,
    #     dpi=100,
    #     bgcolor="1e1e24",
    #     text_str=text_str,
    #     save_path="zeta_egg_wave.gif",
    #     frames=180,
    # )
