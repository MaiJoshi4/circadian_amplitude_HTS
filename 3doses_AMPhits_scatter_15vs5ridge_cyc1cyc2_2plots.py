"""
Created on Thu Jan  8 15:02:32 2026

@author: msjoshi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

# --- Hit identification function ---
def is_hit(row):
    amp_criteria = all([
        row['ridge_1.5'] >= 25, row['cycle1_1.5'] >= 25, row['cycle2_1.5'] >= 25,
        row['ridge_5'] >= 30, row['cycle1_5'] >= 30, row['cycle2_5'] >= 30
    ])
    dose_response_15_vs_5 = any([
        row['ridge_1.5'] < row['ridge_5'],
        row['cycle1_1.5'] < row['cycle1_5'],
        row['cycle2_1.5'] < row['cycle2_5']
    ])
    dose_response_05_vs_15 = any([
        row['ridge_0.5'] < row['ridge_1.5'],
        row['cycle1_0.5'] < row['cycle1_1.5'],
        row['cycle2_0.5'] < row['cycle2_1.5']
    ])
    return amp_criteria and dose_response_15_vs_5 and dose_response_05_vs_15

# --- Load file ---
Tk().withdraw()
file_path = askopenfilename(title='Select Excel file (with compound_dose, ridge, cycle1, cycle2)')
if not file_path:
    print("No file selected, exiting.")
    exit()

df = pd.read_excel(file_path)

# --- Parse compound and dose ---
def parse_compound_dose(s):
    try:
        base = s.split('_')[0]
        parts = base.split()
        compound = parts[0]
        dose = float(parts[1])
        return compound, dose
    except:
        return np.nan, np.nan

df[['Compound', 'Dose']] = df['compound_dose'].apply(parse_compound_dose).apply(pd.Series)
df = df.dropna(subset=['Compound', 'Dose'])
df.loc[df['Dose'] == 5.1, 'Dose'] = 5.0  # normalize

# --- Pivot table ---
pivot = df.pivot_table(
    index='Compound',
    columns='Dose',
    values=['ridge', 'cycle1', 'cycle2'],
    aggfunc='mean'
)

# Clean column names: ('ridge', 5.0) → 'ridge_5'
pivot.columns = [f"{col[0]}_{int(col[1]) if col[1] == int(col[1]) else col[1]}" for col in pivot.columns]
pivot = pivot.reset_index()

# --- Assign hit status ---
pivot['is_hit'] = pivot.apply(is_hit, axis=1)

# --- Assign visual category ---
def get_category(row):
    amp_criteria = all([
        row['ridge_1.5'] >= 25, row['cycle1_1.5'] >= 25, row['cycle2_1.5'] >= 25,
        row['ridge_5'] >= 30, row['cycle1_5'] >= 30, row['cycle2_5'] >= 30
    ])
    if row['is_hit']:
        return 'Hit'
    elif amp_criteria:
        return 'AmpOnly'
    else:
        return 'AmpFail'

pivot['category'] = pivot.apply(get_category, axis=1)

# --- Sort hits to top and alphabetically within groups, then save Excel ---
hits = pivot[pivot['is_hit']].sort_values(by='Compound', ascending=True)
non_hits = pivot[~pivot['is_hit']].sort_values(by='Compound', ascending=True)
pivot_sorted = pd.concat([hits, non_hits], ignore_index=True)

output_excel_path = os.path.join(os.path.dirname(file_path), 'compound_hits_summary.xlsx')
pivot_sorted.to_excel(output_excel_path, index=False)
print(f"✅ Excel saved: {output_excel_path}")

# --- Common plotting settings ---
palette = {
    'Hit': ('green', 's'),         # Green square
    'AmpOnly': ('cyan', 'o'),      # Cyan circle
    'AmpFail': ('deeppink', 'o')   # Deeppink circle
}
plot_order = ['AmpFail', 'AmpOnly', 'Hit']

def scatter_plot(x_col, y_col, xlabel, ylabel, title, filename):
    plt.figure(figsize=(8, 6))
    ax = plt.gca()
    
    # Grid and frame
    plt.grid(True, color='gray', linestyle='-', linewidth=0.1)
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
    
    # Threshold lines
    plt.axhline(30, linestyle='--', color='gray', linewidth=1)
    plt.axvline(25, linestyle='--', color='gray', linewidth=1)
    
    # Plot categories
    for category in plot_order:
        color, marker = palette[category]
        data = pivot[pivot['category'] == category]
        plt.scatter(
            data[x_col], data[y_col],
            c=color,
            edgecolor='black',
            s=120,
            label=category,
            marker=marker,
            linewidth=1,
            zorder=3 if category == 'Hit' else 2 if category == 'AmpOnly' else 1
        )
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(title='Category')
    plt.tight_layout()
    
    output_path = os.path.join(os.path.dirname(file_path), filename)
    plt.savefig(output_path)
    print(f"✅ Plot saved: {output_path}")
    plt.show()

# --- Plot 1: Cycle1 vs Cycle2 at 5 µM ---
scatter_plot(
    x_col='cycle1_5',
    y_col='cycle2_5',
    xlabel='Cycle1 Amplitude (5 µM)',
    ylabel='Cycle2 Amplitude (5 µM)',
    title='Cycle1 vs Cycle2 Amplitudes at 5 µM',
    filename='compound_cycle_plot.svg'
)

# --- Plot 2: Ridge 1.5 µM vs 5 µM ---
scatter_plot(
    x_col='ridge_1.5',
    y_col='ridge_5',
    xlabel='Ridge Amplitude (1.5 µM)',
    ylabel='Ridge Amplitude (5 µM)',
    title='Ridge Amplitudes: 1.5 µM vs 5 µM',
    filename='compound_ridge_plot.svg'
)
