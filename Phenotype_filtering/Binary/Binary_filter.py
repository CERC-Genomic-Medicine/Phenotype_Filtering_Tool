#!/usr/bin/python3

'''
AUTHOR: Vincent Chapdelaine <vincent.chapdelaine@mcgill.ca>
Modified from a Daniel Taliun script.
VERSION: 1.0 (beta)
YEAR: 2023

Goal to filter Binary Variables. works in tendem with the Filtering_tool_Binairy.html

'''

import pandas as pd
import argparse
import seaborn as sns
import matplotlib.pyplot as plt

argparser = argparse.ArgumentParser(description = 'Prepares summary stats about binary phenotypes in the CARTaGENE study.')
argparser.add_argument('-c', '--catalog', metavar = 'name', dest = 'in_catalog_spreadsheet', type = str, required = True, help = 'Excel spreadsheet "COMBINED_CATALOG_*.xlsx". It contains meta-information about all variables and the following sheets: "COMBINED_CATALOG", "Categories", "Linear data missing codes".')
argparser.add_argument('-p', '--phenotypes', metavar = 'name', dest = 'in_phenotypes', type = str, required = True, help = 'CSV file with phenotype values for each sample in the CARTaGENE study.')
argparser.add_argument('-s', '--samples', metavar = 'name', dest = 'in_samples', type = str, required = True, help = 'List of individual IDs to consider (e.g. PLINK\'s *.psam file). The individual IDs must be in the column named "IID".')
argparser.add_argument('-j', '--json', metavar = 'name', dest = 'in_json', type = str, required = False, help = ' (optional, Json file with variables [To exclude, Sex-Specific, Choice_Sex-Specific] to filter.')
argparser.add_argument('-i', '--images', dest = 'pics', action='store_true', help = 'produce age distributions')
argparser.add_argument('-f', '--Final', dest = 'final', action='store_true', help = 'produce phenotype file with json file modification')
argparser.add_argument('-o', '--output', metavar = 'name', dest = 'out_prefix', type = str, required = True, help = 'Prefix for output files.')


catalog_sheet = 'Categories'
categories = {'yes', 'no', 'missing', 'no answer'}

##Evaluating what correspond to yes no missing and no answer
def filter_binary_variables(df):
    for name, group in df.groupby(["SURVEY", "DOMAIN", "VARIABLE"]):
        if len(group) != 4: # Skip if not 4 values
            continue
        if not all(str(c).lower() in categories for c in group.CATEGORY):
            continue
        yes_code = group[group.CATEGORY.str.lower() == 'yes'].CODE.values[0]
        no_code = group[group.CATEGORY.str.lower() == 'no'].CODE.values[0]
        noanswer_code = group[group.CATEGORY.str.lower() == 'no answer'].CODE.values[0]
        missing_code = group[group.CATEGORY.str.lower() == 'missing'].CODE.values[0]
        yield {'SURVEY': name[0], 'DOMAIN': name[1], 'VARIABLE': name[2], 'CODE_YES': yes_code, 'CODE_NO': no_code, 'CODE_NOANSWER': noanswer_code, 'CODE_MISSING': missing_code}

## Analysing phenotypes
def lookup_cases_controls(df_variables, df_pheno, df_pheno_final, sex):
    for index, row in df_variables.iterrows():
        variable = row.VARIABLE
        if variable not in df_pheno.columns:
            continue
        if variable in df_pheno_final.columns:
            continue
        
        codes_map = {
           row.CODE_YES: 1,
           row.CODE_NO: 0
        }

        df_pheno_cut = df_pheno[['SEX_BIRTH','P_AGE', variable]].copy()
        N_noanswer=sum(df_pheno_cut[variable] == row['CODE_NOANSWER']) # for description purpose
        N_missing=sum(df_pheno_cut[variable] == row['CODE_MISSING']) # for description purpose
        df_pheno_cut['RECODED'] = df_pheno_cut[variable].apply(lambda x: codes_map.get(x, None))

        df_all = df_pheno_cut[df_pheno_cut.RECODED.isin({0, 1})]
        
        if sex =='Males':
            df_pheno_all[df_all.SEX_BIRTH == 1,RECODED] = None
        elif sex =='Females':
            df_pheno_all[df_all.SEX_BIRTH == 0,RECODED] = None

        df_males = df_all[df_all.SEX_BIRTH == 0]
        df_females = df_all[df_all.SEX_BIRTH == 1]

        n_total = len(df_all)
        n_males = len(df_males)
        n_females = len(df_females)

        if args.pics and not df_all.empty :
            binary_plot(df_males.copy(),df_females.copy(),variable)
            pie_plot(df_males.copy(),df_females.copy(),variable)

        df_pheno_final[variable] = df_all.RECODED.copy()

        n_cases = len(df_all[df_all.RECODED == 1])
        n_cases_males = len(df_males[df_males.RECODED == 1])
        n_cases_females = len(df_females[df_females.RECODED == 1])

        n_controls = len(df_all[df_all.RECODED == 0])

        ## Identification of easily detectable issues
        flag=[]

        if (n_total<1000):
            flag.append('Too few samples in totals')
        if (n_cases<10):
            flag.append('Too few cases')
        elif (n_cases_males<5):
            flag.append('Sex-Specific (females) ?')
        elif (n_cases_females<5):
            flag.append('Sex-Specific (males)?')
        if (n_controls <10):
            flag.append('Too few controls')

        
        yield({'[Description] Domain': row.DOMAIN, '[Description] Variable': variable,'[Description] Label': lexico[variable], '[Statistics] Total': n_total, '[Statistics] Males': n_males, '[Statistics] Females': n_females, '[Statistics] Cases': n_cases, '[Statistics] Controls': n_controls, '[Statistics] Males Cases': n_cases_males, '[Statistics] Females Cases': n_cases_females, '[Statistics] No Answer' : N_noanswer, '[Statistics] Missing' : N_missing, '[Hidden] problem' :  flag})


