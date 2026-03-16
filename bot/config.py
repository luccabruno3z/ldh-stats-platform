"""Centralized configuration for the PR Stats Discord bot."""

# ── Base URL ──────────────────────────────────────────────────────────────────
BASE_URL = "https://luccabruno3z.github.io"

# ── URL builders ──────────────────────────────────────────────────────────────

def graph_url(clan: str) -> str:
    """Return the interactive chart URL for a given clan."""
    return f"{BASE_URL}/graphs/{clan}_interactive_chart.html"


def json_url(clan: str) -> str:
    """Return the players JSON URL for a given clan."""
    return f"{BASE_URL}/graphs/{clan}_players.json"


def all_players_url() -> str:
    """Return the URL for the combined all-players cluster JSON."""
    return f"{BASE_URL}/graphs/all_players_clusters.json"


def clan_averages_url() -> str:
    """Return the URL for the clan averages JSON."""
    return f"{BASE_URL}/graphs/clan_averages.json"


def history_url(player_name: str) -> str:
    """Return the URL for a player's history JSON (local path pattern)."""
    return f"graphs/history/{player_name}_history.json"


def all_players_graph_url() -> str:
    """Return the interactive chart URL for all players."""
    return f"{BASE_URL}/graphs/all_players_interactive_chart.html"


# ── Clan list ─────────────────────────────────────────────────────────────────
CLAN_NAMES = [
    "LDH", "SAE", "FI", "FI-R", "141", "R-LDH", "A-LDH",
    "WD", "300", "E-LAM", "RIM:LA", "ADG", "FASO", "PORN",
]

# ── Clan emojis (Discord custom emoji markup) ────────────────────────────────
CLAN_EMOJIS = {
    "LDH": "<a:Logo_LDH:1331795086169866290>",
    "SAE": "<:Logo_SAE:1330790573061312542>",
    "FI": "<:Logo_FI:1330790559601659924>",
    "FI-R": "<:Logo_FI:1330790559601659924>",
    "141": "<:Logo_141:emoji_id5>",
    "R-LDH": "<:Logo_R_LDH:1331795559291551877>",
    "A-LDH": "<:Logo_R_LDH:1331795559291551877>",
    "WD": "<:Logo_WD:emoji_id7>",
    "300": "<:Logo_300:1330790501460213770>",
    "E-LAM": "<:Logo_E_LAM:1330790544263217243>",
    "RIM:LA": "<:Logo_RIM_LA:1330790529214185472>",
    "ADG": "<a:Logo_ADG:1331778693949034516>",
    "FASO": "<:Logo_FASO:1344203061907689482>",
    "PORN": "",
}

# ── Flag emojis for timezone selection ────────────────────────────────────────
FLAG_EMOJIS = {
    "\U0001f1e6\U0001f1f7": "America/Argentina/Buenos_Aires",  # AR
    "\U0001f1f2\U0001f1fd": "America/Mexico_City",             # MX
    "\U0001f1ea\U0001f1f8": "Europe/Madrid",                   # ES
    "\U0001f1e8\U0001f1f1": "America/Santiago",                # CL
    "\U0001f1e8\U0001f1f4": "America/Bogota",                  # CO
    "\U0001f1f5\U0001f1ea": "America/Lima",                    # PE
    "\U0001f1fb\U0001f1ea": "America/Caracas",                 # VE
    "\U0001f1f5\U0001f1fe": "America/Asuncion",                # PY
    "\U0001f1fa\U0001f1fe": "America/Montevideo",              # UY
}

# ── Command prefix ────────────────────────────────────────────────────────────
COMMAND_PREFIX = "-"

# ── Performance score color thresholds ────────────────────────────────────────
# Returns a discord.Color; import discord where needed.
PERFORMANCE_THRESHOLDS = [
    (0.85, "gold"),
    (0.70, "green"),
    (0.50, "blue"),
    (0.30, "orange"),
]
# Anything below 0.30 -> red


def performance_color(score: float):
    """Return a discord.Color based on the performance score."""
    import discord
    for threshold, color_name in PERFORMANCE_THRESHOLDS:
        if score >= threshold:
            return getattr(discord.Color, color_name)()
    return discord.Color.red()


# ── Static page URLs ─────────────────────────────────────────────────────────
GITHUB_INDEX = BASE_URL
GITHUB_GUIDES = f"{BASE_URL}/#guias"
GITHUB_VISUALIZER_2D = f"{BASE_URL}/realitytracker.github.io/"

# ── Thumbnail ─────────────────────────────────────────────────────────────────
BOT_THUMBNAIL = f"{BASE_URL}/LDH_BOY2.png"

# ── Metric key mapping (user-facing name -> JSON key) ─────────────────────────
METRIC_KEY_MAP = {
    "performance": "Performance Score",
    "kd": "K/D Ratio",
    "kills": "Total Kills",
    "deaths": "Total Deaths",
    "rounds": "Rounds",
    "score": "Total Score",
}

# ── Valid categories for the top command (lowercase -> clan name) ──────────────
TOP_CATEGORIES = {
    "general": None,  # uses all_players_url()
    "ldh": "LDH",
    "sae": "SAE",
    "fi": "FI",
    "141": "141",
    "fi-r": "FI-R",
    "r-ldh": "R-LDH",
    "a-ldh": "A-LDH",
    "e-lam": "E-LAM",
    "300": "300",
    "rim-la": "RIM:LA",
    "adg": "ADG",
    "faso": "FASO",
    "porn": "PORN",
    "wd": "WD",
}

# ── Clan JSON URL map (uppercase) for sugerir_equipo ──────────────────────────
CLAN_JSON_MAP = {
    "LDH": json_url("LDH"),
    "SAE": json_url("SAE"),
    "FI": json_url("FI"),
    "FI-R": json_url("FI-R"),
    "141": json_url("141"),
    "R-LDH": json_url("R-LDH"),
    "A-LDH": json_url("A-LDH"),
    "WD": json_url("WD"),
    "300": json_url("300"),
    "E-LAM": json_url("E-LAM"),
    "RIM:LA": json_url("RIM:LA"),
    "ADG": json_url("ADG"),
    "FASO": json_url("FASO"),
    "PORN": json_url("PORN"),
}

# ── Graph alias mapping (command alias -> clan name) ──────────────────────────
# Used to register backward-compatible graficoldh, graficosae, etc.
GRAPH_ALIASES = {
    "graficoldh": "LDH",
    "graficosae": "SAE",
    "graficofi": "FI",
    "graficofi_r": "FI-R",
    "grafico141": "141",
    "graficor_ldh": "R-LDH",
    "graficoa_ldh": "A-LDH",
    "graficowd": "WD",
    "grafico300": "300",
    "graficoe_lam": "E-LAM",
    "graficorim_la": "RIM:LA",
    "graficoadg": "ADG",
    "graficofaso": "FASO",
    "graficoporn": "PORN",
}
