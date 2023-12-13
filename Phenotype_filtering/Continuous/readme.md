Goal : 

Create a Data Analysis tool to identify and curate phenotype appropriate for GWAS analysis

Usage :

With a file named Continuous_data.json (created with the associate python script) and an images/ directory (with images created with the same script) simply click on the Unix executable.



#Creation Server Package

npm install open@8.4.2  
npm install express  
npm install multer  
npm install open  

sudo pkg . -t node16-macos  


# old conversion format -> newformat

df1=pd.read_json('new_virgin_file.json')  
df2=pd.read_json('completed_file.json')  

q=df1.merge(df2[['To exclude', 'Not normalize','justification_Not normalize', 'Sex-Specific', 'Threshold Left','justification_To exclude','Choice_Sex-Specific','justification_Threshold Left', 'justification_Threshold Right','[Description] Variable']],on='[Description] Variable')  
a=json.dumps([row.dropna().to_dict() for index,row in q.iterrows()])  
with open("Output.txt", "w") as text_file:  
     text_file.write(a)  