### plotting a sex and case-status stratified density plot.
def binary_plot(males,females,variable) : ##
    i='RECODED'
    if females.empty : # if sex-specific male
        fig, axes = plt.subplots(1,1, figsize=(10, 10))
        plt.rcParams.update({'font.size': 12})
        males.loc[males[i]==0,i]='Controls'
        males.loc[males[i]==1,i]='Cases'
        sns.kdeplot(data= males, x='P_AGE', hue=i, ax=axes, fill=True)
        axes.set_xlabel('Age (Years)')
        axes.set_ylabel('Count')
        axes.set_title(lexico[variable] + ' (Male trait)',size=17, wrap=True)
    elif males.empty :  # if sex-specific female
        fig, axes = plt.subplots(1,1, figsize=(10, 10))
        plt.rcParams.update({'font.size': 12})
        females.loc[females[i]==0,i]='Controls'
        females.loc[females[i]==1,i]='Cases'
        sns.kdeplot(data= females, x='P_AGE', hue=i, ax=axes, fill=True)
        axes.set_xlabel('Age (Years)')
        axes.set_ylabel('Count')
        axes.set_title(lexico[variable] + ' (Female trait)',size=17, wrap=True)
    else:
        fig, axes = plt.subplots(1,2, figsize=(10, 20))
        plt.rcParams.update({'font.size': 12})
        males.loc[males[i]==0,i]='Controls'
        males.loc[males[i]==1,i]='Cases'
        females.loc[females[i]==0,i]='Controls'
        females.loc[females[i]==1,i]='Cases'
        sns.kdeplot(data= males, x='P_AGE', hue=i, ax=axes[0], fill=True)
        axes[0].set_xlabel('Age (Years)')
        axes[0].set_ylabel('Count')
        axes[0].set_title(lexico[variable] + ' (Males)',size=17, wrap=True)
        sns.kdeplot(data= females, x='P_AGE', hue=i, ax=axes[1],fill=True)
        axes[1].set_xlabel('Age (Years)')
        axes[1].set_ylabel('Count')
        axes[1].set_title(lexico[variable] + ' (Females)',size=17, wrap=True)
    fig.savefig(variable + '_age_phenotype.png', dpi=300)
    plt.close(fig)
    plt.close('all')

### plotting a sex stratified pie chart.
def pie_plot(males,females,variable):
    i='RECODED'
    if females.empty : # if sex-specific male
        fig, axes = plt.subplots(1,1, figsize=(8, 8))
        plt.rcParams.update({'font.size': 12})
        Controls_males = len(males[i][males[i]==0])
        Cases_males = len(males[i][males[i]==1])
        axes.pie([Controls_males,Cases_males], labels=['Controls', 'Cases'], autopct='%1.1f%%', shadow=False)
        axes.set_title(lexico[variable] + ' (Male trait)',size=17, wrap=True)
    elif males.empty : # if sex-specific female
        fig, axes = plt.subplots(1,1, figsize=(8, 8))
        plt.rcParams.update({'font.size': 12})
        Controls_females = len(females[i][females[i]==0])
        Cases_females = len(females[i][females[i]==1])
        axes.pie([Controls_females,Cases_females], labels=['Controls', 'Cases'], autopct='%1.1f%%', shadow=False)
        axes.set_title(lexico[variable] + ' (Female trait)',size=17, wrap=True)
    else:
        fig, axes = plt.subplots(2,1, figsize=(10, 20))
        plt.rcParams.update({'font.size': 12})
        Controls_males = len(males[i][males[i]==0])
        Cases_males = len(males[i][males[i]==1])
        Controls_females = len(females[i][females[i]==0])
        Cases_females = len(females[i][females[i]==1])
        axes[0].pie([Controls_males,Cases_males], labels=['Controls', 'Cases'], autopct='%1.1f%%', shadow=True)
        axes[0].set_title(lexico[variable] + ' (Males)',size=17, wrap=True)
        axes[1].pie([Controls_females,Cases_females], labels=['Controls', 'Cases'], autopct='%1.1f%%', shadow=True)
        axes[1].set_title(lexico[variable] + ' (Females)',size=17, wrap=True)
    fig.savefig(variable + '_pie_phenotype.png', dpi=300)
    plt.close(fig)
    plt.close('all')



