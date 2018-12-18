from home.clintad import GetTADs
import json
from home.statistics_old import generate_CNV


class Variant:
    def __init__(self, chromosome, start, end, hpo_matches, gene_matches, weighted_score):
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.hpo_matches = hpo_matches
        self.gene_matches = gene_matches
        self.weighted_score = weighted_score


def get_one_variant(chromosome, start, end, phenotypes):
    start = start.replace(',', '')
    end = end.replace(',', '')

    result = json.loads(GetTADs(chromosome, start, end, phenotypes, 0))
    variant = Variant(chromosome, result['cnv_start'], result['cnv_end'], result['hpo_matches'], result['gene_matches'],
                      result['weighted_score'])
    return json.dumps(variant.__dict__)


def get_25_variants(chromosome, start, end, phenotypes):
    start = start.replace(',', '')
    end = end.replace(',', '')

    variant_list = []
    for i in range(500):
        sim_chr, sim_start, sim_end = generate_CNV(int(end)-int(start))
        result = json.loads(GetTADs(sim_chr, sim_start, sim_end, phenotypes, 0))
        variant_list.append(Variant(chromosome, result['cnv_start'], result['cnv_end'], result['hpo_matches'],
                                    result['gene_matches'], result['weighted_score']))
    return json.dumps([variant.__dict__ for variant in variant_list])
