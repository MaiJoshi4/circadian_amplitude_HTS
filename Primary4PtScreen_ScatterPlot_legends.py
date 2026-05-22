"""
Created on Tue Jan 27 13:44:10 2026

@author: msjoshi
"""

import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

# ---- CONFIG ----
SIZE_SCALE = 18          # increase marker size
COLOR_VMIN = 0
COLOR_VMAX = 15

# Hide the root tkinter window
Tk().withdraw()

# Prompt user to select an Excel file
file_path = askopenfilename(
    title="Select Excel file",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)

if not file_path:
    print("No file selected. Exiting.")
    exit()

# Load Excel data
df = pd.read_excel(file_path)

# Check for required columns
required_columns = {'6hr', '10hr', '24hr', '30hr'}
if not required_columns.issubset(df.columns):
    print(f"Missing required columns. Found: {df.columns.tolist()}")
    exit()

# Drop rows with missing values
df = df[['6hr', '10hr', '24hr', '30hr']].dropna()

# Replace negative 30hr values with a small positive number for size scaling
df['30hr_size'] = df['30hr'].clip(lower=0.1)

# Define hits: all four values > 1
df['is_hit'] = (
    (df['6hr'] > 1) &
    (df['10hr'] > 1) &
    (df['24hr'] > 1) &
    (df['30hr'] > 1)
)

# Start plotting
fig, ax = plt.subplots(figsize=(10, 7))

# Plot non-hits (circles)
sc1 = ax.scatter(
    df.loc[~df['is_hit'], '6hr'],
    df.loc[~df['is_hit'], '24hr'],
    c=df.loc[~df['is_hit'], '10hr'],
    s=df.loc[~df['is_hit'], '30hr_size'] * SIZE_SCALE,
    cmap='turbo',
    alpha=0.7,
    edgecolors='none',
    marker='o',
    vmin=COLOR_VMIN,
    vmax=COLOR_VMAX
)

# Plot hits (squares)
ax.scatter(
    df.loc[df['is_hit'], '6hr'],
    df.loc[df['is_hit'], '24hr'],
    c=df.loc[df['is_hit'], '10hr'],
    s=df.loc[df['is_hit'], '30hr_size'] * SIZE_SCALE,
    cmap='turbo',
    alpha=0.9,
    edgecolors='none',
    marker='s',
    vmin=COLOR_VMIN,
    vmax=COLOR_VMAX
)

# Reference lines at 1
ax.axvline(1, color='gray', linestyle='--', linewidth=1, zorder=5)
ax.axhline(1, color='gray', linestyle='--', linewidth=1, zorder=5)

# Axis labels and title
ax.set_xlabel('6hr')
ax.set_ylabel('24hr')
ax.set_title('Compound Screen: Hit Identification')

# ---- 10hr COLORBAR (TOP RIGHT, 0–15) ----
cbar = fig.colorbar(
    sc1,
    ax=ax,
    shrink=0.35,
    pad=0.02,
    location='right'
)
cbar.set_label('10hr')

# Move colorbar upward
cbar.ax.set_position([
    cbar.ax.get_position().x0,
    cbar.ax.get_position().y0 + 0.35,
    cbar.ax.get_position().width,
    cbar.ax.get_position().height
])

# ---- 30hr SIZE LEGEND (BOTTOM RIGHT) ----
size_legend_values = [0, 3, 6, 9, 12, 15]

for val in size_legend_values:
    size_val = max(val, 0.1)
    ax.scatter(
        [], [],
        s=size_val * SIZE_SCALE,
        c='gray',
        alpha=0.7,
        edgecolors='none',
        label=f'{val}'
    )

ax.legend(
    title='30hr',
    scatterpoints=1,
    frameon=False,
    labelspacing=1.2,
    handletextpad=1.5,
    loc='lower right',
    bbox_to_anchor=(1.28, 0.05)
)

# Axis tick spacing
ax.set_xticks(
    range(int(df['6hr'].min()) - 1, int(df['6hr'].max()) + 2, 2)
)
ax.set_yticks(
    range(int(df['24hr'].min()) - 1, int(df['24hr'].max()) + 2, 2)
)

# No grid / no minor ticks
ax.grid(False)
ax.minorticks_off()

plt.tight_layout()

# Save as SVG
output_path = os.path.join(
    os.path.dirname(file_path),
    "compound_screen_plot.svg"
)
plt.savefig(output_path, format='svg')
print(f"Plot saved as: {output_path}")

plt.show()
