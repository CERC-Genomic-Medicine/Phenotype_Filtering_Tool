#!/usr/bin/python3


'''
AUTHOR: Daniel Taliun
YEAR: 2022 ?

Modified by Vincent Chapdelaine (2023)

-> introduction of outlier filters (sd fold)
-> integration of a display

'''
import pandas as pd
import math
import warnings
import argparse
import numpy as np
import sys
from collections import OrderedDict
import math
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew
from scipy.stats import kurtosis
from scipy.stats import rankdata, norm
from scipy import stats
import statsmodels.api as sm
import pylab as py

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


argparser = argparse.ArgumentParser(description = 'Prepares summary stats about continuous phenotypes in the CARTaGENE study.')
argparser.add_argument('-c', '--catalog', metavar = 'name', dest = 'in_catalog_spreadsheet', type = str, required = True, help = 'Excel spreadsheet "COMBINED_CATALOG_*.xlsx". It contains meta-information about all variables and the following sheets: "COMBINED_CATALOG", "Categories", "Linear data missing codes".')
argparser.add_argument('-p', '--phenotypes', metavar = 'name', dest = 'in_phenotypes', type = str, required = True, help = 'CSV file with phenotype values for each sample in the CARTaGENE study.')
argparser.add_argument('-s', '--samples', metavar = 'name', dest = 'in_samples', type = str, required = True, help = 'List of individual IDs to consider (e.g. PLINK\'s *.psam file). The individual IDs must be in the column named "IID".')
argparser.add_argument('-o', '--output', metavar = 'name', dest = 'out_prefix', type = str, required = True, help = 'Prefix for output files.')
argparser.add_argument('-t', '--outlier_threshold', metavar = 'value', dest = 'outlier_value', type = int, default=3, help = 'Standard threshold (number of fold above and below of threshold) Fold value of the given outlier detection threshold (default 3)')
argparser.add_argument('-n', '--n_threshold', metavar = 'value', dest = 'n_threshold', type = int, default=100, help = 'Threshold at which the number of Sample problem flag is raised ')
argparser.add_argument('-ss', '--SS_threshold', metavar = 'value', dest = 'ss_threshold', type = int, default=5, help = 'Threshold at which the number of Sex-Specific problem flag is raised')
argparser.add_argument('-u,', '--u_threshold', metavar = 'value', dest = 'u_threshold', type = int, default=10, help = 'Minimal number of Unique value below which the problem flag is raised')



catalog_sheet_categories = 'Categories'
catalog_sheet_missing_codes = 'Linear data missing codes'
catalog_sheet_main = 'COMBINED_CATALOG'

missing_categories = {'no answer', 'missing', 'missing answer', 'not available', 'not applicable', '-9', '-7', '77', '88', '99'}


plt.rcParams.update({'font.size': 20})

def rint(listed):
    c=3/8
    rank=rankdata(listed)
    x = (rank - c) / (len(rank) - 2*c + 1)
    return norm.ppf(x)

def plot(df, row, meaned, sd):
    # Pre-calculations
    recoded = df['RECODED']
    maxVal, minVal = np.nanmax(recoded), np.nanmin(recoded)
    ulim, llim = maxVal + 1, minVal - 1  # Default values

    if sd != 0:
        outlier_term = args.outlier_value * sd
        ulim = min(maxVal + sd, meaned + outlier_term + sd)
        llim = max(minVal - sd, meaned - outlier_term - sd)

    # Setup plot
    f, axes = plt.subplots(2, 3, height_ratios=[3, 1], figsize=(33, 10))

    # Histogram or KDE plot
    try:
        sns.histplot(recoded, ax=axes[0, 0])
    except np.core._exceptions._ArrayMemoryError:
        sns.kdeplot(recoded, ax=axes[0, 0])

    # Set limits and lines
    axes[0, 0].set_xlim(llim, ulim)
    axes[0, 0].axvline(x=meaned, color='black')

    # SD lines
    if sd != 0:
        for fold in range(2, args.outlier_value + 1):
            axes[0, 0].axvline(x=meaned + fold * sd, color='red')
            axes[0, 0].axvline(x=meaned - fold * sd, color='red')

    # Boxplot
    axes[1, 0].boxplot(recoded, vert=False)
    axes[1, 0].set_xlim(llim, ulim)

    # Skewness
    if sd != 0:
        S = skew(recoded)
        SS = skew(recoded[(recoded > meaned - 2 * sd) & (recoded < meaned + 2 * sd)])
        SSS = skew(recoded[(recoded > meaned - 3 * sd) & (recoded < meaned + 3 * sd)])
        axes[0, 0].annotate(f"Skewness = {S:.3f}\nSkewness (without outlier 2sd) = {SS:.3f}\nSkewness (without outlier 3sd) = {SSS:.3f}", xy=(0.01, .99), xycoords='axes fraction', textcoords='axes fraction', va='top', ha='left', fontsize='medium')

    # QQ plot
    sm.qqplot(recoded, line='s', ax=axes[0, 2])
    f.delaxes(axes[1, 2])

    # Final touches
    plt.suptitle(f'Phenotype Distribution \n {row.LABEL_ENGLISH}', size=24)
    f.savefig(f'{row.Varname}_distribution.png', dpi=300)
    plt.close(f)



