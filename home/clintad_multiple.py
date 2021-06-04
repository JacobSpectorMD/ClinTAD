import os
import json

from home.clintad import GetTADs
from home.helper import parse_coordinates, parse_phenotypes


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


def process_multiple_patients(request):
    choice = request.POST.get('cases_or_regions', None)
    text = request.POST.get('text', None)
    if not text or not choice:
        return []
    lines = text.split('\n')

    if choice == 'cases':
        lines_to_read = lines[:]
    elif choice == 'regions':
        lines_to_read = lines[1:]

    clintad_data = []
    for line in lines_to_read:
        if line.strip() == '':  # Skip blank lines
            continue

        # The input for multiple regions should have all phenotypes on the first line
        if choice == 'cases':
            col = line.split('\t')

            case_id = col[0].strip()
            coordinate_string = col[1]
            chromosome, start, end = parse_coordinates(coordinate_string)
            phenotypes = parse_phenotypes(col[2].strip())
        elif choice == 'regions':
            case_id = 'Case 1'
            phenotypes = parse_phenotypes(lines[0].strip())
            coordinate_string = line.strip()
            chromosome, start, end = parse_coordinates(coordinate_string)

        line_data = json.loads(GetTADs(request, case_id, chromosome, start, end, phenotypes, 0,
                                       source_function='multiple'))
        clintad_data.append(line_data)
    return clintad_data


def process_multiple_patients_old(request):
    choice = request.POST.get('cases_or_regions')
    text = request.POST.get('text')
    lines = text.split('\n')

    result = "Chromosome\tStart\tEnd\t Matches\tAutosomal Dominant\tAutosomal Recessive\tX-Linked Dominant\t" \
             "X-linked Recessive\r\n"
    for line in lines:
        if line.strip() == '':  # Skip blank lines
            continue
        col = line.split('\t')
        patient_ID, chromosome, start, end, phenotypes = col[0], col[1], col[2], col[3], col[4]
        data = json.loads(GetTADs(request, '', chromosome, start, end, phenotypes, 0, source_function='multiple'))

        matches = ''
        autosomal_recessive = ''
        autosomal_dominant = ''
        x_linked_recessive = ''
        x_linked_dominant = ''
        for gene in data['genes']:
            if gene['matches']:
                matches += gene['name'] + '('
                hpo_ids = [str(match['hpo']) for match in gene['matches']]
                matches += ', '.join(hpo_ids) + '), '
            if gene['autosomal_dominant']:
                autosomal_dominant += gene['name']+'('+', '.join('OMIM:'+ad for ad in gene['autosomal_dominant'].keys())+'), '
            if gene['autosomal_recessive']:
                autosomal_recessive += gene['name']+'('+', '.join('OMIM:'+ar for ar in gene['autosomal_recessive'].keys())+'), '
            if gene['x_linked_dominant']:
                x_linked_dominant += gene['name']+'('+', '.join('OMIM:'+xd for xd in gene['x_linked_dominant'].keys())+'), '
            if gene['x_linked_recessive']:
                x_linked_recessive += gene['name']+'('+', '.join('OMIM:'+xr for xr in gene['x_linked_recessive'].keys())+'), '
        x_linked_recessive += '\r\n'
        result += '\t'.join([chromosome, start, end, matches, autosomal_dominant, autosomal_recessive,
                             x_linked_dominant, x_linked_recessive])
    return result