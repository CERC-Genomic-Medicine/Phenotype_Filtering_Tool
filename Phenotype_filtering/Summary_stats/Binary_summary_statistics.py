import pandas as pd
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import sys

argparser = argparse.ArgumentParser(description = 'Prepares summary stats about binary phenotypes in the CARTaGENE study.')
argparser.add_argument('-c', '--catalog', metavar = 'name', dest = 'in_catalog_spreadsheet', type = str, required = True, help = 'Excel spreadsheet "COMBINED_CATALOG_*.xlsx". It contains meta-information about all variables and the following sheets: "COMBINED_CATALOG", "Categories", "Linear data missing codes".')
argparser.add_argument('-p', '--phenotypes', metavar = 'name', dest = 'in_phenotypes', type = str, required = True, help = 'CSV file with phenotype values for each sample in the CARTaGENE study.')
argparser.add_argument('-s', '--samples', metavar = 'name', dest = 'in_samples', type = str, required = True, help = 'List of individual IDs to consider (e.g. PLINK\'s *.psam file). The individual IDs must be in the column named "IID".')
argparser.add_argument('-j', '--json', metavar = 'name', dest = 'in_json', type = str, required = '--Final' in sys.argv or '-f' in sys.argv , help = ' (optional, Json file with inclusion and exclusion.')
argparser.add_argument('-i', '--images', dest = 'pics', action='store_true', help = 'produce age distributions')
argparser.add_argument('-f', '--Final', dest = 'final', action='store_true', help = 'produce phenotype file with json file modification')
argparser.add_argument('-o', '--output', metavar = 'name', dest = 'out_prefix', type = str, required = True, help = 'Prefix for output files.')
argparser.add_argument('-n', '--n_threshold', metavar = 'value', dest = 'n_threshold', type = int, default=1000, help = 'Threshold at which the number of Sample problem flag is raised ')
argparser.add_argument('--c_threshold', metavar = 'value', dest = 'cases_threshold', type = int, default=10, help = 'Threshold at which the number of Sample problem flag is raised ')
argparser.add_argument('-ss', '--SS_threshold', metavar = 'value', dest = 'ss_threshold', type = int, default=5, help = 'Threshold at which the number of Sex-Specific problem flag is raised')

catalog_sheet = 'Categories'
categories = {'yes', 'no', 'missing', 'no answer'}

plt.rcParams.update({'font.size': 25})
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


