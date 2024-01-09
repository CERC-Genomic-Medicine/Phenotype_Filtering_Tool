# Summary Statistics Generation 

From the Cartagene data provide Summary_statics of each variable for the purpose of filtering.

## Continuous Summary statistics

### Features
- **Outlier Identification**: Implements standard deviation fold-based methods for identifying and handling outliers in data.
- **Data Visualization**: Integrates Seaborn and Matplotlib for sophisticated data visualization capabilities.
- **Statistical Analysis**: Utilizes SciPy for conducting various statistical analyses.

### Requirements
- Python 3
- Pandas
- NumPy
- Seaborn
- Matplotlib
- SciPy

### Installation
Ensure that all required libraries are installed in your Python environment. You can install these packages using `pip`:

```bash
pip install pandas numpy seaborn matplotlib scipy
```

### Usage Continuous version
```
python Continuous_summary_statistics.py -c [catalog] -p [phenotypes] -s [samples] -o [output] -t [outlier_threshold] -n [n_threshold] -ss [SS_threshold] -u [u_threshold]
```
| Argument               | Description                                                            |
|------------------------|------------------------------------------------------------------------|
| `-c` or `--catalog`    | Specify the Excel spreadsheet containing meta-information about variables. |
| `-p` or `--phenotypes` | Path to the CSV file with phenotype values.                            |
| `-s` or `--samples`    | File with a list of individual IDs to be considered.                   |
| `-o` or `--output`     | Prefix for the output files generated.                                 |
| `-t` or `--outlier_threshold` | Set the max threshold for outlier identification. (default 3)             |
| `-n` or `--n_threshold`| Define the threshold for raising the Sample problem flag. (default 100)            |
| `-ss` or `--SS_threshold` | Threshold for raising the Sex-Specific problem flag. (default 10)             |
| `-u` or `--u_threshold`| Set the minimum number of unique values before a problem flag is raised. (default 5) |

### Usage Binary version



