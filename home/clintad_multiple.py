import os
import json
from home.clintad import GetTADs

class Gene:
    def __init__(self, symbol, start, end):
        self.name = symbol
        self.start = start
        self.end = end
        self.phenotypes = []
        self.phenotype_score = 0


class Patient:
    def __init__(self, identifier, chromosome, start, end, phenotypes, matched_genes, all_genes):
        self.identifier = identifier
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.phenotypes = phenotypes
        self.matched_genes = matched_genes
        self.all_genes = all_genes


def sort_genes(gene_list):
    changed = True
    
    while changed:
        changed = False
        for i in range(len(gene_list)-1):
            if gene_list[i].start > gene_list[i+1].start:
                gene_list[i], gene_list[i+1] = gene_list[i+1], gene_list[i]
                changed = True
    
    return None


def process_multiple_patients(patient_data):
    patient_data_split = patient_data.splitlines()

    result = "Chromosome\tStart\tEnd\t Matches\r\n"
    for line in patient_data_split:
        if line.strip() == '':  # Skip blank lines
            continue
        col = line.split('\t')
        patient_ID, chromosome, start, end, phenotypes = col[0], col[1], col[2], col[3], col[4]
        data = json.loads(GetTADs(chromosome, start, end, phenotypes, 0))

        matches = ''
        for gene in data['genes']:
            if gene['matches']:
                matches += gene['name'] + '('
                hpo_ids = [str(match['hpo']) for match in gene['matches']]
                matches += ', '.join(hpo_ids) + '), '
        matches += '\r\n'
        result += '\t'.join([chromosome, start, end, matches])
    return result