def filter_binary_variables(df):
    for name, df_group in df.groupby(["SURVEY", "DOMAIN", "VARIABLE"]):
        df_only_codes = df_group[~df_group.CATEGORY.str.lower().isin(missing_categories)]
        if len(df_only_codes) != 2:
            continue
        yield name[2]


def filter_categorical_variables(df):
    for name, df_group in df.groupby(["SURVEY", "DOMAIN", "VARIABLE"]):
        df_only_codes = df_group[~df_group.CATEGORY.str.lower().isin(missing_categories)]
        if len(df_only_codes) < 2:
            continue
        yield name[2]


def recursive_detect_missing_codes_9(variable, missing_codes, df_pheno):
    has_missing_code = False
    max_value = df_pheno[variable].max()
    min_value = df_pheno[variable].min()
    if max_value in [9, 99, 999, 9999, 99999, 999999]:
        has_missing_code = True
        missing_codes.add(max_value)
    if min_value in [-9]:
        has_missing_code = True
        missing_codes.add(min_value)
    return has_missing_code


def recursive_detect_missing_codes_7(variable, missing_codes, df_pheno):
    has_missing_code = False
    max_value = df_pheno[variable].max()
    min_value = df_pheno[variable].min()
    if max_value in [7, 77, 777, 7777, 77777, 777777]:
        has_missing_code = True
        missing_codes.add(max_value)
    if min_value in [-7]:
        has_missing_code = True
        missing_codes.add(min_value)
    return has_missing_code

def Outlier_evaluation (Series,sd,mean):
    sd_details={}
    for i in range(2,int(args.outlier_value)+1):
        below = Series[Series < (mean-i*sd)]
        above = Series[Series > (mean+i*sd)]
        sd_details['[Outliers] Number of values below mean -'+str(i)+' SD'] = len(below)
        sd_details['[Outliers] Number of values above mean +'+str(i)+' SD'] = len(above)
        if sd_details['[Outliers] Number of values below mean -'+str(i)+' SD'] !=0 :
            sd_details['[Outliers] Maximum value below mean -'+str(i)+' SD'] = max(below)
        else :
            sd_details['[Outliers] Maximum value below mean -'+str(i)+' SD'] = 'NA'
        if sd_details['[Outliers] Number of values above mean +'+str(i)+' SD'] !=0 :
            sd_details['[Outliers] Minimal value above mean +'+str(i)+' SD'] = min(above)
        else :
            sd_details['[Outliers] Minimal value above mean +'+str(i)+' SD'] = 'NA'
    return sd_details


