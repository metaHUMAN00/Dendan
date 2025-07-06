import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys

# Get filename from command line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <input_csv_file>")
    sys.exit(1)
input_file = sys.argv[1]

# Load data with correct date parsing
df = pd.read_csv(input_file, parse_dates=['Date'], dayfirst=True)

# Verify date parsing
print("First 3 dates after parsing:")
print(df['Date'].head(3))

# Define standards
standards = {
    'MES': #MES_standard,
    'DCO': #DCO_standard,
    'DBO5': #DBO5_standard,
}

# Calculate weights with K-factor
K = 1 / sum(1/s for s in standards.values())
weights = {param: K/s for param, s in standards.items()}

# Modified WQI calculation function that returns intermediate values
def calculate_wqi(row):
    wqi = 0
    qi_wi_values = {}  # Store intermediate calculations
    for param, s in standards.items():
        ci = row[param]
        qi = (ci / s) * 100
        qi_wi = qi * weights[param]
        qi_wi_values[param] = qi_wi
        wqi += qi_wi
    return wqi, qi_wi_values  # Return both WQI and intermediate values

# Apply calculations and store results
wqi_results = df.apply(calculate_wqi, axis=1)
df['WQI'] = wqi_results.apply(lambda x: x[0])  # Extract WQI values

# Add temporal columns
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year
df['Month_Name'] = df['Date'].dt.strftime('%B')

# Classification function
def classify_wqi(wqi):
    if wqi < 50: return "Excellent"
    elif 50 <= wqi < 100: return "Good"
    elif 100 <= wqi < 200: return "Poor"
    else: return "Unsuitable"
df['WQI_Class'] = df['WQI'].apply(classify_wqi)

# Calculate monthly average WQI
monthly_avg_wqi = df['WQI'].mean()

# Dynamic parameter contribution calculation
def calculate_parameter_contributions(row):
    contributions = {}
    _, qi_wi_values = calculate_wqi(row)  # Reuse the WQI function
    total_qi_wi = row['WQI']  # Use the pre-calculated WQI
    
    for param in standards.keys():
        contribution_percent = (qi_wi_values[param] / total_qi_wi) * 100
        contributions[f'{param}_contribution'] = contribution_percent
    
    return pd.Series(contributions)

# Apply parameter contribution calculations
contribution_df = df.apply(calculate_parameter_contributions, axis=1)
df = pd.concat([df, contribution_df], axis=1)

# Calculate average parameter contributions
avg_contributions = {param: df[f'{param}_contribution'].mean() for param in standards.keys()}

# Generate output
output_filename = f"WQI_EC__results_{df['Month_Name'][0]}_{df['Year'][0]}.csv"
df.to_csv(output_filename, index=False)

# Visualization - WQI Trend
plt.figure(figsize=(12,6))
colors = {'Excellent':'green', 'Good':'blue', 'Poor':'orange', 'Unsuitable':'red'}
plt.scatter(df['Date'], df['WQI'], c=df['WQI_Class'].map(colors), s=100)

# Add threshold and average lines
plt.axhline(y=100, color='black', linestyle='--', label='Good/Poor Threshold')
plt.axhline(y=monthly_avg_wqi, color='purple', linestyle='-', 
            label=f'Monthly Avg: {monthly_avg_wqi:.1f}')

plt.title(f"WQI Analysis Clarified Water ({df['Month_Name'][0]} {df['Year'][0]})")
plt.ylabel('WQI Score')
plt.xticks(rotation=45)

# Create legend
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Excellent'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Good'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Poor'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Unsuitable'),
    plt.Line2D([0], [0], color='black', linestyle='--', label='WQI = 100 Threshold'),
    plt.Line2D([0], [0], color='purple', linestyle='-', label=f'Monthly Avg = {monthly_avg_wqi:.1f}')
]

plt.legend(
    handles=legend_elements,
    bbox_to_anchor=(1.05, 1),
    loc='upper left',
    borderaxespad=0.
)

plt.grid(True, alpha=0.3)
plt.subplots_adjust(right=0.8)
plt.tight_layout()
output_fig = f"WQI_EC__fig_{df['Month_Name'][0]}_{df['Year'][0]}.png"
plt.savefig(output_fig, dpi=300, bbox_inches='tight')
plt.show()

# Visualization - Parameter Contributions (Dynamic)
plt.figure(figsize=(14, 8))

# Scientific color palette (dynamic assignment)
scientific_palette = [
    '#1f77b4',  # Blue
    '#9467bd',  # Purple
    '#FFE55C',  # Pale Gold
    '#98FB98',  # Pale Green
    '#17becf'   # Cyan
    '#2ca02c',  # Green
    '#d62728',  # Red
    '#8c564b',  # Brown
    '#ff7f0e',  # Orange
    '#7f7f7f',  # Gray
]

# Dynamically assign colors from scientific palette
param_colors = {param: scientific_palette[i % len(scientific_palette)] 
               for i, param in enumerate(standards.keys())}

# Prepare data and create stacked bars
dates = df['Date']
x_pos = range(len(dates))
width = 0.8

# Initialize bottom for stacking
bottom = None
for param in standards.keys():
    contrib = df[f'{param}_contribution']
    if bottom is None:
        plt.bar(x_pos, contrib, width, label=param, color=param_colors[param])
        bottom = contrib
    else:
        plt.bar(x_pos, contrib, width, bottom=bottom, label=param, color=param_colors[param])
        bottom += contrib

# Customize the plot
plt.title(f"Parameter Contributions to WQI ({df['Month_Name'][0]} {df['Year'][0]})", 
          fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Contribution (%)', fontsize=12)
plt.xlabel('Date', fontsize=12)

# Format x-axis with dates
date_labels = [d.strftime('%d-%m-%Y') for d in dates]
plt.xticks(x_pos, date_labels, rotation=45, ha='right')

# Add grid
plt.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)

# Create legend with average contributions
legend_labels = [f'{param} ({avg_contributions[param]:.1f}%)' for param in standards.keys()]
plt.legend(
    legend_labels,
    bbox_to_anchor=(1.18, 1.02),  # Adjusted for top-right placement
    loc='upper left',
    borderaxespad=0.,
    frameon=True,
    fancybox=True,
    shadow=True,
    fontsize=10
)

# Set y-axis limits and ticks
plt.ylim(0, 100)
plt.yticks(range(0, 101, 10))

# Improve layout
plt.tight_layout()

# Save the stacked contribution chart
output_contrib_fig = f"WQI_EC__param_contrib_stacked_{df['Month_Name'][0]}_{df['Year'][0]}.png"
plt.savefig(output_contrib_fig, dpi=300, bbox_inches='tight')
plt.show()

print(f"\nResults saved to {output_filename}")
print(f"\nStacked contribution chart saved to {output_contrib_fig}")
print(f"Monthly average WQI= {monthly_avg_wqi:.2f}")
print("\nAverage parameter contributions:")
for param, contrib in avg_contributions.items():
    print(f"{param}: {contrib:.1f}%")
print("\nFirst 3 calculated rows:")
print(df[['Date', 'WQI', 'WQI_Class']].head(3))