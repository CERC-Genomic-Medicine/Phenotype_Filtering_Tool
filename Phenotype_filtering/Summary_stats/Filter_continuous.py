import numexpr as ne
import pandas as pd
import warnings
import argparse
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew
from scipy.stats import rankdata, norm
import statsmodels.api as sm
import matplotlib as matplotlib

plt.rcParams.update({'font.size': 20})
matplotlib.rc('xtick', labelsize=20)
matplotlib.rc('ytick', labelsize=20)

argparser = argparse.ArgumentParser(description='Prepares summary stats about continuous phenotypes in the CARTaGENE study.')
argparser.add_argument('-p', '--phenotypes', metavar='name', dest='in_phenotypes', type=str, required=True, help='CSV file with phenotype values for each sample in the CARTaGENE study.')
argparser.add_argument('-s', '--samples', metavar='name', dest='in_samples', type=str, required=True, help='List of individual IDs to consider (e.g. PLINK\'s *.psam file). The individual IDs must be in the column named "IID".')
argparser.add_argument('-o', '--output', metavar='name', dest='out_prefix', type=str, required=True, help='Prefix for output files.')
argparser.add_argument('-j', '--json', metavar='name', dest='json', type=str, required=True, help='JSON file with inclusion/exclusion and curation parameters.')


def rint(values):
    """Rank-inverse normal transformation."""
    c = 3/8
    rank = rankdata(values)
    x = (rank - c) / (len(rank) - 2*c + 1)
    return norm.ppf(x)


def normalize_columns(df, skip_cols=('FID', 'IID', 'SEX_BIRTH')):
    """Apply rint normalization to all columns except skip_cols."""
    df_norm = df.copy()
    for col in df_norm.columns:
        if col in skip_cols:
            continue
        non_null_idx = df_norm[col].dropna().index
        if len(non_null_idx) > 1:
            df_norm.loc[non_null_idx, col] = rint(df_norm.loc[non_null_idx, col].values)
    return df_norm


def plot(df, row, meaned, sd):
    recoded = df.loc[~df[row['[Description] Variable']].isna(), row['[Description] Variable']]
    print(row['[Description] Variable'])
    maxVal, minVal = np.nanmax(recoded), np.nanmin(recoded)
    ranged = (maxVal - minVal) / 100
    ulim, llim = maxVal + ranged, minVal - ranged
    f, axes = plt.subplots(2, 3, height_ratios=[3, 1], figsize=(33, 10))
    try:
        sns.histplot(recoded, ax=axes[0, 0])
    except np.core._exceptions._ArrayMemoryError:
        sns.kdeplot(recoded, ax=axes[0, 0])
    axes[0, 0].set_xlim(llim, ulim)
    axes[1, 0].boxplot(recoded, vert=False)
    axes[1, 0].set_xlim(llim, ulim)
    if sd != 0:
        S = skew(recoded)
        SS = skew(recoded[(recoded > meaned - 2 * sd) & (recoded < meaned + 2 * sd)])
        SSS = skew(recoded[(recoded > meaned - 3 * sd) & (recoded < meaned + 3 * sd)])
        axes[0, 0].annotate(
            f"Skewness = {S:.3f}\nSkewness (without outlier 2sd) = {SS:.3f}\nSkewness (without outlier 3sd) = {SSS:.3f}",
            xy=(0.01, .99), xycoords='axes fraction', textcoords='axes fraction',
            va='top', ha='left', fontsize='medium'
        )
    try:
        sns.histplot(rint(recoded), ax=axes[0, 1])
    except np.core._exceptions._ArrayMemoryError:
        sns.kdeplot(rint(recoded), ax=axes[0, 1])
    axes[1, 1].boxplot(rint(recoded), vert=False)
    axes[0, 0].set_xlabel('Distribution')
    axes[0, 1].set_xlabel('Normalized distribution')
    sm.qqplot(recoded, fit=True, ax=axes[0, 2])
    f.delaxes(axes[1, 2])
    plt.suptitle(f'Phenotype Distribution \n {row["[Description] Label"]}', size=24)
    f.savefig(f'{row["[Description] Variable"]}.png', dpi=300)
    plt.close(f)
    del f


