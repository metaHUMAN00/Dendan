import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def calculate_xbar_r(data, usl=None, lsl=None):
    """
    Calculate X-bar and R chart statistics for a parameter
    """
    # Group by subgroup
    grouped = data.groupby('Sub-Groups')
    # Calculate subgroup means (X-bar) and ranges (R)
    xbar = grouped.mean()
    ranges = grouped.max() - grouped.min()
    # Calculate center lines
    xbar_bar = xbar.mean().values[0]
    r_bar = ranges.mean().values[0]
    # Determine subgroup size dynamically
    subgroup_size = grouped.size().iloc[0]
    # Get appropriate control chart constants based on subgroup size
    constants = {
        2: {'a2': 1.880, 'd3': 0, 'd4': 3.267, 'd2': 1.128},
        3: {'a2': 1.023, 'd3': 0, 'd4': 2.574, 'd2': 1.693},
        4: {'a2': 0.729, 'd3': 0, 'd4': 2.282, 'd2': 2.059},
        5: {'a2': 0.577, 'd3': 0, 'd4': 2.114, 'd2': 2.326},
        6: {'a2': 0.483, 'd3': 0, 'd4': 2.004, 'd2': 2.534},
        7: {'a2': 0.419, 'd3': 0.076, 'd4': 1.924, 'd2': 2.704},
        8: {'a2': 0.373, 'd3': 0.136, 'd4': 1.864, 'd2': 2.847},
        9: {'a2': 0.337, 'd3': 0.184, 'd4': 1.816, 'd2': 2.970},
        10: {'a2': 0.308, 'd3': 0.223, 'd4': 1.777, 'd2': 3.078}
    }
    # Get constants for the actual subgroup size
    if subgroup_size in constants:
        const = constants[subgroup_size]
    else:
        raise ValueError(f"Subgroup size {subgroup_size} not supported. Supported sizes: 2-10")
    a2 = const['a2']
    d3 = const['d3']
    d4 = const['d4']
    d2 = const['d2']
    ucl_xbar = xbar_bar + a2 * r_bar
    lcl_xbar = xbar_bar - a2 * r_bar
    ucl_r = d4 * r_bar
    lcl_r = d3 * r_bar
    # Calculate process capability if specifications are provided
    cp = np.nan
    cpk = np.nan
    if usl is not None or lsl is not None:
        # Estimate standard deviation from R-bar
        sigma = r_bar / d2
        if usl is not None and lsl is not None:
            cp = (usl - lsl) / (6 * sigma)
            cpu = (usl - xbar_bar) / (3 * sigma)
            cpl = (xbar_bar - lsl) / (3 * sigma)
            cpk = min(cpu, cpl)
        elif usl is not None:
            cpk = (usl - xbar_bar) / (3 * sigma)
        elif lsl is not None:
            cpk = (xbar_bar - lsl) / (3 * sigma)
    return {
        'xbar_values': xbar.values.flatten(),
        'r_values': ranges.values.flatten(),
        'xbar_bar': xbar_bar,
        'r_bar': r_bar,
        'ucl_xbar': ucl_xbar,
        'lcl_xbar': lcl_xbar,
        'ucl_r': ucl_r,
        'lcl_r': lcl_r,
        'cp': cp,
        'cpk': cpk,
        'subgroup_size': subgroup_size
    }

