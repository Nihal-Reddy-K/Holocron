"""
Holocron - Basic Chorea Simulation

Illustrative software simulation only.
This does not control a stimulation device and is not a medical model.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict


# ============================================================
# SETTINGS
# ============================================================

SLEEP_TARGET = 8
SLEEP_EFFECT = 0.06

MEALS_TARGET = 3
MEAL_EFFECT = 0.05

STRESS_EFFECT = 0.03

STIM_MAX = 80
MAX_REDUCTION = 0.35

SAMPLE_RATE = 100
SESSION_LENGTH = 30

BASELINE_END = 10
STIM_END = 20
RAMP_TIME = 2
FADE_TIME = 5


# ============================================================
# DATA
# ============================================================

@dataclass
class Inputs:
    chorea: float
    sleep_hours: float
    meals: int
    stress: float = 0


@dataclass
class Result:
    reported_chorea: float
    adjusted_chorea: float
    stimulation: float
    predicted_after: float
    sleep_effect: float
    food_effect: float
    stress_effect: float

    def to_dict(self):
        return {
            key: round(value, 2)
            for key, value in asdict(self).items()
        }


# ============================================================
# HELPERS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


# ============================================================
# SIMULATION
# ============================================================

def simulate(inputs: Inputs) -> Result:

    chorea = clamp(inputs.chorea, 0, 10)

    sleep_effect = clamp(
        SLEEP_EFFECT * (SLEEP_TARGET - inputs.sleep_hours),
        0,
        0.36
    )

    food_effect = clamp(
        MEAL_EFFECT * (MEALS_TARGET - inputs.meals),
        0,
        0.15
    )

    stress_effect = clamp(
        STRESS_EFFECT * inputs.stress,
        0,
        0.30
    )

    adjusted = chorea * (
        1
        + sleep_effect
        + food_effect
        + stress_effect
    )

    adjusted = clamp(adjusted, 0, 10)

    stimulation = clamp(
        adjusted * 10,
        0,
        STIM_MAX
    )

    reduction = (
        MAX_REDUCTION
        * stimulation
        / STIM_MAX
    )

    predicted_after = adjusted * (1 - reduction)

    return Result(
        reported_chorea=chorea,
        adjusted_chorea=adjusted,
        stimulation=stimulation,
        predicted_after=predicted_after,
        sleep_effect=sleep_effect * 100,
        food_effect=food_effect * 100,
        stress_effect=stress_effect * 100,
    )


# ============================================================
# MOVEMENT SIGNAL
# ============================================================

def build_signal(result: Result, seed=None):

    import numpy as np

    rng = np.random.default_rng(seed)

    time = np.arange(
        0,
        SESSION_LENGTH,
        1 / SAMPLE_RATE
    )

    # Irregular movement
    noise = rng.normal(0, 1, len(time))

    kernel = np.ones(20) / 20

    movement = np.convolve(
        noise,
        kernel,
        mode="same"
    )

    # Occasional movement spikes
    spikes = np.zeros(len(time))

    for i in range(len(time)):

        if rng.random() < 0.008:

            size = rng.uniform(1.5, 3.0)

            if rng.random() > 0.5:
                size *= -1

            end = min(i + 30, len(spikes))

            decay = np.exp(
                -np.arange(end - i) / 8
            )

            spikes[i:end] += size * decay

    movement += spikes

    # Normalize
    movement /= max(
        np.percentile(np.abs(movement), 98),
        0.001
    )

    # ========================================================
    # STIMULATION CURVE
    # ========================================================

    stimulation = np.zeros_like(time)

    ramp = (
        time - BASELINE_END
    ) / RAMP_TIME

    ramp = np.clip(ramp, 0, 1)

    active = (
        (time >= BASELINE_END)
        & (time < STIM_END)
    )

    stimulation[active] = (
        result.stimulation
        * ramp[active]
    )

    # After-effect
    after = time >= STIM_END

    stimulation[after] = (
        result.stimulation
        * np.exp(
            -(time[after] - STIM_END)
            / FADE_TIME
        )
    )

    # ========================================================
    # MOVEMENT RESPONSE
    # ========================================================

    maximum_reduction = (
        MAX_REDUCTION
        * result.stimulation
        / STIM_MAX
    )

    effect = stimulation / max(
        result.stimulation,
        1
    )

    amplitude = (
        result.adjusted_chorea
        * (1 - maximum_reduction * effect)
    )

    movement *= amplitude

    return time, movement, stimulation


# ============================================================
# GRAPH
# ============================================================

def show_graph(result: Result, seed=None):

    import matplotlib.pyplot as plt

    time, movement, stimulation = build_signal(
        result,
        seed
    )

    fig, (movement_ax, stimulation_ax) = plt.subplots(
        2,
        1,
        figsize=(11, 7),
        sharex=True,
        gridspec_kw={
            "height_ratios": [3, 1]
        }
    )

    # Movement graph
    movement_ax.plot(
        time,
        movement,
        linewidth=1.2
    )

    movement_ax.axvspan(
        BASELINE_END,
        STIM_END,
        alpha=0.10
    )

    movement_ax.set_ylabel("Movement")

    movement_ax.set_title(
        f"Holocron Simulation | "
        f"Chorea: {result.reported_chorea:.1f} → "
        f"{result.adjusted_chorea:.1f} → "
        f"{result.predicted_after:.1f}"
    )

    movement_ax.grid(
        axis="y",
        alpha=0.25
    )

    # Stimulation graph
    stimulation_ax.plot(
        time,
        stimulation,
        linewidth=2
    )

    stimulation_ax.fill_between(
        time,
        stimulation,
        alpha=0.12
    )

    stimulation_ax.axvspan(
        BASELINE_END,
        STIM_END,
        alpha=0.10
    )

    stimulation_ax.set_ylabel(
        "Simulated\nLevel"
    )

    stimulation_ax.set_xlabel(
        "Time (seconds)"
    )

    stimulation_ax.set_ylim(
        0,
        STIM_MAX + 10
    )

    stimulation_ax.grid(
        axis="y",
        alpha=0.25
    )

    # Phase labels
    movement_ax.text(
        5,
        movement_ax.get_ylim()[1] * 0.85,
        "BASELINE",
        ha="center"
    )

    movement_ax.text(
        15,
        movement_ax.get_ylim()[1] * 0.85,
        "SIMULATED STIMULATION",
        ha="center"
    )

    movement_ax.text(
        25,
        movement_ax.get_ylim()[1] * 0.85,
        "AFTER-EFFECT",
        ha="center"
    )

    plt.tight_layout()
    plt.show()


# ============================================================
# TERMINAL
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Holocron chorea simulation"
    )

    parser.add_argument(
        "--chorea",
        type=float,
        required=True
    )

    parser.add_argument(
        "--sleep",
        type=float,
        required=True
    )

    parser.add_argument(
        "--meals",
        type=int,
        required=True
    )

    parser.add_argument(
        "--stress",
        type=float,
        default=0
    )

    parser.add_argument(
        "--plot",
        action="store_true"
    )

    parser.add_argument(
        "--json",
        action="store_true"
    )

    args = parser.parse_args()

    inputs = Inputs(
        chorea=args.chorea,
        sleep_hours=args.sleep,
        meals=args.meals,
        stress=args.stress
    )

    result = simulate(inputs)

    if args.json:

        print(
            json.dumps(
                result.to_dict()
            )
        )

    else:

        print()
        print("HOLOCRON SIMULATION")
        print("-" * 30)

        print(
            f"Reported chorea : "
            f"{result.reported_chorea:.1f}/10"
        )

        print(
            f"Sleep effect    : "
            f"+{result.sleep_effect:.0f}%"
        )

        print(
            f"Food effect     : "
            f"+{result.food_effect:.0f}%"
        )

        print(
            f"Stress effect   : "
            f"+{result.stress_effect:.0f}%"
        )

        print()

        print(
            f"Adjusted chorea : "
            f"{result.adjusted_chorea:.1f}/10"
        )

        print(
            f"Simulated level : "
            f"{result.stimulation:.0f}/{STIM_MAX}"
        )

        print(
            f"Predicted after : "
            f"{result.predicted_after:.1f}/10"
        )

        print()
        print("SIMULATION ONLY.")

    if args.plot:
        show_graph(result)


if __name__ == "__main__":
    main()
