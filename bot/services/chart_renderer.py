"""Matplotlib chart helpers with guaranteed plt.close() and dark theme."""

from contextlib import contextmanager
import io

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend; must be set before importing pyplot
import matplotlib.pyplot as plt


@contextmanager
def _chart_context(figsize=(10, 6)):
    """Context manager that yields (fig, ax) and always closes the figure."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=figsize)
    try:
        yield fig, ax
    finally:
        buf = None  # caller handles buf outside
        plt.close(fig)


def _save_to_buffer(fig) -> io.BytesIO:
    """Save figure to a BytesIO buffer and close it."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


# ── Public renderers ──────────────────────────────────────────────────────────

def render_bar_chart(
    labels: list[str],
    values: list[float],
    title: str,
    xlabel: str,
    ylabel: str,
) -> io.BytesIO:
    """Generic bar chart with dark theme. Returns BytesIO ready for discord.File."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))

    index = range(len(labels))
    bars = ax.bar(index, values, 0.5, label=ylabel)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(index)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()

    return _save_to_buffer(fig)


def render_kd_chart(
    player_names: list[str],
    kd_ratios: list[float],
    title: str,
) -> io.BytesIO:
    """Bar chart of K/D ratios with green bars, value labels, and grid."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))

    index = range(len(player_names))
    bars = ax.bar(index, kd_ratios, 0.5, color="#00FF00", edgecolor="white")

    ax.set_xlabel("Jugadores", color="white")
    ax.set_ylabel("K/D Ratio", color="white")
    ax.set_title(title, color="white")
    ax.set_xticks(index)
    ax.set_xticklabels(player_names, rotation=45, ha="right", color="white")
    ax.tick_params(axis="y", colors="white")
    ax.grid(axis="y", linestyle="--", color="gray")

    # Value labels on bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval + 0.01,
            f"{yval:.2f}",
            ha="center",
            color="white",
        )

    return _save_to_buffer(fig)


def render_comparison_chart(
    team1_name: str,
    team1_data: list[dict],
    team2_name: str,
    team2_data: list[dict],
) -> io.BytesIO:
    """Side-by-side K/D bar charts for two teams."""
    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 1, figsize=(12, 12))

    for ax, team_name, team_players in [
        (axes[0], team1_name, team1_data),
        (axes[1], team2_name, team2_data),
    ]:
        nombres = [p["Player"] for p in team_players]
        kd_ratios = [p["K/D Ratio"] for p in team_players]

        ax.bar(nombres, kd_ratios, color="#00FF00", edgecolor="white")
        ax.set_xlabel("Jugadores", color="white")
        ax.set_ylabel("K/D Ratio", color="white")
        ax.set_title(f"K/D Ratio de Jugadores - {team_name}", color="white")
        ax.tick_params(axis="x", rotation=45, colors="white")
        ax.tick_params(axis="y", colors="white")

        # Horizontal reference lines
        max_kd = max(kd_ratios) if kd_ratios else 1
        for y in range(0, int(max_kd) + 2):
            ax.axhline(y=y, color="gray", linestyle="--", linewidth=0.5)

    fig.tight_layout()
    return _save_to_buffer(fig)


def render_history_chart(
    player_name: str,
    dates: list[str],
    scores: list[float],
) -> io.BytesIO:
    """Line chart of historical performance scores."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(dates, scores, marker="o", color="#00FF00")
    ax.set_title(f"Performance Score Historico de {player_name}", color="white")
    ax.set_xlabel("Fecha", color="white")
    ax.set_ylabel("Performance Score", color="white")
    ax.tick_params(axis="x", rotation=45, colors="white")
    ax.tick_params(axis="y", colors="white")
    ax.grid(True, linestyle="--", color="gray")

    return _save_to_buffer(fig)
