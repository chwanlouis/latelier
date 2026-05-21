import colorsys
import matplotlib.pyplot as plt
import numpy as np


def fast_hurwitz_zeta(s, q, terms=30):
    s = np.asarray(s, dtype=complex)
    output = np.zeros_like(s, dtype=complex)
    n = np.arange(terms)[:, None]
    q_expanded = q + n
    output = np.sum(1.0 / (q_expanded**s[None, :]), axis=0)
    return output


def generate_rainbow_zeta_egg(egg_size=1.0, dpi=150, save_path=None):
    L = 14.0 * egg_size
    B = 9.5 * egg_size
    a = 0.2
    res = 500

    x_bound = 7.0 * egg_size
    y_bound = 6.0 * egg_size

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

    img_rgba = np.ones((res, res, 4))
    phase = np.angle(Z_complex[mask])

    H = (phase + np.pi) / (2 * np.pi)
    S = np.ones_like(H)
    V = np.ones_like(H)

    distance_ratio = np.abs(Y[mask]) / (Y_edge[mask] + 1e-5)
    alpha = 1.0 - (distance_ratio**3)
    alpha = np.clip(alpha, 0.0, 1.0)

    rgb_colors = np.array(
        [colorsys.hsv_to_rgb(h, s, v) for h, s, v in zip(H, S, V)]
    )

    img_rgba[mask, :3] = rgb_colors
    img_rgba[mask, 3] = alpha
    img_rgba[~mask, 3] = 0.0

    fig, ax = plt.subplots(figsize=(8, 8), facecolor="white", dpi=dpi)
    ax.set_facecolor("white")

    ax.imshow(
        img_rgba,
        extent=[-x_bound, x_bound, -y_bound, y_bound],
        origin="lower",
        interpolation="bilinear",
        zorder=1,
    )

    ax.axis("equal")
    ax.axis("off")

    if save_path:
        plt.savefig(
            save_path,
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0,
            facecolor="white",
        )
        print(f"Successfully saved high-resolution art to: {save_path}")

    plt.show()


generate_rainbow_zeta_egg(egg_size=1.0, dpi=300, save_path="eggsize_1_dpi_300.png")
