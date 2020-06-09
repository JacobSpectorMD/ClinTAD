import json

from home.clintad import GetTADs
from home.statistics_old import generate_CNV


class Variant:
    def __init__(self, chromosome, start, end, hpo_matches, gene_matches, weighted_score):
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.hpo_matches = hpo_matches
        self.gene_matches = gene_matches
        self.weighted_score = weighted_score


def get_one_variant(request, chromosome, start, end, phenotypes):
    start = start.replace(',', '')
    end = end.replace(',', '')

    result = json.loads(GetTADs(request, '', chromosome, start, end, phenotypes, 0))
    variant = Variant(chromosome, result['cnv_start'], result['cnv_end'], result['hpo_matches'], result['gene_matches'],
                      result['weighted_score'])
    return json.dumps(variant.__dict__)


def get_100_variants(request, chromosome, start, end, phenotypes):
    # ToDo: Fix this, it appears that it is being called 5 times asynchronously
    start = start.replace(',', '')
    end = end.replace(',', '')

    variant_list = []
    while len(variant_list) <= 100:
        sim_chr, sim_start, sim_end = generate_CNV(int(end)-int(start))
        result = json.loads(GetTADs(request, '', sim_chr, sim_start, sim_end, phenotypes, 0, source_function='single'))
        variant_list.append(Variant(chromosome, result['cnv_start'], result['cnv_end'], result['hpo_matches'],
                                    result['gene_matches'], result['weighted_score']))
    return json.dumps([variant.__dict__ for variant in variant_list])


def get_n_variants(request, chromosome, start, end, phenotypes, n):
    start = start.replace(',', '')
    end = end.replace(',', '')

    variant_list = []
    while len(variant_list) < n:
        sim_chr, sim_start, sim_end = generate_CNV(int(end)-int(start))
        result = json.loads(GetTADs(request, '', sim_chr, sim_start, sim_end, phenotypes, 0, source_function='single'))
        variant_list.append(result)
    return variant_list
