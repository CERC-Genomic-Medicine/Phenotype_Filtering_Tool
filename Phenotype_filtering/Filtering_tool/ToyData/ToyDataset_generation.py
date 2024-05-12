import pandas as pd
import math
import warnings
import numpy as np
import sys
import random
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

########### Continuous

df_continuous = pd.DataFrame((np.random.randn(1000, 5)*100), columns=['First_Phenotype', 'First_Flagged Phenotype','Third_Phenotype','Fourth_Phenotype','Sex-Specific_Phenotype'])
df_continuous = round(df_continuous)
df_continuous.iloc[:,1] = 100
df_continuous.iloc[1,1] = 1
df_continuous['SEX_BIRTH']=1
df_continuous.loc[1:500,'SEX_BIRTH']=0
df_continuous.loc[1:500,'Sex-Specific_Phenotype']= None

df_variables = pd.DataFrame({'Varname': ['First_Phenotype', 'First_Flagged Phenotype','Third_Phenotype','Fourth_Phenotype','Sex-Specific_Phenotype'], 'database': ['Toy Dataset', 'Toy Dataset','Toy Dataset','Toy Dataset','Toy Dataset'], 'LABEL_ENGLISH': ['First Phenotype', 'First Flagged Phenotype','Third Phenotype','Fourth Phenotype','Sex-Specific Phenotype']})



plt.rcParams.update({'font.size': 20})

def rint(listed):
	c=3/8
	rank=rankdata(listed)
	x = (rank - c) / (len(rank) - 2*c + 1)
	return norm.ppf(x)

def plot(df,row,meaned,sd):
	#Raw Phenotype Distribution
	maxVal=np.nanmax(df.RECODED)
	minVal=np.nanmin(df.RECODED)
	f, axes = plt.subplots(2, 3, height_ratios=[3,1],figsize=(33, 10))
	try:
		sns.histplot(data=df, ax=axes[0,0], x="RECODED")
	except np.core._exceptions._ArrayMemoryError:
		sns.kdeplot(data=df, ax=axes[0,0], x="RECODED")
	axes[0,0].axvline(x=meaned,color='black')
	if sd !=0 :
		ulim = (maxVal + sd) if (maxVal > 5*sd+meaned) else (5*sd+sd+meaned)
		llim = (minVal - sd) if (minVal < meaned-5*sd) else (meaned-(5*sd)-sd)
	else :
		ulim = maxVal + 1
		llim = minVal - 1
	axes[0,0].set_xlim(llim, ulim)
	axes[1,0].boxplot(df.RECODED,vert=False)
	axes[1,0].set_xlim(llim, ulim)
	fold=2
	## Displays SD outlier values
	if sd != 0 :
		while (fold*sd+meaned < ulim) :
			axes[0,0].axvline(x=fold*sd+meaned,color='red')
			fold+=1
			if fold >5:
				break
		fold=2
		while (meaned-(fold*sd) > llim) :
			axes[0,0].axvline(x=meaned-(fold*sd),color='red')
			fold+=1
			if fold > 5:
				break
	axes[0,0].axes.get_xaxis().set_visible(False)
	axes[1,0].axes.get_yaxis().set_visible(False)
	plt.suptitle(f'Phenotype Distribution \n {row.LABEL_ENGLISH}',size=22)
	axes[0,0].set_ylabel('Count')
	axes[1,0].set_xlabel('Unit')
	## Normalized Values where appropriate
	if sd !=0 :
		normalized=rint(df.loc[:,'RECODED'])
		maxValn=np.nanmax(normalized)
		minValn=np.nanmin(normalized)
		try:
			sns.histplot(data=normalized, ax=axes[0,1])
		except np.core._exceptions._ArrayMemoryError:
			sns.kdeplot(data=normalized, ax=axes[0,1])
		axes[1,1].boxplot(normalized,vert=False)
		axes[1,1].set_xlim(minValn, maxValn)
		axes[0,1].set_xlim(minValn, maxValn)
		axes[0,1].set_ylabel('Count')
		axes[1,1].set_xlabel('Normalized Unit')
		axes[0,1].axes.get_xaxis().set_visible(False)
		axes[1,1].axes.get_yaxis().set_visible(False)
		separator=(maxVal-minVal)/100 # Display purposes
		separatorN=(maxValn-minValn)/100 # Display Purposes
		## Assess Skewness
		S=skew(df.RECODED, axis=0, bias=True)
		SS=skew(df.loc[(df.loc[:,'RECODED']>meaned-(2*sd)) & (df.loc[:,'RECODED']<meaned+(2*sd)) ,'RECODED'], axis=0, bias=True)
		SSS=skew(df.loc[(df.loc[:,'RECODED']>meaned-(3*sd)) & (df.loc[:,'RECODED']<meaned+(3*sd)) ,'RECODED'], axis=0, bias=True)
		axes[0,0].annotate("Skewness = {S:.3f} \n Skewness (without outlier 2sd) = {SS:.3f}  \n Skewness (without outlier 3sd) = {SSS:.3f} \n ".format(
		S=S,
		SS=SS,
		SSS=SSS), xy=(minVal+separator, 1), xycoords='data', xytext=(0.01, .99), textcoords='axes fraction', va='top', ha='left', fontsize='medium')
	## Provides QQ plot
	sm.qqplot(df.RECODED, line ='s',ax=axes[0,2])
	f.delaxes(axes[1,2])
	plt.suptitle(f'Phenotype Distribution \n {row.LABEL_ENGLISH}',size=24)
	f.savefig(f'{row.Varname}.png', dpi=300)
	plt.close(f)