def lookup_cases_controls(df_variables, df_pheno, df_pheno_final, sex):
    for index, row in df_variables.iterrows():
        variable = row.VARIABLE
        if variable not in df_pheno.columns:
            continue
        if variable in df_pheno_final.columns:
            continue
        
        codes_map = {
           row.CODE_YES: 1,
           row.CODE_NO: 0,
           row.CODE_NOANSWER : -1,
           row.CODE_MISSING : -2
        }

        df_pheno_cut = df_pheno[['SEX_BIRTH','P_AGE', variable]].copy()
        N_noanswer=len(df_pheno_cut[df_pheno_cut[variable] == row['CODE_NOANSWER']])
        N_missing=len(df_pheno_cut[df_pheno_cut[variable] == row['CODE_MISSING']])
        Unique_values=pd.unique(df_pheno_cut[variable])

        df_pheno_cut['RECODED'] = df_pheno_cut[variable].apply(lambda x: codes_map.get(x, None))
        N_NA=len(df_pheno_cut.RECODED[df_pheno_cut['RECODED'].isna()])
        if args.pics :
            bar_plot(df_pheno_cut[df_pheno_cut.SEX_BIRTH == 0].copy(),df_pheno_cut[df_pheno_cut.SEX_BIRTH == 1].copy(),variable)
        
        df_all = df_pheno_cut[df_pheno_cut.RECODED.isin({0, 1})]
        df_males = df_all[df_all.SEX_BIRTH == 0]
        df_females = df_all[df_all.SEX_BIRTH == 1]
        
        if args.pics and not df_all.empty and args.final:
            if sex =='Males':
                df_pheno_all[df_all.SEX_BIRTH == 1,RECODED] = None
            elif sex =='Females':
                df_pheno_all[df_all.SEX_BIRTH == 0,RECODED] = None
            binary_plot(df_males.copy(),df_females.copy(),variable)

        n_total = len(df_all)
        n_males = len(df_males)
        n_females = len(df_females)


        df_pheno_final[variable] = df_all.RECODED.copy()

        n_cases = len(df_all[df_all.RECODED == 1])
        n_cases_males = len(df_males[df_males.RECODED == 1])
        n_cases_females = len(df_females[df_females.RECODED == 1])

        n_controls = len(df_all[df_all.RECODED == 0])
        n_controls_males = len(df_males[df_males.RECODED == 0])
        n_controls_females = len(df_females[df_females.RECODED == 0])
        flag=[]
        if (n_total<args.n_threshold):
            flag.append('Total number of samples below ' +str(args.n_threshold))
        if (n_cases<args.cases_threshold):
            flag.append('Number of cases below ' + str(args.cases_threshold))
        elif (n_cases_males<args.ss_threshold):
            flag.append('Sex-Specific (females) ?')
        elif (n_cases_females<args.ss_threshold):
            flag.append('Sex-Specific (males)?')
        
        yield({'[Description] Domain': row.DOMAIN, '[Description] Variable': variable,'[Description] Label': lexico[variable],'[Description] Type': 'Binary' ,'[Statistics] Total': n_total, '[Statistics] Males': n_males, '[Statistics] Females': n_females, '[Statistics] Cases': n_cases, '[Statistics] Controls': n_controls, '[Statistics] Males Cases': n_cases_males, '[Statistics] Females Cases': n_cases_females, '[Statistics] Males Controls': n_controls_males, '[Statistics] Females Controls' : n_controls_females,'[Statistics] No Answer' : N_noanswer, '[Statistics] Missing' : N_missing, '[Statistics] Other codes (NA assumed)' : N_NA,'[Codes] Missing' : row.CODE_MISSING, '[Codes] No answer' : row.CODE_NOANSWER, '[Codes] Yes ' : row.CODE_YES, '[Codes] No' : row.CODE_NO, '[Codes] Used Values' : ' | '.join([str(i) for i in Unique_values]), '[Hidden] problem' :  '|'.join(flag)})

def binary_plot(males,females,variable) : ##
    i='RECODED'
    if females.empty :
        fig, axes = plt.subplots(1,1, figsize=(10, 10))
        males.loc[males[i]==0,i]='Controls'
        males.loc[males[i]==1,i]='Cases'
        sns.kdeplot(data= males, x='P_AGE', hue=i, ax=axes, fill=True)
        axes.set_xlabel('Age (Years)')
        axes.set_ylabel('Count')
        axes.set_title(lexico[variable] + ' (Male trait)',size=17, wrap=True)
    elif males.empty :
        fig, axes = plt.subplots(1,1, figsize=(10, 10))
        females.loc[females[i]==0,i]='Controls'
        females.loc[females[i]==1,i]='Cases'
        sns.kdeplot(data= females, x='P_AGE', hue=i, ax=axes, fill=True)
        axes.set_xlabel('Age (Years)')
        axes.set_ylabel('Count')
        axes.set_title(lexico[variable] + ' (Female trait)',size=17, wrap=True)
    else:
        fig, axes = plt.subplots(1,2, figsize=(10, 20))
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

def bar_plot(males,females,variable):
    i='RECODED'
    fig, axes = plt.subplots(1,2, figsize=(20, 10))
    Controls_males = len(males[males[i]==0])
    Cases_males = len(males[males[i]==1])
    Controls_females = len(females[females[i]==0])
    Cases_females = len(females[females[i]==1])
    NA_males = len(males[males[i].isin({0, 1})])
    NA_females = len(females[females[i].isin({0, 1})])
    axes[0].bar(['Controls', 'Cases','Missing/Not Answered'],[Controls_males,Cases_males,NA_males],log=True)
    axes[0].set_title(lexico[variable] + '  (Males) ',size=28,wrap=True)
    axes[1].bar(['Controls', 'Cases','Missing/Not Answered'],[Controls_females,Cases_females,NA_females],log=True)
    axes[1].set_title(lexico[variable] + ' (Females)',size=28, wrap=True)
    axes[1].set_xticklabels(['Controls', 'Cases','Missing/Not Answered/NA'], rotation = 30, ha='right')
    plt.tight_layout()
    axes[0].set_xticklabels(['Controls', 'Cases','Missing/Not Answered/NA'], rotation = 30, ha='right')
    fig.savefig(variable + '_phenotype.png', dpi=300)
    plt.close(fig)
    plt.close('all')



