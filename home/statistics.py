import json

from home.clintad import GetTADs
from home.helper import parse_coordinates, parse_phenotypes
from home.statistics_old import generate_CNV


class Variant:
    def __init__(self, chromosome, start, end, hpo_matches, gene_matches, tads, weighted_score, unique_matches):
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.hpo_matches = hpo_matches
        self.gene_matches = gene_matches
        self.tads = tads
        self.weighted_score = weighted_score
        self.unique_matches = unique_matches


def get_one_variant(request, coordinates, phenotypes, ret='String'):
    chromosome, start, end = parse_coordinates(coordinates)
    phenotypes = parse_phenotypes(phenotypes)
    if not chromosome or not start or not end or not phenotypes:
        return {}

    result = json.loads(GetTADs(request, '', chromosome, start, end, phenotypes, 0))
    variant = Variant(chromosome, result['cnv_start'], result['cnv_end'], result['hpo_matches'], result['gene_matches'],
                      result['tads'], result['weighted_score'], result['unique_matches'])
    if ret == 'String':
        return json.dumps(variant.__dict__)
    else:
        return variant.__dict__


def get_100_variants(request, coordinates, phenotypes):
    # ToDo: Fix this, it appears that it is being called 5 times asynchronously
    chromosome, start, end = parse_coordinates(coordinates)
    phenotypes = parse_phenotypes(phenotypes)
    print('getting variants...')
    variant_list = []
    while len(variant_list) < 20:
        sim_chr, sim_start, sim_end = generate_CNV(int(end) - int(start))
        result = json.loads(GetTADs(request, '', sim_chr, sim_start, sim_end, phenotypes, 0, source_function='single'))
        variant_list.append(Variant(chromosome, result['cnv_start'], result['cnv_end'], result['hpo_matches'],
                                    result['gene_matches'], result['weighted_score']))
    print(variant_list)
    return json.dumps([variant.__dict__ for variant in variant_list])


def get_n_variants(request, chromosome, start, end, phenotypes, n):
    start = start.replace(',', '')
    end = end.replace(',', '')

    variant_list = []
    while len(variant_list) < n:
        sim_chr, sim_start, sim_end = generate_CNV(int(end) - int(start))
        result = json.loads(GetTADs(request, '', sim_chr, sim_start, sim_end, phenotypes, 0, source_function='single'))
        variant_list.append(result)
    return variant_list
