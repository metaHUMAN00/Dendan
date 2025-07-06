# Dendan
Dendan is a WIP water treatement plant monitoring software. Currently the monitoring is based solely on WQIs for the water quality and PCIs for the treatment performance.
Make sure to install all of the following libraries before running any script:
pip install pandas
pip install numpy
pip install datetime
pip install matplotlib
# WQI Usage
WQI_calc script requires parsing .csv files in the command line as arguments ie : python WQI_calc.py File_containing_water_quality_parameters_NumberofMonth_Year.csv.
  The .csv file must be structured as following:
  -The first Row contains labels: The first cell is the Date, the other cells of this row contains the names of the parameters used for the WQI analysis.
  -The first collumn excluding the label cell has the dates in the DD-MM-YYYY format.
  -The remaining collumns contain the values of each parameter respectively.
This script outputs a .csv file containing the results and two graphs one displaying the evolution of the WQI through the month and one that displays the Contribution of each parameter to the total WQI.
# X_bar, R charts and Cp,Cpk analysis
This script realises control charts for each individual parameter and calculates their respective Cp and Cpk.
  This script requires parcing .csv files in the command line same as the previous one; python X_bar_R_C.py Table_containing_subgroupings_of_parameter_X_NumberofMonth_Year.csv
  The .csv file must be structured as following:
  - The first row contains two cells: The first is the rational subgrouping label name it as u wish, The second is the Parameter X's name.
  - The first collumn excluding the first cell contains the number of the subgroup N to which the value of the parameter X belongs.
  - The size on all subgroups must be equal.
  - For precise instructions on choosing rational subgroupings consult the ISO 7870-2:2013 for elaborating Shewart control charts.
The script prompts the user for Upper and Lower Specification limits.
This script Outputs a .csv file containing the results of the analysis and two Graphs displaying the control Charts.
# Pp and Ppk analysis
This script calculates the Pp and Ppk for each parameter used in the WQI analysis.
  Usage: python X_bar_R_C.py Table_containing_values_of_parameter_X_NumberofMonth_Year.csv
  The .csv file contains a single collumn with the first cell containing the parameter name while the rest contains the values of parameter X.
This script outputs a .csv file containing the results of the analysis.
  
