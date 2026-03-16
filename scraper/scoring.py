"""Fixed-range normalization and Performance Score calculation."""

import logging
import math

import pandas as pd

from .config import NORM_CAPS, SCORING_WEIGHTS

logger = logging.getLogger(__name__)


def _sigmoid_penalty(rounds: float) -> float:
    """Smooth sigmoid penalty for low round counts.

    Returns a value between ~0 and ~1.
    Centered at 25 rounds, with slope controlled by divisor 10.
    Players with very few rounds get penalized; those above ~50 are near 1.0.
    """
    return 1.0 / (1.0 + math.exp(-((rounds - 25) / 10)))


def calculate_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Performance Score using fixed-range normalization.

    Operates in-place on the DataFrame and returns it.

    Expected input columns: K/D Ratio, Score per Round, Kills per Round, Rounds.
    Added columns: Normalized_KD, Normalized_Score, Normalized_Kills_Per_Round,
                    Normalized_Rounds, Performance Score.
    """
    if df.empty:
        logger.warning("Empty DataFrame passed to calculate_scores.")
        return df

    df = df.copy()

    # Fixed-range normalization (deterministic, no dependency on current data)
    df["Normalized_KD"] = (df["K/D Ratio"] / NORM_CAPS["kd"]).clip(upper=1.0)
    df["Normalized_Score"] = (df["Score per Round"] / NORM_CAPS["score_per_round"]).clip(upper=1.0)
    df["Normalized_Kills_Per_Round"] = (df["Kills per Round"] / NORM_CAPS["kills_per_round"]).clip(upper=1.0)
    df["Normalized_Rounds"] = (df["Rounds"] / NORM_CAPS["rounds"]).clip(upper=1.0)

    # Weighted sum
    w = SCORING_WEIGHTS
    df["Performance Score"] = (
        w["kd"] * df["Normalized_KD"]
        + w["score"] * df["Normalized_Score"]
        + w["kills_per_round"] * df["Normalized_Kills_Per_Round"]
        + w["rounds"] * df["Normalized_Rounds"]
    )

    # Apply smooth sigmoid penalty for low round counts
    df["Performance Score"] *= df["Rounds"].apply(_sigmoid_penalty)

    logger.info(
        "Scores calculated for %d players. Range: %.4f — %.4f",
        len(df),
        df["Performance Score"].min(),
        df["Performance Score"].max(),
    )

    return df
