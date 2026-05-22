"""
Created on Fri Jan 23 11:30:40 2026

@author: msjoshi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
import itertools
from matplotlib.ticker import MultipleLocator

# -------------------------------
# File selection (input)
# -------------------------------
root = Tk()
root.withdraw()

input_file = filedialog.askopenfilename(
    title="Select Excel data file",
    filetypes=[("Excel files", "*.xlsx")]
)

if not input_file:
    raise SystemExit("No input file selected.")

# -------------------------------
# Load data
# -------------------------------
df = pd.read_excel(input_file)

time = df.iloc[:, 0]        # assumed to be in hours
signals = df.iloc[:, 1:]

# -------------------------------
# Restrict data to >= 12 h
# -------------------------------
mask = time >= 12
time = time[mask]
signals = signals.loc[mask]

# -------------------------------
# Darker floral color palette
# -------------------------------
floral_colors = [
    "#D16D8A",  # dark rose
    "#6FAED9",  # muted blue
    "#6FB7A5",  # teal
    "#C97C7C",  # dusty red
    "#9B7CB8",  # lavender
    "#D4B24C",  # warm yellow
    "#5DADE2",  # sky blue
    "#E59866",  # peach
]

color_cycle = itertools.cycle(floral_colors)

# -------------------------------
# Plot traces
# -------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

for col in signals.columns:
    ax.plot(
        time,
        signals[col],
        color=next(color_cycle),
        alpha=0.8,
        linewidth=1
    )

# -------------------------------
# Moving median of population
# -------------------------------
population_median = signals.median(axis=1)

window_size = 10
moving_median = population_median.rolling(
    window=window_size,
    center=True
).median()

ax.plot(
    time,
    moving_median,
    color="black",
    linewidth=3,
    label=f"Moving median (window={window_size})"
)

# -------------------------------
# Axis formatting
# -------------------------------
ax.set_xlabel("Time (h)")
ax.set_ylabel("Bioluminescence")
ax.set_title("Bioluminescence signals vs time")

ax.xaxis.set_major_locator(MultipleLocator(12))

# Exact axis intersections (no gaps)
ax.set_xlim(left=12)
ax.margins(x=0, y=0)

# Clean axes: only left & bottom
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Thicker axes for print
ax.spines["left"].set_linewidth(1.2)
ax.spines["bottom"].set_linewidth(1.2)

ax.tick_params(direction="out", length=6)
ax.legend(frameon=False)

plt.tight_layout()

# -------------------------------
# Save dialog (SVG)
# -------------------------------
output_file = filedialog.asksaveasfilename(
    title="Save plot as SVG",
    defaultextension=".svg",
    filetypes=[("SVG files", "*.svg")]
)

if output_file:
    plt.savefig(output_file, format="svg")
    print(f"Plot saved to: {output_file}")

plt.show()