if __name__ == '__main__':
    args = argparser.parse_args()
    df = pd.read_excel(args.in_catalog_spreadsheet, sheet_name = catalog_sheet)
    lexico = pd.read_excel(args.in_catalog_spreadsheet, sheet_name = 'COMBINED_CATALOG')[['Varname','LABEL_ENGLISH']] #obtaining more detailed label
    lexico = dict(zip(lexico['Varname'],lexico['LABEL_ENGLISH'])) #obtaining more detailed label
    df_codes_only = df[["SURVEY", "DOMAIN", "VARIABLE", "CODE", "CATEGORY"]]
    if args.in_json :
        json_df = pd.read_json(args.in_json)
        exclusion_list = json_df.loc[json_df['To exclude']==True,'VARIABLE']
        females_only = json_df.loc[(json_df['Sex-Specific']==True) & (json_df['Choice_Sex-Specific']=='Females'),'VARIABLE']
        males_only = json_df.loc[(json_df['Sex-Specific']==True) & (json_df['Choice_Sex-Specific']=='Males'),'VARIABLE']
        unisex = json_df.loc[~(json_df['Sex-Specific']==True),'VARIABLE']
        df_unisex = df_codes_only.loc[~df_codes_only['VARIABLE'].isin(unisex),:]
        df_females_only = df_codes_only.loc[~df_codes_only['VARIABLE'].isin(females_only),:]
        df_males_only = df_codes_only.loc[~df_codes_only['VARIABLE'].isin(males_only),:]
        df_variables_uni = pd.DataFrame(filter_binary_variables(df_unisex))
        df_variables_male = pd.DataFrame(filter_binary_variables(df_males_only ))
        df_variables_female = pd.DataFrame(filter_binary_variables(df_females_only))

    else :
        df_variables = pd.DataFrame(filter_binary_variables(df_codes_only))

    df_samples = pd.read_csv(args.in_samples, sep = '\t', header = 0, low_memory = False, usecols = ['IID'])
    df_pheno = pd.read_csv(args.in_phenotypes, sep = ',', header = 0, low_memory = False)
    df_pheno = df_pheno[df_pheno.PROJECT_CODE.isin(df_samples['IID'])].copy()

    assert len(df_pheno) == len(df_samples)
    
    if args.in_json:
        df_pheno_males = pd.DataFrame({'FID': df_pheno.PROJECT_CODE, 'IID': df_pheno.PROJECT_CODE})
        df_pheno_females = pd.DataFrame({'FID': df_pheno.PROJECT_CODE, 'IID': df_pheno.PROJECT_CODE})
        df_pheno_uni = pd.DataFrame({'FID': df_pheno.PROJECT_CODE, 'IID': df_pheno.PROJECT_CODE})
        df_variables_males = pd.DataFrame(lookup_cases_controls(df_variables_male, df_pheno, df_pheno_males,'Males'))
        df_variables_females = pd.DataFrame(lookup_cases_controls(df_variables_female, df_pheno, df_pheno_females,'Females'))
        df_variables_uni = pd.DataFrame(lookup_cases_controls(df_variables_uni, df_pheno, df_pheno_uni,'Unisex'))
        df_pheno_uni.to_csv(f'{args.out_prefix}.unisex.pheno', sep = '\t', header = True, index = False, na_rep = 'NA', float_format = '%.0f')
        df_pheno_males.to_csv(f'{args.out_prefix}.males.pheno', sep = '\t', header = True, index = False, na_rep = 'NA', float_format = '%.0f')
        df_pheno_females.to_csv(f'{args.out_prefix}.females.pheno', sep = '\t', header = True, index = False, na_rep = 'NA', float_format = '%.0f')
        df_variables_uni.to_csv(f'{args.out_prefix}.unisex..summary.tsv', sep = '\t', header = True, index = False, na_rep = 'NA')
        df_variables_males.to_csv(f'{args.out_prefix}.males.summary.tsv', sep = '\t', header = True, index = False, na_rep = 'NA')
        df_variables_females.to_csv(f'{args.out_prefix}.females.summary.tsv', sep = '\t', header = True, index = False, na_rep = 'NA')
    else :
        df_pheno_final = pd.DataFrame({'FID': df_pheno.PROJECT_CODE, 'IID': df_pheno.PROJECT_CODE})
        df_variables_final = pd.DataFrame(lookup_cases_controls(df_variables, df_pheno, df_pheno_final,''))
        df_variables_final.to_json(f'{args.out_prefix}.summary.json',orient='records')