def plot_control_charts(parameter, xbar_data, r_data, output_prefix):
    """
    Create X-bar and R control charts
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # X-bar chart
    ax1.plot(xbar_data['xbar_values'], marker='o', color='b', label='Subgroup Means')
    ax1.axhline(xbar_data['xbar_bar'], color='g', linestyle='--', label='X-bar-bar')
    ax1.axhline(xbar_data['ucl_xbar'], color='r', linestyle=':', label='UCL')
    ax1.axhline(xbar_data['lcl_xbar'], color='r', linestyle=':', label='LCL')
    ax1.set_title(f'X-bar Chart for {parameter} (Subgroup size: {xbar_data["subgroup_size"]})')
    ax1.set_xlabel('Subgroup')
    ax1.set_ylabel('Mean Value')
    ax1.legend()
    ax1.grid(True)
    
    # R chart
    ax2.plot(r_data['r_values'], marker='o', color='b', label='Subgroup Ranges')
    ax2.axhline(r_data['r_bar'], color='g', linestyle='--', label='R-bar')
    ax2.axhline(r_data['ucl_r'], color='r', linestyle=':', label='UCL')
    ax2.axhline(r_data['lcl_r'], color='r', linestyle=':', label='LCL')
    ax2.set_title(f'R Chart for {parameter} (Subgroup size: {r_data["subgroup_size"]})')
    ax2.set_xlabel('Subgroup')
    ax2.set_ylabel('Range')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}_{parameter}_control_charts.png')
    plt.close()

def get_spec_limits(parameter):
    """
    Prompt user for specification limits
    """
    print(f"\nEnter specification limits for {parameter}:")
    while True:
        try:
            usl_input = input("Upper Specification Limit (USL, press Enter if none): ")
            usl = float(usl_input) if usl_input else None
            
            lsl_input = input("Lower Specification Limit (LSL, press Enter if none): ")
            lsl = float(lsl_input) if lsl_input else None
            
            if usl is None and lsl is None:
                print("At least one specification limit must be provided for Cp/Cpk calculation.")
                continue
                
            return {'USL': usl, 'LSL': lsl}
        except ValueError:
            print("Invalid input. Please enter a numeric value or press Enter for none.")

def main(input_file):
    # Load data
    data = pd.read_csv(input_file)
    
    # Prepare results storage
    all_results = []
    specs = {}
    
    # Get specification limits for each parameter
    for parameter in data.columns[1:]:  # Skip first column (Sub-Groups)
        specs[parameter] = get_spec_limits(parameter)
    
    # Process each parameter
    for parameter in data.columns[1:]:  # Skip first column (Sub-Groups)
        # Get specification limits for this parameter
        usl = specs[parameter]['USL']
        lsl = specs[parameter]['LSL']
        
        # Calculate X-bar and R statistics
        param_data = data[['Sub-Groups', parameter]].copy()
        results = calculate_xbar_r(param_data, usl=usl, lsl=lsl)
        
        # Store results
        results_df = pd.DataFrame({
            'Subgroup': np.unique(data['Sub-Groups']),
            'X-bar': results['xbar_values'],
            'R': results['r_values']
        })
        
        summary_stats = pd.DataFrame({
            'Statistic': ['X-bar-bar', 'R-bar', 'UCL (X-bar)', 'LCL (X-bar)', 
                         'UCL (R)', 'LCL (R)', 'Cp', 'Cpk', 'Subgroup Size'],
            'Value': [results['xbar_bar'], results['r_bar'], 
                     results['ucl_xbar'], results['lcl_xbar'],
                     results['ucl_r'], results['lcl_r'],
                     results['cp'], results['cpk'],
                     results['subgroup_size']]
        })
        
        # Save results to CSV
        output_prefix = input_file.replace('.csv', '')
        results_df.to_csv(f'{output_prefix}_analysis_{parameter}_values.csv', index=False)
        summary_stats.to_csv(f'{output_prefix}_analysis_{parameter}_stats.csv', index=False)
        
        # Plot control charts
        plot_control_charts(parameter, results, results, output_prefix)
        
        # Collect results for combined output
        all_results.append({
            'Parameter': parameter,
            'X-bar-bar': results['xbar_bar'],
            'R-bar': results['r_bar'],
            'UCL (X-bar)': results['ucl_xbar'],
            'LCL (X-bar)': results['lcl_xbar'],
            'UCL (R)': results['ucl_r'],
            'LCL (R)': results['lcl_r'],
            'Cp': results['cp'],
            'Cpk': results['cpk'],
            'Subgroup Size': results['subgroup_size'],
            'USL': usl,
            'LSL': lsl
        })
    
    # Save combined results
    all_results_df = pd.DataFrame(all_results)
    all_results_df.to_csv(f'{input_file.replace(".csv", "")}_analysis_summary.csv', index=False)
    
    print("\nAnalysis complete. Results saved to:")
    print(f"- {input_file.replace('.csv', '')}_analysis_summary.csv")
    print("- Individual parameter files with _analysis_ prefix")
    print("- Control chart plots")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python xbar_r_analysis.py <input_file.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    main(input_file)