def Outlier_evaluation (Series,sd,mean):
	sd_details={}
	for i in range(2,int(5)+1):
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


def filter_continuous_variables(df_variables,df_pheno):
	for index, row in df_variables.iterrows():
		variable = row['Varname']
		df_pheno_cut = df_pheno[['SEX_BIRTH', variable]].copy()
		df_pheno_cut['RECODED'] = df_pheno_cut[variable]
		mean = np.nanmean(df_pheno_cut.RECODED)
		df_not_missing = df_pheno_cut[~df_pheno_cut.RECODED.isna()]
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
			if n_total < 100 :
				problem.append('Total number of samples below ' + str(100))
			elif n_males < 5 :
				problem.append('Sex-Specific ?')
			elif n_females < 5 :
				problem.append('Sex-Specific ?')
			if mode_freq == 1 :
				problem.append('Mode frequency is 1')
			elif n_total - mode_freq == unique_values-1 :
				problem.append('Each values other than the mode appears only once')
			if unique_values < 10  :
				problem.append('Number of unique values below ' + str(10))
		yield {**{'[Description] Variable' : variable, '[Description] Domain':  row['database'], '[Description] Label' : row['LABEL_ENGLISH'], '[Samples] Total': n_total, '[Samples] Males' : n_males,  '[Samples] Females' : n_females,'[Statistics] Minimum': min_value, '[Statistics] Maximum' : max_value, '[Statistics] N unique values': unique_values, '[Statistics] PERC_5' : PERC_5, '[Statistics] median' : median_value, '[Statistics] PERC_95' : PERC95, '[Statistics] Mean': mean_value, '[Statistics] Mode': mode_value, '[Statistics] Mode frequency': mode_freq,'[Hidden] Skewness': S,'[Statistics] SD' : sd, '[Hidden] problem' : problem },** sd_details}


df_dummy_data = pd.DataFrame(filter_continuous_variables(df_variables, df_continuous))
df_dummy_data.to_json('Continuous_data.json', orient='records')


###### Binary


def bar_plot(males,females,variable):
	 i='RECODED'
	 Controls_males = len(males[males[i]==0])
	 Cases_males = len(males[males[i]==1])
	 Controls_females = len(females[females[i]==0])
	 Cases_females = len(females[females[i]==1])
	 NA_males = len(males[males[i].isin({0, 1})])
	 NA_females = len(females[females[i].isin({0, 1})])
	 if NA_males + Cases_males + Controls_males == 0 :
		  fig, axes = plt.subplots(1,1, figsize=(10, 10))
		  axes.bar(['Controls', 'Cases','Missing/Not Answered'],[Controls_females,Cases_females,NA_females],log=True)
		  axes.set_title(variable + ' (Females)',size=28, wrap=True)
		  axes.set_xticklabels(['Controls', 'Cases','Missing/Not Answered'], rotation = 30, ha='right')
		  plt.tight_layout()
		  fig.savefig(variable + '.png', dpi=300)
	 elif NA_females + Cases_females + Controls_females == 0 :
		  fig, axes = plt.subplots(1,1, figsize=(10, 10))
		  axes.bar(['Controls', 'Cases','Missing/Not Answered'],[Controls_males,Cases_males,NA_males],log=True)
		  axes.set_title(variable + '  (Males) ',size=28,wrap=True)
		  axes.set_xticklabels(['Controls', 'Cases','Missing/Not Answered'], rotation = 30, ha='right')
		  plt.tight_layout()
		  fig.savefig(variable + '.png', dpi=300)
	 else :
		  fig, axes = plt.subplots(1,2, figsize=(20, 10))
		  axes[0].bar(['Controls', 'Cases','Missing/Not Answered'],[Controls_males,Cases_males,NA_males],log=True)
		  axes[0].set_title(variable + '  (Males) ',size=28,wrap=True)
		  axes[1].bar(['Controls', 'Cases','Missing/Not Answered'],[Controls_females,Cases_females,NA_females],log=True)
		  axes[1].set_title(variable + ' (Females)',size=28, wrap=True)
		  axes[1].set_xticklabels(['Controls', 'Cases','Missing/Not Answered'], rotation = 30, ha='right')
		  plt.tight_layout()
		  axes[0].set_xticklabels(['Controls', 'Cases','Missing/Not Answered'], rotation = 30, ha='right')
		  fig.savefig(variable + '.png', dpi=300)
	 plt.close(fig)
	 plt.close('all')