def before_after_plot(before, after, row):
    f, axes = plt.subplots(1, 2, figsize=(20, 10))
    missing = pd.to_numeric(row['[Description] Missing code'].split('|'))
    before = np.where([pd.to_numeric(num) in missing for num in before], np.nan, before)
    maxValBefore, minValBefore = np.nanmax(before), np.nanmin(before)
    maxValAfter, minValAfter = np.nanmax(after), np.nanmin(after)
    units = row['[Description] Unit'] if row['[Description] Unit'] != '' else 'Units'
    ranged = (maxValBefore - minValBefore) / 100
    ulim, llim = maxValBefore + ranged, minValBefore - ranged
    before = pd.Series(before)
    after = pd.Series(after)
    n = sum(~before.isna())
    n2 = sum(~after.isna())
    try:
        sns.histplot(before, ax=axes[0])
    except np.core._exceptions._ArrayMemoryError:
        sns.kdeplot(before, ax=axes[0])
    axes[0].set_xlim(llim, ulim)
    try:
        sns.histplot(after, ax=axes[1])
    except np.core._exceptions._ArrayMemoryError:
        sns.kdeplot(after, ax=axes[1])
    ranged = (maxValAfter - minValAfter) / 100
    ulim, llim = maxValAfter + ranged, minValAfter - ranged
    axes[1].set_xlim(llim, ulim)
    axes[0].set_title('Uncurated', fontsize=20)
    axes[1].set_title('Curated', fontsize=20)
    axes[0].set_xlabel(units, fontsize=20)
    axes[1].set_xlabel(units, fontsize=20)
    axes[0].text(0.95, 0.95, f'N = {n}', horizontalalignment='right', verticalalignment='top', transform=axes[0].transAxes, fontsize=24)
    axes[1].text(0.95, 0.95, f'N = {n2}', horizontalalignment='right', verticalalignment='top', transform=axes[1].transAxes, fontsize=24)
    plt.suptitle(f'Phenotype Distribution \n {row["[Description] Label"]}', size=24)
    f.savefig(f'{row["[Description] Variable"]}_curation.png', dpi=300)
    plt.close(f)
    del f


