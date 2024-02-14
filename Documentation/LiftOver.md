# Liftover

## GOAL

- Change array genotyping position from b37 to b38
- intermediary goal : change encoding to MT
- intermediary goal : Merge XY into X chromosome 

## Software

plink/1.9

## Input

- path=''
- arrays ${path}/gsa.${i}.final.v1.1.bed ${path}/gsa.${i}.final.v1.1.fam ${path}/gsa.${i}.final.v1.1.bim
- ** 17K ${path}/gsa.17k.final.v1.1.hg19.bed ${path}/gsa.17k.final.v1.1.hg19.fam ${path}/gsa.17k.final.v1.1.hg19.bim

## Output 

- {array}_Hg38_Xmerged (.bed / .bim /.fam)

### Arrays

- 4224 5300 760 archi 17k

#### Script ###
#Step 1 : Intermediay Goals
for  i in 4224 5300 archi; do 
        plink -bfile ${path}/gsa.${i}.final.v1.1 --remove Samples_to_Remove/${i}.samples --make-bed --output-chr MT --out tmp
        plink -bfile tmp --merge-x --make-bed --output-chr MT --out XYmerged_${i}
        rm tmp*
done

for  i in 760; do
        plink -bfile ${path}/gsa.${i}.final.v1.1  --make-bed --output-chr MT --out tmp
        plink -bfile tmp --merge-x --make-bed --output-chr MT --out XYmerged_${i}
        rm tmp*
done

plink -bfile ${path}/gsa.17k.final.v1.1.hg19 --make-bed --output-chr MT --out XYmerged_17k --remove Samples_to_Remove/17k.samples

# Step 2 Liftover 

for array in 17k 4224 5300 760 archi; do 
        awk '{print "chr" $1, $4-1, $4, $2}' XYmerged_${array}.bim > ${array}_bedfile           ## Produces a bed file of all variants
        liftOver ${array}_bedfile hg19ToHg38.over.chain.gz ${array}_mapfile ${array}_unmappedfile   ## Produces Map file and unmapped variant file
        grep ^chr[0-9A-Za-z]*_ ${array}_mapfile | cut -f 4 > ${array}_excludefile    ## Identifies Alternate contig mod A-Z a-z
        grep -v '^#' ${array}_unmappedfile | cut -f 4 >> ${array}_excludefile              ## Total list of variant to be excluded
        grep -v ${array}_excludefile ${array}_mapfile > ${array}_mapfile_final          ## Remove excluded variant

        plink --bfile XYmerged_${array} \
        --exclude ${array}_excludefile \
        --make-bed \
        --not-chr MT \
        --out tmp_${array}

        plink --bfile tmp_${array} \
        --update-chr ${array}_mapfile_final 1 4 \
        --update-map ${array}_mapfile_final 3 4 \
        --make-bed \
        --output-chr chrMT \
        --out ${array}_Hg38_Xmerged

        mv *.log logs/
        rm tmp* 
done

Verification Step :

for i in *bim; do echo $i ; grep ^chrM $i| wc -l ; grep ^chrX $i| wc -l ; grep ^chrY $i | wc -l ; grep ^chrXY $i | wc -l ; done ## check No mitochondria (chrM or chrMT) and no Pseudoautosomal regions (chrXY)

for i in *bim; do grep rs2341354 $i ; done  # produces postion corresponding to dbsnp Hg38
