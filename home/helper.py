# Turn phenotype input string into array of ints
def parse_phenotypes(phenotype_string):
    phenotype_list=[]
    phenotypes_split = phenotype_string.split(',')
    for i in range (len(phenotypes_split)):
        try:
            if "HP" in phenotypes_split[i].upper():
                x = phenotypes_split[i].split(':')
                phenotype_list.append(int(x[1]))
            else:
                phenotype_list.append(int(phenotypes_split[i]))
        except:
            continue
    return phenotype_list