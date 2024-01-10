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

##  Binary version

### Additional Feature
- **Filtering**: If specified can take a Json's filter (obtained through https://github.com/CERC-Genomic-Medicine/CARTaGENE_PheWas/tree/d1b00e77aac95383536bde07c5a3756e1d8b95b8/Phenotype_filtering/Filtering_tool)

### Usage Binary version

| Argument               | Description                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------------|
| `-c` or `--catalog`    | Excel spreadsheet "COMBINED_CATALOG_*.xlsx". Contains meta-information about variables and sheets like "COMBINED_CATALOG", "Categories", "Linear data missing codes". |
| `-p` or `--phenotypes` | CSV file with phenotype values for each sample in the CARTaGENE study.                           |
| `-s` or `--samples`    | List of individual IDs to consider (e.g., PLINK's *.psam file). The IDs must be in the column named "IID". |
| `-j` or `--json`       | (Optional) Json file with inclusion and exclusion criteria. Required if `--Final` or `-f` is used. |
| `-i` or `--images`     | Produce age distributions. This is a flag with no additional arguments needed.                  |
| `-f` or `--Final`      | Produce phenotype file with modifications from a JSON file. This is a flag with no additional arguments needed. |
| `-o` or `--output`     | Prefix for output files.                                                                        |
| `-n` or `--n_threshold`| Threshold at which the number of Sample problem flag is raised.                                 |
| `--c_threshold`        | Threshold at which the number of Sample problem flag is raised.                                 |
| `-ss` or `--SS_threshold` | Threshold at which the number of Sex-Specific problem flag is raised.                       |


