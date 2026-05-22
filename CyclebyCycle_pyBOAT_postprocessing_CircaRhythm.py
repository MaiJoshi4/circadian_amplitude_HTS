"""
Created on Wed Dec 17 16:14:30 2025

@author: msjoshi
"""

import pandas as pd
import numpy as np
import glob
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory, asksaveasfilename

# -------------------------
# Select folder with CSV files
# -------------------------
Tk().withdraw()

input_dir = askdirectory(title="Select folder containing *_readout.csv files")
if not input_dir:
    print("No folder selected. Exiting.")
    exit()

csv_files = glob.glob(os.path.join(input_dir, "*_readout.csv"))
if not csv_files:
    print("No *_readout.csv files found. Exiting.")
    exit()

all_cycles = []

# -------------------------
# Process each file
# -------------------------
for file_path in csv_files:
    file_name = os.path.basename(file_path)

    ridge = pd.read_csv(file_path)
    ridge = ridge.sort_values("time").reset_index(drop=True)

    # -------------------------
    # Cycle detection via period integration
    # -------------------------
    dt = ridge["time"].diff().fillna(0)
    dphi = 2 * np.pi * dt / ridge["periods"]
    ridge["cum_phase"] = dphi.cumsum()

    # Cycle numbering starts at 1
    ridge["cycle"] = np.floor(ridge["cum_phase"] / (2 * np.pi)) + 1

    # -------------------------
    # Drop partial first/last cycles
    # -------------------------
    cycle_counts = ridge["cycle"].value_counts()
    full_cycles = cycle_counts[cycle_counts > 5].index
    ridge = ridge[ridge["cycle"].isin(full_cycles)]

    # -------------------------
    # Mean ridge metrics (whole trace)
    # -------------------------
    mean_ridge_amplitude = ridge["amplitude"].mean()
    mean_ridge_period = ridge["periods"].mean()
    mean_ridge_power = ridge["power"].mean()

    # -------------------------
    # Cycle-by-cycle metrics
    # -------------------------
    cycles = ridge.groupby("cycle").agg(
        avg_amplitude=("amplitude", "mean"),
        peak_amplitude=("amplitude", "max"),
        mean_period=("periods", "mean"),
        avg_power=("power", "mean"),
        start_time=("time", "min"),
        end_time=("time", "max")
    ).reset_index()

    # -------------------------
    # Add metadata
    # -------------------------
    cycles.insert(0, "file", file_name)
    cycles["mean_ridge_amplitude"] = mean_ridge_amplitude
    cycles["mean_ridge_period"] = mean_ridge_period
    cycles["mean_ridge_power"] = mean_ridge_power
    cycles["cycle_duration"] = cycles["end_time"] - cycles["start_time"]

    all_cycles.append(cycles)

# -------------------------
# Combine all files
# -------------------------
final_df = pd.concat(all_cycles, ignore_index=True)

# -------------------------
# Sort samples alphabetically
# -------------------------
final_df = final_df.sort_values("file").reset_index(drop=True)

# -------------------------
# Save Excel output (1 sheet per cycle)
# -------------------------
save_path = asksaveasfilename(
    title="Save combined cycle-by-cycle output",
    defaultextension=".xlsx",
    filetypes=[("Excel files", "*.xlsx")]
)

if save_path:
    with pd.ExcelWriter(save_path, engine="xlsxwriter") as writer:
        for cycle_num, cycle_df in final_df.groupby("cycle"):
            sheet_name = f"Cycle_{int(cycle_num)}"
            cycle_df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"\nCombined cycle-by-cycle output saved to:\n{save_path}")
else:
    print("No save location selected.")
