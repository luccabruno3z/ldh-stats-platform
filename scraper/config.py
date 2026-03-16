"""Configuration for the PR Stats scraper."""

CLAN_URLS = {
    "LDH": "https://prstats.realitymod.com/clan/11204/ldh",
    "FI": "https://prstats.realitymod.com/clan/8067/fi",
    "SAE": "https://prstats.realitymod.com/clan/42817/sae",
    "FI-R": "https://prstats.realitymod.com/clan/30397/fi-r",
    "R-LDH": "https://prstats.realitymod.com/clan/37315/r-ldh",
    "141": "https://prstats.realitymod.com/clan/7555/141",
    "WD": "https://prstats.realitymod.com/clan/11052/wd",
    "300": "https://prstats.realitymod.com/clan/36331/300",
    "E-LAM": "https://prstats.realitymod.com/clan/29486/e-lam",
    "RIM:LA": "https://prstats.realitymod.com/clan/9406/rimla",
    "ADG": "https://prstats.realitymod.com/clan/17913/adg",
    "A-LDH": "https://prstats.realitymod.com/clan/44173/a-ldh",
    "FASO": "https://prstats.realitymod.com/clan/46393/faso",
    "PORN": "https://prstats.realitymod.com/clan/47806/porn",
}

# Scoring weights for Performance Score calculation
SCORING_WEIGHTS = {
    "kd": 1.0,
    "score": 0.4,
    "kills_per_round": 0.4,
    "rounds": 0.2,
}

# Fixed normalization caps (for stable historical scores)
NORM_CAPS = {
    "kd": 5.0,
    "score_per_round": 500.0,
    "kills_per_round": 10.0,
    "rounds": 1000.0,
}

LOW_ROUNDS_THRESHOLD = 50
MIN_ROUNDS_PENALTY = 10

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3

OUTPUT_DIR = "graphs"
HISTORY_DIR = "graphs/history"

GITHUB_PAGES_URL = "https://luccabruno3z.github.io"
