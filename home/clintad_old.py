# Import required packages
import os
import json
import io

#Opens the TAD boundary file, chromosome lengths file, and genes to phenotype file
module_dir = os.path.dirname(__file__)  # get current directory
boundary_path = os.path.join(module_dir, 'files/boundary.txt')
length_path = os.path.join(module_dir, 'files/chromosomeLengthsHG19.txt')
genes_to_phenotype_path = os.path.join(module_dir, 'files/genes_to_phenotypes_simple.txt')
hpo_path = os.path.join(module_dir, 'files/hpo_list.txt')

class gene():
    def __init__(self, symbol, start, end):
        self.name = symbol
        self.start = start
        self.end = end
        self.phenotypes = []
        self.phenotype_score = 0
        self.matches = []

def sort_genes(gene_list):
    changed = True
    
    while changed:
        changed = False
        for i in range(len(gene_list)-1):
            if gene_list[i].start > gene_list[i+1].start:
                gene_list[i], gene_list[i+1] = gene_list[i+1], gene_list[i]
                changed = True
    
    return None

#-----Draws and labels the nearby genes
def GetTADs(chromosome, CNV_start, CNV_end, phenotypes, zoom):
    TAD_boundary_file = open(boundary_path, 'r')
    chromosome_length_file = open(length_path, 'r')
    genes_to_phenotypes = open(genes_to_phenotype_path, 'r')
    
    if chromosome == 'x' or chromosome == 'y':
        chromosome = chromosome.upper()
    patient_chromosome = 'chr'+ str(chromosome)
    patient_CNV_start = int(CNV_start.replace(',',''))
    patient_CNV_end = int(CNV_end.replace(',',''))
    
    # Finds the chromosome length for the patient's chromosome
    for line in chromosome_length_file:
        column = line.split('\t')
        if patient_chromosome == column[0]:
            chromosome_length = int(column[1])
    
    # If the user enters a search distance, add this to the start and end of the CNV
    # and look for all genes in that area
    if zoom > 0:
        search_distance = 1000000 * (2 ** zoom)
        search_start = patient_CNV_start - search_distance
        search_end = patient_CNV_end + search_distance
        if search_start < 0:
            search_start = 0
        if search_end > chromosome_length:
            search_end = chromosome_length
    else:
        search_start = patient_CNV_start
        search_end = patient_CNV_end

    
    # Finds the nearest left and right TAD boundary    
    temp_boundaries_l = [0]
    temp_boundaries_r = [0]
    patient_boundaries_r = []
    patient_boundaries_l = []
    boundaries_started = False
    TAD_boundary_file.seek(0,0)
    for line in TAD_boundary_file:
        column = line.split('\t')
        if column[0] == patient_chromosome:
            boundaries_started = True
            if int(column[1]) <= search_start:
                temp_boundaries_l[0] = int(column[1])
            if int(column[1]) > search_start:
                temp_boundaries_l.append(int(column[1]))
            if int(column[2]) <= search_start:
                temp_boundaries_r[0] = int(column[2])
            if int(column[2]) >= search_start and int(column[2]) < search_end:
                temp_boundaries_r.append(int(column[2]))
            if int(column[2]) >= search_end:
                temp_boundaries_r.append(int(column[2]))
                break
        if boundaries_started and column[0] != patient_chromosome:
            break
    for i in range(len(temp_boundaries_r)):
        if (temp_boundaries_r[i] > temp_boundaries_l[0]):
            patient_boundaries_r.append(temp_boundaries_r[i])
    
    if temp_boundaries_l[0] == 0:
        for i in range (len(temp_boundaries_l)-1):
            patient_boundaries_l.append(temp_boundaries_l[i+1])
    elif temp_boundaries_l[0] != 0:
        for i in range (len(temp_boundaries_l)):
            patient_boundaries_l.append(temp_boundaries_l[i])
    
    # If the CNV start/end is less than/greater than the TAD boundarie, use the 
    # start/end of the chromosome
    if patient_boundaries_l:
        if search_start < patient_boundaries_l[0]:
            minimum_coordinate = 0
            min_type = "chromosome"
        else:
            minimum_coordinate = patient_boundaries_l[0]
            min_type = "boundary"
    elif not patient_boundaries_l:
        minimum_coordinate = 0
        min_type = "chromosome"
    
    if patient_boundaries_r:
        if search_end > patient_boundaries_r[-1]:
            maximum_coordinate = chromosome_length
            max_type = "chromosome"
        else:
            maximum_coordinate = patient_boundaries_r[-1]
            max_type = "boundary"
    elif not patient_boundaries_r:
        maximum_coordinate = chromosome_length
        max_type = "chromosome"
    
    gene_list=[]
    genes_path = os.path.join(module_dir, 'files/genes/')
    genes_path = genes_path + patient_chromosome + '.txt'
    with open(genes_path, 'r') as f:
        for line in f:
            cell = line.split("\t")
            start, end = int(cell[1]), int(cell[2])
            if start >= minimum_coordinate and start <= maximum_coordinate:
                try:
                    gene_list.append(gene(cell[3], start, end))
                    if end > maximum_coordinate:
                        maximum_coordinate = end
                        max_type = "gene"
                except:
                    continue
            elif (end >= minimum_coordinate and end <= maximum_coordinate):
                try:
                    gene_list.append(gene(cell[3].strip(), start, end))
                    if start < minimum_coordinate:
                        minimum_coordinate = start
                        min_type = "gene"
                except:
                    continue
            elif (start > maximum_coordinate):
                break
    f.close()
                
    sort_genes(gene_list)
    
    # For every gene, go through genes_to_phenotypes_simple and add all phenotypes
    # to that gene's object
    for i in range(len(gene_list)):
        genes_to_phenotypes.seek(0,0)
        for line in genes_to_phenotypes:
           column = line.split('\t')
           if column[0].strip().upper() == gene_list[i].name.strip().upper():
               cell = column[1].split(',')
               for x in cell:
                   try:
                       gene_list[i].phenotypes.append(int(x))
                   except:
                       break
               break
           
    phenotype_list=[]
    phenotypes_split = phenotypes.split(',')
    for i in range (len(phenotypes_split)):
        try:
            if "HP" in phenotypes_split[i].upper():
                x = phenotypes_split[i].split(':')
                phenotype_list.append(int(x[1]))
            else:
                phenotype_list.append(int(phenotypes_split[i]))  
        except:
            continue
    for i in range(len(gene_list)):
        for j in range(len(phenotype_list)):
            if phenotype_list[j] in gene_list[i].phenotypes:
                gene_list[i].matches.append(phenotype_list[j])
                gene_list[i].phenotype_score+=1
        
    my_array_of_genes=[]
    my_array_of_genes.append(patient_boundaries_l)
    my_array_of_genes.append(patient_boundaries_r)
    my_array_of_genes.append([patient_CNV_start, patient_CNV_end])
    my_array_of_genes.append([{"coord":minimum_coordinate, "type":min_type}, 
                              {"coord":maximum_coordinate, "type":max_type}])
    
    for i in range(len(gene_list)):
        my_array_of_genes.append(gene_list[i].__dict__)
    
    TAD_boundary_file.close()
    chromosome_length_file.close()
    genes_to_phenotypes.close()
    
    return(my_array_of_genes)

