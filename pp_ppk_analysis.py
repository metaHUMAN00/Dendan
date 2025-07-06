import pandas as pd
import numpy as np
import sys

def calculate_pp_ppk(data, usl=None, lsl=None):
    """
    Calculate Pp and Ppk for a given parameter
    """
    # Remove NaN values
    clean_data = data.dropna()
    n = len(clean_data)
    
    if n < 2:
        return {
            'Pp': np.nan,
            'Ppk': np.nan,
            'Mean': np.nan,
            'Std Dev': np.nan,
            'n': n
        }
    
    mean = np.mean(clean_data)
    std_dev = np.std(clean_data)  # Population standard deviation
    
    # Initialize capability indices
    pp = np.nan
    ppk = np.nan
    
    # Calculate capability indices based on available specification limits
    if not np.isnan(usl) and not np.isnan(lsl):
        # Two-sided specification
        pp = (usl - lsl) / (6 * std_dev)
        ppu = (usl - mean) / (3 * std_dev)
        ppl = (mean - lsl) / (3 * std_dev)
        ppk = min(ppu, ppl)
    elif not np.isnan(usl):
        # Only upper specification
        ppk = (usl - mean) / (3 * std_dev)
    elif not np.isnan(lsl):
        # Only lower specification
        ppk = (mean - lsl) / (3 * std_dev)
    
    return {
        'Pp': pp,
        'Ppk': ppk,
        'Mean': mean,
        'Std Dev': std_dev,
        'n': n,
        'USL': usl,
        'LSL': lsl
    }

def get_spec_limits(parameter):
    """
    Prompt user for specification limits for a parameter
    """
    print(f"\nEnter specification limits for {parameter}:")
    while True:
        try:
            usl_input = input("Upper Specification Limit (USL, press Enter if none): ").strip()
            usl = float(usl_input) if usl_input else np.nan
            
            lsl_input = input("Lower Specification Limit (LSL, press Enter if none): ").strip()
            lsl = float(lsl_input) if lsl_input else np.nan
            
            if np.isnan(usl) and np.isnan(lsl):
                print("At least one specification limit must be provided. Please try again.")
                continue
                
            return usl, lsl
        except ValueError:
            print("Invalid input. Please enter a numeric value or press Enter for none.")

def main(input_file):
    # Load data
    try:
        data = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    # Get all parameter columns (now includes first column)
    parameters = data.columns
    
    # Prepare results dictionary
    results = {
        'Statistic': ['Mean', 'Standard Deviation', 'USL', 'LSL', 'Pp', 'Ppk', 'Sample Size']
    }
    
    # Get specification limits and calculate for each parameter
    for param in parameters:
        usl, lsl = get_spec_limits(param)
        capability = calculate_pp_ppk(data[param], usl=usl, lsl=lsl)
        
        # Add results for this parameter
        results[param] = [
            capability['Mean'],
            capability['Std Dev'],
            capability['USL'],
            capability['LSL'],
            capability['Pp'],
            capability['Ppk'],
            capability['n']
        ]
    
    # Create and save results dataframe
    results_df = pd.DataFrame(results)
    
    # Reorder columns to put 'Statistic' first
    cols = ['Statistic'] + [col for col in results_df.columns if col != 'Statistic']
    results_df = results_df[cols]
    
    # Save to CSV
    output_file = input_file.replace('.csv', '_pp_ppk_analysis.csv')
    results_df.to_csv(output_file, index=False)
    
    print(f"\nAnalysis complete. Results saved to '{output_file}'")
    print("\nResults Summary:")
    print(results_df.to_string(index=False))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python pp_ppk_analysis.py <input_file.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    main(input_file)