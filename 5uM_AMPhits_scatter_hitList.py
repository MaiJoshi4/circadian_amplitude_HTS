"""
Circadian rhythm compound screening scatter plot
with hit / non-hit classification and Excel export
Sorted by intermediate plate location
@author: msjoshi
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import filedialog

# -----------------------------
# Threshold definitions
# -----------------------------
PERIOD_MIN = 23
PERIOD_MAX = 27
CYCLE1_MIN = 50
CYCLE2_MIN = 25

# -----------------------------
# File selection dialog
# -----------------------------
def get_file_path():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Excel file",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    root.destroy()
    return file_path

file_path = get_file_path()

if not file_path:
    print("No file selected.")
    raise SystemExit

# -----------------------------
# Load data
# -----------------------------
df = pd.read_excel(file_path)

# -----------------------------
# Classification function
# -----------------------------
def classify(row):
    valid_period = PERIOD_MIN <= row['period'] <= PERIOD_MAX
    good_cycle1 = row['cycle1'] >= CYCLE1_MIN
    good_cycle2 = row['cycle2'] >= CYCLE2_MIN

    if valid_period and good_cycle1 and good_cycle2:
        return pd.Series(
            ['green', 's',
             f"Hit: period {PERIOD_MIN}-{PERIOD_MAX}, cycle1≥{CYCLE1_MIN}, cycle2≥{CYCLE2_MIN}",
             'Hit'],
            index=['color', 'marker', 'label', 'hit_status']
        )
    elif valid_period:
        return pd.Series(
            ['cyan', 'o',
             f"Only period valid ({PERIOD_MIN}-{PERIOD_MAX}), cycle1<{CYCLE1_MIN} or cycle2<{CYCLE2_MIN}",
             'Non-hit'],
            index=['color', 'marker', 'label', 'hit_status']
        )
    else:
        return pd.Series(
            ['deeppink', 'o',
             f"Period outside {PERIOD_MIN}-{PERIOD_MAX}",
             'Non-hit'],
            index=['color', 'marker', 'label', 'hit_status']
        )

df[['color', 'marker', 'label', 'hit_status']] = df.apply(classify, axis=1)

# -----------------------------
# Scatter plot
# -----------------------------
plt.figure(figsize=(8, 6))

for (color, marker, label), subset in df.groupby(['color', 'marker', 'label']):
    plt.scatter(
        subset['cycle2'],
        subset['cycle1'],
        c=color,
        marker=marker,
        edgecolors='black',
        s=100,
        label=label
    )

# Threshold lines
plt.axhline(y=CYCLE1_MIN, color='gray', linestyle='--', linewidth=1)
plt.axvline(x=CYCLE2_MIN, color='gray', linestyle='--', linewidth=1)

plt.xlabel("Cycle 2")
plt.ylabel("Cycle 1")
plt.title("Compound Screening – Circadian Rhythm")
plt.legend(frameon=False)
plt.grid(True, color='gray', linestyle='-', linewidth=0.1)
plt.tight_layout()

# Save plot
base_name = os.path.splitext(os.path.basename(file_path))[0]
out_dir = os.path.dirname(file_path)
svg_path = os.path.join(out_dir, f"{base_name}_scatter.svg")
plt.savefig(svg_path, format='svg')
print(f"Plot saved as: {svg_path}")

plt.show()

# -----------------------------
# Export hit tables as Excel
# -----------------------------
export_cols = ['sample_assay_384', 'intermediate_plate_1536', 'period', 'cycle1', 'cycle2', 'hit_status', 'label']
summary_df = df[export_cols]

# Hits only, sorted by intermediate plate location
hits_df = summary_df[summary_df['hit_status'] == 'Hit']
hits_df = hits_df.sort_values(by='intermediate_plate_1536')

xlsx_path = os.path.join(out_dir, f"{base_name}_hit_classification.xlsx")
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='All_compounds', index=False)
    hits_df.to_excel(writer, sheet_name='Hits_only_sorted', index=False)

print(f"Hit classification Excel file saved as: {xlsx_path}")
