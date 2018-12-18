# Import required packages
import os
import json
import io
import random

#Opens the TAD boundary file, chromosome lengths file, and genes to phenotype file
module_dir = os.path.dirname(__file__)  # get current directory
boundary_path = os.path.join(module_dir, 'files/boundary.txt')
length_path = os.path.join(module_dir, 'files/chromosomeLengthsHG19.txt')
genes_to_phenotype_path = os.path.join(module_dir, 'files/genes_to_phenotypes_weighted.txt')
hpo_path = os.path.join(module_dir, 'files/hpo_list.txt')

class gene():
    def __init__(self, symbol, start, end):
        self.name = symbol
        self.start = start
        self.end = end
        self.phenotypes = []
        self.weights = []
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


def GetStatistics(request, chromosome, CNV_start, CNV_end, phenotypes, zoom):
    start = CNV_start.replace(',','')
    start = int(start)
    end = CNV_end.replace(',','')
    end = int(end)
    CNV_length = end - start + 1
    result = "Chromosome\tStart\tEnd\tGenes with matches\tTotal Matches\tWeighted Score\tUnique Matches\r\n"
    
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
    
    #Get results with the actual CNV first
    matched= []
    genes, genes_with_matches, total_phenotype_score, weighted_score, unique_matches\
        = GetTADs(request, chromosome, start, end, phenotypes, zoom)
    for j in range(4, len(genes)):
            gene_phenotypes = genes[j].phenotypes
            for k in range(len(gene_phenotypes)):
                if gene_phenotypes[k] in phenotype_list:
                    matched.append(str(genes[j].name.strip()) + "(" + str(gene_phenotypes[k]) + ")")
        
    number_of_matches = len(genes_with_matches)
    
    result = result + str(chromosome)+"\t"+str(start)+"\t"+str(end)+"\t"+\
        str(number_of_matches)+"\t"+str(total_phenotype_score)+"\t"+str(weighted_score)+\
        "\t"+str(unique_matches)+"\t"+str(matched)+"\r\n\r\n"

    actual_weighted = weighted_score
    lower_weighted_score = 0

    # Simulate multiple CNVs to determine the number of genes with phenotype matches
    for i in range(500):
        matched = []
        sim_chromosome, sim_start, sim_end = generate_CNV(CNV_length)
        genes, genes_with_matches, total_phenotype_score, weighted_score, unique_matches\
            = GetTADs(request, sim_chromosome, sim_start, sim_end, phenotypes, zoom)
        print(i, ': chromosome', sim_chromosome, sim_start, '-', sim_end)
        for j in range(4, len(genes)):
            gene_phenotypes = genes[j].phenotypes
            for k in range(len(gene_phenotypes)):
                if gene_phenotypes[k] in phenotype_list:
                    matched.append(str(genes[j].name.strip()) + "(" + str(gene_phenotypes[k]) + ")")
        if weighted_score <= actual_weighted:
            lower_weighted_score +=1
        number_of_matches = len(genes_with_matches)
        
        result = result + str(sim_chromosome)+"\t"+str(sim_start)+"\t"+str(sim_end)+"\t"+\
            str(number_of_matches)+"\t"+str(total_phenotype_score)+"\t"+str(weighted_score)+\
            "\t"+str(unique_matches)+"\t"+str(matched)+"\r\n"
    result = "Random with lower or equal weighted score " + str(lower_weighted_score) +"/500\n"+result
    return(result)

def generate_CNV(CNV_length):
    chromosome_length_file = open(length_path, 'r')
    end_numbers = []
    
    i=0
    for line in chromosome_length_file:
        column = line.split('\t')
        chromosome_length = int(column[1])
        chromosome_length = chromosome_length - CNV_length
        if i==0:
            end_numbers.append(chromosome_length)
        else:
            end_numbers.append(chromosome_length+end_numbers[i-1])
        i+=1
    random_coordinate = random.randint(1, end_numbers[-1])
    
    for i in range(24):
        if random_coordinate < end_numbers[i]:
            chromosome = i+1
            break
    
    if chromosome > 1:
        start = random_coordinate - end_numbers[chromosome-2]
    else:
        start = random_coordinate
    
    if chromosome == 23:
        chromosome = 'X'
    if chromosome == 24:
        chromosome = 'Y'
    return str(chromosome), str(start), str(start+CNV_length)


# Draws and labels the nearby genes
def GetTADs(request, chromosome, CNV_start, CNV_end, phenotypes, zoom):
    TAD_boundary_file = open(boundary_path, 'r')
    chromosome_length_file = open(length_path, 'r')
    genes_to_phenotypes = open(genes_to_phenotype_path, 'r')
    
    if chromosome == 'x' or chromosome == 'y':
        chromosome = chromosome.upper()
    patient_chromosome = 'chr'+ str(chromosome)
    patient_CNV_start = CNV_start
    patient_CNV_end = CNV_end
    
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
    
    # If the CNV start/end is less than/greater than the TAD boundaries, use the 
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
               for word in cell:
                   try:
                       hpo_weight = word.split('w')
                       gene_list[i].phenotypes.append(int(hpo_weight[0]))
                       gene_list[i].weights.append(int(hpo_weight[1]))
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
    
    genes_with_matches = []
    unique_matches = []
    total_phenotype_score = 0
    weighted_score = 0
    for i in range(len(gene_list)):
        for j in range(len(phenotype_list)):
            for k in range(len(gene_list[i].phenotypes)):
                if phenotype_list[j] == gene_list[i].phenotypes[k]:
                    gene_list[i].matches.append(phenotype_list[j])
                    gene_list[i].phenotype_score+= 1
                    total_phenotype_score+= 1
                    weighted_score+= 20/gene_list[i].weights[k]
                    if phenotype_list[j] not in unique_matches:
                        unique_matches.append(phenotype_list[j])
        if gene_list[i].phenotype_score > 0:
            genes_with_matches.append(gene_list[i].name)
        
    my_array_of_genes=[]
    my_array_of_genes.append(patient_boundaries_l)
    my_array_of_genes.append(patient_boundaries_r)
    my_array_of_genes.append([patient_CNV_start, patient_CNV_end])
    my_array_of_genes.append([{"coord":minimum_coordinate, "type":min_type}, 
                              {"coord":maximum_coordinate, "type":max_type}])
    
    for i in range(len(gene_list)):
        my_array_of_genes.append(gene_list[i])
    
    TAD_boundary_file.close()
    chromosome_length_file.close()
    genes_to_phenotypes.close()
    
    return(my_array_of_genes, genes_with_matches, total_phenotype_score, weighted_score, len(unique_matches))