def filter_phenotypes(df_pheno, json):
    df = df_pheno.copy()

    # OPTIMIZATION 1: drop all excluded variables upfront before the main loop
    to_exclude = json.loc[json['To_exclude'] == True, '[Description] Variable'].tolist()
    cols_to_drop = [v for v in to_exclude if v in df.columns]
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)
        print(f"Excluded upfront: {cols_to_drop}")

    # Only iterate over rows that are active (not excluded, not SEX_BIRTH)
    active_rows = json[
        (json['To_exclude'] != True) &
        (json['[Description] Variable'] != 'SEX_BIRTH') &
        (json['[Description] Variable'].notna()) &
        (json['[Description] Variable'] != '')
    ]

    records = []

    for index, row in active_rows.iterrows():
        var = row['[Description] Variable']
        if var not in df.columns:
            print(f"Warning: {var} not found in phenotype data, skipping.")
            continue

        print(var)

        # OPTIMIZATION 3: parse and cache missing codes once per variable
        missing_str = row['[Description] Missing code']
        missing = pd.to_numeric(missing_str.split("|")) if missing_str else []

        df[var] = np.where(
            [pd.to_numeric(num) in missing for num in df[var]],
            np.nan, df[var]
        )

        # Adjustment
        if row['Adjustement']:
            if 'var_Adjustement' in row.index and row['var_Adjustement'] in df_pheno.columns:
                X = np.where(~(df_pheno[row['var_Adjustement']] == 1), False, df_pheno[row['var_Adjustement']])
                X_var_Adjustement = (X == 1)
            if missing_str:
                missing_numeric = pd.to_numeric(missing_str.split("|"))
                Y = np.where(
                    [pd.to_numeric(num) in missing_numeric for num in df_pheno[var]],
                    np.nan, df_pheno[var]
                )
                Y_var_Adjusted = ~np.isnan(Y)
            else:
                Y = df_pheno[var]
                Y_var_Adjusted = ~Y.isna()
            expression = row['form_Adjustement']
            df[var] = ne.evaluate(expression, local_dict={'X': X, 'Y': Y})
            N_ajusted = sum(X_var_Adjustement & Y_var_Adjusted)
            adjustement_formula = expression.translate(str.maketrans({'X': row['var_Adjustement'], 'Y': var}))
        else:
            N_ajusted = 'NA'
            adjustement_formula = 'NA'

        if row['Remove_Zeros']:
            zero_removed = sum(df[var] == 0)
            df.loc[df[var] == 0, var] = np.nan
        else:
            zero_removed = 'NA'

        SD = np.nanstd(df[var])
        MEAN = np.nanmean(df[var])
        maxVal, minVal = np.nanmax(df[var]), np.nanmin(df[var])

        if 'Threshold_Right' in row.index and row['Threshold_Right'] != 'none':
            Right_Threshold_removed = sum(pd.to_numeric(df[var]) >= (int(row['Threshold_Right']) * SD + MEAN))
            df.loc[pd.to_numeric(df[var]) >= (int(row['Threshold_Right']) * SD + MEAN), var] = np.nan
        else:
            Right_Threshold_removed = 'NA'

        if 'Threshold_Left' in row.index and row['Threshold_Left'] != 'none':
            Left_Threshold_removed = sum(pd.to_numeric(df[var]) <= (-int(row['Threshold_Left']) * SD + MEAN))
            df.loc[pd.to_numeric(df[var]) <= (-int(row['Threshold_Left']) * SD + MEAN), var] = np.nan
        else:
            Left_Threshold_removed = 'NA'

        PERC_5, PERC95 = np.nanpercentile(df[var], [5, 95])
        min_value = np.nanmin(df[var])
        max_value = np.nanmax(df[var])
        median_value = df[var].median()
        value_counts = df[var].value_counts()
        mode_freq = value_counts.values[0]
        mode_value = value_counts.index[0]
        n_unique = len(value_counts.index)
        n_total = sum(~df[var].isna())
        n_males = sum(~df.loc[df['SEX_BIRTH'] == 0, var].isna())
        n_females = sum(~df.loc[df['SEX_BIRTH'] == 1, var].isna())
        deltaMaxVal = np.nanmax(df[var]) - maxVal
        deltaMinVal = np.nanmin(df[var]) - minVal

        records.append({
            '[Description] Variable': var,
            '[Curated] Total': n_total,
            '[Curated] Males': n_males,
            '[Curated] Females': n_females,
            '[Curated] Minimum': min_value,
            '[Curated] Maximum': max_value,
            '[Curated] N uniques values': n_unique,
            '[Curated] PERC_5': PERC_5,
            '[Curated] median': median_value,
            '[Curated] PERC_95': PERC95,
            '[Curated] Mean': MEAN,
            '[Curated] SD': SD,
            '[Curated] Mode': mode_value,
            '[Curated] Mode frequency': mode_freq,
            '[Curation] Formula': adjustement_formula,
            '[Curation] N Adjusted': N_ajusted,
            '[Curation] Right threshold removed': Right_Threshold_removed,
            '[Curation] Left threshold removed': Left_Threshold_removed,
            '[Curation] Delta Maximum ': deltaMaxVal,
            '[Curation] Delta Minimum': deltaMinVal
        })

        before_after_plot(df_pheno[var], df[var], row)
        plot(df, row, MEAN, SD)

    change_df = pd.DataFrame(records)

    if change_df.empty:
        return pd.DataFrame(), change_df

    curated_vars = change_df['[Description] Variable'].tolist()
    cols_to_keep = (['SEX_BIRTH'] if 'SEX_BIRTH' in df.columns else []) + curated_vars
    df = df[cols_to_keep]
    return df, change_df


