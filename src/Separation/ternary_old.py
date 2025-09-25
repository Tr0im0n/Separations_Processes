import numpy as np

solubilty_curve_file_name = r"solubility curve.txt"
solubility_array1d = np.loadtxt(solubilty_curve_file_name)
solubility_table2d = solubility_array1d.reshape(16, 9)
solubility_array = solubility_table2d[:, -3:]
np.savetxt("solubility_curve.csv", solubility_array, fmt='%.4e')
solubility_array *= 100

tie_lines_file_name = r"tie lines.txt"
tie_lines1d = np.loadtxt(tie_lines_file_name)
tie_lines2d = tie_lines1d.reshape(6, 6)
np.savetxt("tie_lines.csv", tie_lines2d, fmt='%.4e')