if __name__ == '__main__':
    args = argparser.parse_args()
    df = pd.read_excel(args.in_catalog_spreadsheet, sheet_name = catalog_sheet)
    lexico = pd.read_excel(args.in_catalog_spreadsheet, sheet_name = 'COMBINED_CATALOG')[['Varname','LABEL_ENGLISH']]
    lexico = dict(zip(lexico['Varname'],lexico['LABEL_ENGLISH']))
    df_codes_only = df[["SURVEY", "DOMAIN", "VARIABLE", "CODE", "CATEGORY"]]
    df_variables = pd.DataFrame(filter_binary_variables(df_codes_only))

    df_samples = pd.read_csv(args.in_samples, sep = '\t', header = 0, low_memory = False, usecols = ['IID'])
    df_pheno = pd.read_csv(args.in_phenotypes, sep = ',', header = 0, low_memory = False)
    df_pheno = df_pheno[df_pheno.PROJECT_CODE.isin(df_samples['IID'])].copy()

    assert len(df_pheno) == len(df_samples)
    
    if args.in_json and args.final:
        json_df = pd.read_json(args.in_json)
        exclusion_list=json_df.loc[json_df['To exclude']==True,'VARIABLE']
        df_codes_only=df_codes_only.loc[~df_codes_only['VARIABLE'].isin(exclusion_list),:]
        females_only=json_df.loc[(json_df['Sex-Specific']==True) & (json_df['Choice_Sex-Specific']=='Females'),'VARIABLE']
        males_only=json_df.loc[(json_df['Sex-Specific']==True) & (json_df['Choice_Sex-Specific']=='Males'),'VARIABLE']
        unisex=json_df.loc[~(json_df['Sex-Specific']==True),'VARIABLE']
        df_pheno_males = pd.DataFrame({'FID': df_pheno.PROJECT_CODE, 'IID': df_pheno.PROJECT_CODE})
        df_pheno_females = pd.DataFrame({'FID': df_pheno.PROJECT_CODE, 'IID': df_pheno.PROJECT_CODE})
        df_pheno_uni = pd.DataFrame({'FID': df_pheno.PROJECT_CODE, 'IID': df_pheno.PROJECT_CODE})
        df_variables_males = pd.DataFrame(lookup_cases_controls(df_variables, df_pheno, df_pheno_males,'Males'))
        df_variables_females = pd.DataFrame(lookup_cases_controls(df_variables, df_pheno, df_pheno_females,'Females'))
        df_variables_uni = pd.DataFrame(lookup_cases_controls(df_variables, df_pheno, df_pheno_uni,'Unisex'))
        df_pheno_uni.to_csv(f'{args.out_prefix}.unisex.pheno', sep = '\t', header = True, index = False, na_rep = 'NA', float_format = '%.0f')
        df_pheno_males.to_csv(f'{args.out_prefix}.males.pheno', sep = '\t', header = True, index = False, na_rep = 'NA', float_format = '%.0f')
        df_pheno_females.to_csv(f'{args.out_prefix}.females.pheno', sep = '\t', header = True, index = False, na_rep = 'NA', float_format = '%.0f')
        df_variables_uni.to_csv(f'{args.out_prefix}.unisex..summary.tsv', sep = '\t', header = True, index = False, na_rep = 'NA')
        df_variables_males.to_csv(f'{args.out_prefix}.males.summary.tsv', sep = '\t', header = True, index = False, na_rep = 'NA')
        df_variables_females.to_csv(f'{args.out_prefix}.females.summary.tsv', sep = '\t', header = True, index = False, na_rep = 'NA')
    else :
        df_pheno_final = pd.DataFrame({'FID': df_pheno.PROJECT_CODE, 'IID': df_pheno.PROJECT_CODE})
        df_variables_final = pd.DataFrame(lookup_cases_controls(df_variables, df_pheno, df_pheno_final,''))
        df_variables_final['Length'] = df_variables_final['[Hidden] problem'].apply(len)  # Create a new column with lengths
        sorted_df = df_variables_final.sort_values(by='Length', ascending=False)
        sorted_df = sorted_df.drop('Length', axis=1)
        sorted_df.to_json(f'{args.out_prefix}.summary.json',orient='records')