def hpo_lookup(entered_string):   
    class phenotype_class():
        def __init__(self, d):
            self.__dict__= d

    HPOs_to_return = []
    array_to_return =[]
    with io.open(hpo_path, 'r', encoding='utf-8-sig') as f:
        list_of_hpo = json.load(f, encoding="ANSI")
    f.close()

    words = entered_string.split()
    for i in range(len(list_of_hpo)):
        current_phenotype = phenotype_class(list_of_hpo[i])
        score = 0
        for word in words:
            if word.upper() in str(current_phenotype.__dict__).upper():
                score += 1
        current_phenotype.score = score
        if score >= len(words):
            HPOs_to_return.append(current_phenotype)

    HPOs_to_return.sort(key = lambda x: x.score, reverse=True)
    for HPO in HPOs_to_return:
        array_to_return.append(HPO.id)

    # If the match is in the description or comment and not the HPO name/title, move it to the bottom
    for i in range(len(array_to_return)):
        in_title = False
        for word in words:
            if word.upper() in array_to_return[i].upper():
                in_title = True
        if not in_title:
            j = i
            while j < len(array_to_return)-1:
                j+=1
                for word in words:
                    if word.upper() in array_to_return[j].upper():
                        array_to_return[i], array_to_return[j] = array_to_return[j], array_to_return[i]
                        break
            
    return (array_to_return)
    
