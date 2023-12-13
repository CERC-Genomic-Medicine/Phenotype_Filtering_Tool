# Goal : 

Create a Data Analysis tool to identify and curate phenotype appropriate for GWAS analysis

# Usage :
```
python3 Script_statistics_continuous_variable.py -c Catalog.excel -p Phenotype.csv -s Sample_list.txt -out Continuous_data
mkdir images
mv *.png images/
wget https://github.com/CERC-Genomic-Medicine/CARTaGENE_PheWas/blob/4b9bed6e68ff3058373ac8e71029c6e5e7257397/Phenotype_filtering/Continuous/Continuous_filter.zip
unzip Continuous_filter.zip
*** click on Continuous_filter ***
```
* Continuous_filter requieres __in the same directory as the executable__ a file named Continuous_data.json and an images/ directory (with images associated with each phenotype with N_unique > 1). All these file should be produced with the Script_statistics_continuous_variable.py.  
* Flags can be adjusted using the options in the Script_statistics_continuous_variable.py optional inputs



# Creation of Unix executable
```
npm install open@8.4.2  
npm install express  
npm install multer  
npm install open  

sudo pkg . -t node16-macos  
```
pkg interprets the 'package.json' file provided which interns references the public/ directory scripts  


# old conversion format -> newformat

df1=pd.read_json('new_virgin_file.json')  
df2=pd.read_json('completed_file.json')  

q=df1.merge(df2[['To exclude', 'Not normalize','justification_Not normalize', 'Sex-Specific', 'Threshold Left','justification_To exclude','Choice_Sex-Specific','justification_Threshold Left', 'justification_Threshold Right','[Description] Variable']],on='[Description] Variable')  
a=json.dumps([row.dropna().to_dict() for index,row in q.iterrows()])  
with open("Output.txt", "w") as text_file:  
     text_file.write(a)  
