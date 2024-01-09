# CARTaGENE_PheWas

Goal This repository will contain all script and code used in the creation of the data for the PheWeb.

## Variable Summary Statistics

### Goal

This tool provides a json format summary statistic and images to describe variable.



## Filtering Tool

### Goal

This tool aim to provide a User Interface to display variables statistics and images to help decide filtering options.

### Usage

```
- Important!
@@ This tool works only when the dependant files are within the same direction see below @@
 wget https://github.com/CERC-Genomic-Medicine/CARTaGENE_PheWas/blob/29052a0f53396846f20531109565f68a8e754332/Phenotype_filtering/Filtering_tool/Filtering_tool.zip 
 unzip Filtering_tool.zip 
 open Filtering_tool executable  
```
```diff
- Required Files!

1) Continuous_data.json or Binary_data.json
---> a json file detailing the variables to be analysed, requiered fields : '[Hidden] problem', "[Description] Variable", "[Description] Label"
2) Images folder (containing images to be displayed)
--->file called : images/"[Description] Variable".png for each object.
```

### Broader application

While this tool currently has features unique to certain types of data (i.e. Sex-Specific) integrated, the tool can still be used to explore and filter broader data. The feature of each objects are grouped and displayed into tables along the feature key scheme : '[table head/group] row name'. All '[Hidden]' and '[Description]' groups are not displayed into tables.