def save_group(df_curated, variables, sex_group, not_normalize, out_prefix):
    """
    Save a phenotype TSV for a specific (sex_group, normalization) combination.
      sex_group   : 'unisex' | 'Males' | 'Females'
      not_normalize: True → write raw values; False → apply rint normalization
    """
    available = [v for v in variables if v in df_curated.columns]
    if not available:
        return

    # Filter samples by sex group
    if sex_group == 'Males':
        df_out = df_curated.loc[df_curated['SEX_BIRTH'] == 0, available].copy()
        sex_suffix = 'males'
    elif sex_group == 'Females':
        df_out = df_curated.loc[df_curated['SEX_BIRTH'] == 1, available].copy()
        sex_suffix = 'females'
    else:
        df_out = df_curated[available].copy()
        sex_suffix = 'unisex'

    norm_suffix = 'raw' if not_normalize else 'normalized'

    # Apply rint normalization column by column if requested
    if not not_normalize:
        df_out = normalize_columns(df_out)

    df_out.insert(0, 'IID', df_out.index)
    df_out.insert(0, 'FID', df_out.index)

    out_path = f'{out_prefix}_{sex_suffix}_{norm_suffix}_phenotype.tsv'
    df_out.to_csv(out_path, sep='\t', index=False, na_rep='NA')
    print(f"Saved: {out_path}  ({len(df_out)} samples, {len(available)} variables)")


if __name__ == '__main__':
    args = argparser.parse_args()

    df_samples = pd.read_csv(args.in_samples, sep='\t', header=0, low_memory=False, usecols=['IID'])
    df_pheno = pd.read_csv(args.in_phenotypes, sep=',', header=0, low_memory=False)
    df_pheno = df_pheno[df_pheno.PROJECT_CODE.isin(df_samples['IID'])].copy()
    df_pheno.index = df_pheno.PROJECT_CODE
    df_pheno.columns = [i.upper() for i in df_pheno.columns]

    json = pd.read_json(args.json)
    json['[Description] Variable'] = json['[Description] Variable'].str.upper()

    df_pheno_curated, df_json_curated = filter_phenotypes(df_pheno, json)

    # --- Summary CSV ---
    filtered_columns = [col for col in json.columns if col.startswith('[Description]') or col.startswith('[Samples]') or col.startswith('[Statistics]')]
    ordered_columns = sorted(filtered_columns, key=lambda x: ['[Description]', '[Samples]', '[Statistics]'].index(x.split(' ')[0]))
    json_summary = json[ordered_columns]
    json_summary.merge(df_json_curated, on='[Description] Variable', how='inner').to_csv(f'{args.out_prefix}_summary.csv', index=False)

    # --- Per-group phenotype files ---
    # Active (non-excluded, non-SEX_BIRTH) rows from json, matched to curated variables
    curated_vars = set(df_json_curated['[Description] Variable'].tolist())
    active = json[
        (json['To_exclude'] != True) &
        (json['[Description] Variable'] != 'SEX_BIRTH') &
        (json['[Description] Variable'].isin(curated_vars))
    ].copy()

    # Groups are all combinations of (Sex-Specific, Choice_Sex-Specific, Not_normalize)
    # Sex-Specific=False → 'unisex' regardless of Choice_Sex-Specific
    # Sex-Specific=True  → 'Males' or 'Females' from Choice_Sex-Specific
    groups = {}
    for _, row in active.iterrows():
        var = row['[Description] Variable']
        sex_specific = bool(row.get('Sex-Specific', False))
        not_normalize = bool(row.get('Not_normalize', False))

        if sex_specific:
            sex_group = row.get('Choice_Sex-Specific', 'unisex')
            if sex_group not in ('Males', 'Females'):
                sex_group = 'unisex'
        else:
            sex_group = 'unisex'

        key = (sex_group, not_normalize)
        groups.setdefault(key, []).append(var)

    for (sex_group, not_normalize), variables in sorted(groups.items()):
        save_group(df_pheno_curated, variables, sex_group, not_normalize, args.out_prefix)