def filter_continuous_variables(df_variables, df_missing_codes, df_pheno):
    for index, row in df_variables.iterrows():
        variable = row['Varname']
        if 'RX_MED' in variable :
            continue
        if variable not in df_pheno.columns:
            continue
        if variable == 'PROJECT_CODE':
            continue
        if df_pheno.dtypes[variable] != 'float64':
            continue

        unit = row['UNIT_EN']
        missing_codes = variable_missing_codes.get(variable, set())

        df_pheno_cut = df_pheno[['SEX_BIRTH', variable]].copy()
        df_pheno_cut['RECODED'] = df_pheno_cut[variable].apply(lambda x: None if x in missing_codes else x )

        while recursive_detect_missing_codes_9('RECODED', missing_codes, df_pheno_cut):
            df_pheno_cut['RECODED'] = df_pheno_cut[variable].apply(lambda x: None if x in missing_codes else x )
        while recursive_detect_missing_codes_7('RECODED', missing_codes, df_pheno_cut):
            df_pheno_cut['RECODED'] = df_pheno_cut[variable].apply(lambda x: None if x in missing_codes else x )

        df_not_missing = df_pheno_cut[~df_pheno_cut.RECODED.isna()]
        if len(df_not_missing) ==0:
            continue

        mean = np.nanmean(df_pheno_cut.RECODED)
        unique_values = len(df_not_missing.RECODED.unique())
        # Several Statistics
        min_value = df_not_missing.RECODED.min()
        max_value = df_not_missing.RECODED.max()
        mean_value = df_not_missing.RECODED.mean()
        median_value = df_not_missing.RECODED.median()
        value_counts = df_not_missing.RECODED.value_counts()
        mode_freq = value_counts.values[0]
        mode_value = value_counts.index[0]
        n_total = len(df_not_missing)
        n_males = len(df_not_missing[df_not_missing.SEX_BIRTH == 0])
        n_females = len(df_not_missing[df_not_missing.SEX_BIRTH == 1])
        sd=np.nanstd(df_pheno_cut.RECODED)
        sd_details={}
        if sd != 0 :
            sd_details=Outlier_evaluation(df_not_missing.RECODED,sd,mean)
            PERC_5,PERC95 = np.percentile(df_not_missing.RECODED , [5,95])
            S=skew(df_not_missing.RECODED, axis=0, bias=True)
        else :
            ## if SD=0 only one value is present therefor these value are irrelevant
            PERC_5='NA'
            PERC95='NA'
            S='NA'
        #Plotting phenotypes
        plot(df_not_missing,row,mean,sd)
        problem=[] ## Provides flags
        if n_total==1 or unique_values == 1 :
            problem.append('Only one value')
        else :
            if n_total < args.n_threshold :
                problem.append('Total number of samples below ' + str(args.n_threshold))
            elif n_males < args.ss_threshold :
                problem.append('Sex-Specific ?')
            elif n_females < args.ss_threshold :
                problem.append('Sex-Specific ?')
            if mode_freq == 1 :
                problem.append('Mode frequency is 1')
            elif n_total - mode_freq == unique_values-1 :
                problem.append('Each values other than the mode appears only once')
            if unique_values < args.u_threshold  :
                problem.append('Number of unique values below ' + str(args.u_threshold))
        yield {**{'[Description] Variable' : variable, '[Description] Domain':  row['database'], '[Description] Label' : row['LABEL_ENGLISH'], '[Samples] Total': n_total, '[Samples] Males' : n_males,  '[Samples] Females' : n_females,'[Statistics] Minimum': min_value, '[Statistics] Maximum' : max_value, '[Statistics] N uniques values': unique_values, '[Statistics] PERC_5' : PERC_5, '[Statistics] median' : median_value, '[Statistics] PERC_95' : PERC95, '[Statistics] Mean': mean_value, '[Statistics] Mode': mode_value, '[Statistics] Mode frequency': mode_freq,'[Hidden] Skewness': S,'[Statistics] SD' : sd, '[Hidden] problem' : '|'.join(problem) },** sd_details,**{'[Description] Unit': unit, '[Description] Missing code' : '|'.join([str(i) for i in missing_codes])}}


if __name__ == '__main__':
    args = argparser.parse_args()
    num_processes = multiprocessing.cpu_count()-1
    df = pd.read_excel(args.in_catalog_spreadsheet, sheet_name = catalog_sheet_categories)
    df = df[["SURVEY", "DOMAIN", "VARIABLE", "CODE", "CATEGORY"]]
    df['CATEGORY'] = df['CATEGORY'].astype("string")

    binary_variables = set(filter_binary_variables(df))    
    categorical_variables = set(filter_categorical_variables(df))

    df_missing_codes = pd.read_excel(args.in_catalog_spreadsheet, sheet_name = catalog_sheet_missing_codes)
    variable_missing_codes = {row['varname']: set(int(x) for x in row['Missing codes'].split(',')) for index, row in df_missing_codes.iterrows()}

    df_variables = pd.read_excel(args.in_catalog_spreadsheet, sheet_name = catalog_sheet_main, header = 0, skiprows = lambda x: x == 1, dtype = {'UNIT_EN': str})
    df_variables['UNIT_EN'] = df_variables['UNIT_EN'].fillna('')

    df_variables = df_variables[(df_variables['Type '] == 1) & \
       (df_variables['Survey'].isin({'Phase A and B', 'Phase A', 'Phase B'})) & \
       (~df_variables['database'].isin({'ETHNIC', 'RESIDENTIAL_HISTORY', 'IDENTITY'})) & \
       (~df_variables['Format'].isin({'DATETIME', 'YYMMDD'})) & \
       (~df_variables['Varname'].isin(binary_variables)) & \
       (~df_variables['Varname'].isin(categorical_variables))]
    df_variables =  df_variables[~df_variables['Varname'].str.lower().str.endswith('_onset_year')]

    df_samples = pd.read_csv(args.in_samples, sep = '\t', header = 0, low_memory = False, usecols = ['IID'])
    df_pheno = pd.read_csv(args.in_phenotypes, sep = ',', header = 0, low_memory = False)
    df_pheno = df_pheno[df_pheno.PROJECT_CODE.isin(df_samples['IID'])].copy()
    assert len(df_pheno) == len(df_samples)

    df_variables_final = pd.DataFrame(filter_continuous_variables(df_variables, variable_missing_codes, df_pheno))
    df_variables_final['Length'] = df_variables_final['[Hidden] problem'].apply(len)  # Create a new column with lengths
    sorted_df = df_variables_final.sort_values(by='Length', ascending=False)
    sorted_df = sorted_df.drop('Length', axis=1)

    df_variables_final.to_csv(f'{args.out_prefix}.summary.tsv', sep = '\t', header = True, index = False)
    sorted_df.to_json(f'{args.out_prefix}.json', orient='records')