def lookup_cases_controls(df_variables, df_pheno, sex):
	for index, row in df_variables.iterrows():
		 variable = row.Varname
		 if variable not in df_pheno.columns:
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
		 bar_plot(df_pheno_cut[df_pheno_cut.SEX_BIRTH == 0].copy(),df_pheno_cut[df_pheno_cut.SEX_BIRTH == 1].copy(),variable)
		 df_all = df_pheno_cut[df_pheno_cut.RECODED.isin({0, 1})]
		 df_males = df_all[df_all.SEX_BIRTH == 0]
		 df_females = df_all[df_all.SEX_BIRTH == 1]
		 n_total = len(df_all)
		 n_males = len(df_males)
		 n_females = len(df_females)
		 n_cases = len(df_all[df_all.RECODED == 1])
		 n_cases_males = len(df_males[df_males.RECODED == 1])
		 n_cases_females = len(df_females[df_females.RECODED == 1])
		 n_controls = len(df_all[df_all.RECODED == 0])
		 n_controls_males = len(df_males[df_males.RECODED == 0])
		 n_controls_females = len(df_females[df_females.RECODED == 0])
		 flag=[]
		 if (n_total<100):
			  flag.append('Total number of samples below ' +str(100))
		 if (n_cases<10):
			  flag.append('Number of cases below ' + str(10))
		 if (n_controls<10):
			  flag.append('Number of controls below ' + str(10))
		 if ((n_cases_males<5) and (n_total>5)):
			  flag.append('Sex-Specific (females) ?')
		 if ((n_cases_females<5) and (n_total>5)):
			  flag.append('Sex-Specific (males)?')
		 yield({'[Description] Domain': row.DOMAIN, '[Description] Variable': variable,'[Description] Label': row['LABEL_ENGLISH'],'[Description] Type': 'Binary' ,'[Statistics] Total': n_total, '[Statistics] Males': n_males, '[Statistics] Females': n_females, '[Statistics] Cases': n_cases, '[Statistics] Controls': n_controls, '[Statistics] Males Cases': n_cases_males, '[Statistics] Females Cases': n_cases_females, '[Statistics] Males Controls': n_controls_males, '[Statistics] Females Controls' : n_controls_females,'[Statistics] No Answer' : N_noanswer, '[Statistics] Missing' : N_missing, '[Statistics] Other codes (NA assumed)' : N_NA,'[Codes] Missing' : row.CODE_MISSING, '[Codes] No answer' : row.CODE_NOANSWER, '[Codes] Yes ' : row.CODE_YES, '[Codes] No' : row.CODE_NO, '[Codes] Used Values' : ' | '.join([str(i) for i in Unique_values]), '[Hidden] problem' : flag})



df_binary = pd.DataFrame({'Binary_Phenotype_1': np.random.choice([0,1,99,-7], 1000, p=[0.5, 0.1, 0.1, 0.3]), 'Binary_Phenotype_2': np.random.choice([0,1,99,-7], 1000, p=[0.5, 0.1, 0.1, 0.3]),'Binary_Phenotype_3': np.random.choice([0,1,99,-7], 1000, p=[0.5, 0.1, 0.1, 0.3]),'Binary_Phenotype_4': np.random.choice([0,1,99,-7], 1000, p=[0.5, 0.1, 0.1, 0.3]),'Binary_Phenotype_5': np.random.choice([0,1,99,-7], 1000, p=[0.5, 0.1, 0.1, 0.3])})
df_binary['SEX_BIRTH']=1
df_binary['P_AGE']=[random.randrange(100) for i in range(0,1000) ]
df_binary.loc[1:500,'SEX_BIRTH']=0
df_binary.loc[1:500,'Binary_Phenotype_5']= -7
df_binary.loc[1:998,'Binary_Phenotype_2']= -7
df_variables = pd.DataFrame({'Varname': ['Binary_Phenotype_1', 'Binary_Phenotype_2','Binary_Phenotype_3','Binary_Phenotype_4','Binary_Phenotype_5'], 'DOMAIN': ['Toy Dataset', 'Toy Dataset','Toy Dataset','Toy Dataset','Toy Dataset'], 'LABEL_ENGLISH': ['First Phenotype', 'First Flagged Phenotype','Third Phenotype','Fourth Phenotype','Sex-Specific Phenotype'],'CODE_YES' : [1,1,1,1,1],'CODE_NOANSWER' : [-7,-7,-7,-7,-7],'CODE_MISSING' : [99,99,99,99,99],'CODE_NO' : [0,0,0,0,0]})

df_variables_uni = pd.DataFrame(lookup_cases_controls(df_variables, df_binary,'Unisex'))
df_variables_uni.to_json('Binary_data.json', orient='records')
