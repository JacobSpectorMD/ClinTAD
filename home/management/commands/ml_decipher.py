import csv
import datetime
import json

from django.core import management
from django.core.management.base import BaseCommand
from home.statistics import get_one_variant


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Read in the patient data
        patient_data = read_patient_data()

        # # Get all of the metric for machine learning
        # add_ml_metrics(patient_data)
        #
        # # Write the data to a file
        # write_data(patient_data)


class Variant:

    def __init__(self, chr=-1, end=-1, genotype='', hpo_accessions=[], inheritance='', num_hpos=-1, pathogenicity='',
                 patient_id=-1, start=-1, variant_class=''):
        self.patient_id = patient_id
        self.chr = chr
        self.start = start
        self.end = end

        self.genotype = genotype
        self.inheritance = inheritance
        self.num_hpos = num_hpos
        self.hpo_accessions = hpo_accessions
        self.pathogenicity = pathogenicity
        self.variant_class = variant_class

        self.genes = None
        self.hpo_matches = -1
        self.unique_matches = -1
        self.unique_over_input = -1
        self.gene_matches = -1
        self.length = -1
        self.tads = None
        self.weighted_score = -1

        # Number of haploinsufficient/triplosensitive genes and whether or not the variant completely overlaps
        # a dosage sensitive region
        self.num_hi_genes = -1
        self.num_ts_genes = -1
        self.overlaps_hi = None
        self.overlaps_ts = None

        # TAD boundaries and total distance between boundaries
        self.left_tad = None
        self.right_tad = None
        self.mb = -1

        # Parameters that are corrected for length
        self.hpo_matches_per_mb = -1
        self.unique_matches_per_mb = -1
        self.gene_matches_per_mb = -1
        self.weighted_score_per_mb = -1
        self.num_hi_genes_per_mb = -1
        self.num_ts_genes_per_mb = -1
        self.num_genes_per_mb = -1

    def get_tad_boundaries(self):
        for tad in self.tads:
            if not self.left_tad or tad['start'] <= self.left_tad:
                self.left_tad = tad['start']
            if not self.right_tad or tad['end'] >= self.right_tad:
                self.right_tad = tad['end']
        self.mb = (self.right_tad - self.left_tad) / 1000000

    def num_genes(self):
        """Genes from the GetTADs function is an array of gene objects"""
        return len(self.genes)

    def create_length_based_parameters(self):
        self.hpo_matches_per_mb = self.hpo_matches / self.mb
        self.unique_matches_per_mb = self.unique_matches / self.mb
        self.gene_matches_per_mb = self.gene_matches / self.mb
        self.weighted_score_per_mb = self.weighted_score / self.mb
        self.num_hi_genes_per_mb = self.num_hi_genes / self.mb
        self.num_ts_genes_per_mb = self.num_ts_genes / self.mb
        self.num_genes_per_mb = self.num_genes() / self.mb

    def to_string(self):
        features = [self.patient_id, self.pathogenicity, self.variant_class, self.inheritance, self.length,
                    self.num_genes(),
                    self.hpo_matches, self.gene_matches, self.weighted_score, self.unique_matches,
                    self.unique_over_input,
                    self.num_hi_genes, self.num_ts_genes, self.overlaps_hi, self.overlaps_ts, self.hpo_matches_per_mb,
                    self.unique_matches_per_mb, self.gene_matches_per_mb, self.weighted_score_per_mb,
                    self.num_hi_genes_per_mb,
                    self.num_ts_genes_per_mb, self.num_genes_per_mb]
        for feature in features:
            feature = str(feature)
        return '\t'.join(features)


def read_patient_data():
    all_patient_data = {}
    with open('/Users/jacob/Downloads/decipher-cnvs-grch38-2022-08-28.txt', 'r') as infile:
        infile.readline()
        infile.readline()

        for line in infile:
            col = line.split('\t')
            patient_id = col[0]

            pathogenicity = col[8]
            if pathogenicity.lower() not in ['likely pathogenic', 'pathogenic', 'likely benign', 'benign']:
                continue

            hpo_accessions = col[11]
            if hpo_accessions.strip() == '':
                continue

            patient_id = col[0]
            chr = col[1]
            start = col[2]
            end = col[3]
            genotype = col[5]
            variant_class = col[6]
            inheritance = col[7]
            pathogenicity = col[8]
            hpo_accessions = col[11].strip()
            num_hpos = len(hpo_accessions.split('|'))

            all_patient_data[patient_id] = Variant(chr=chr, end=end, genotype=genotype, hpo_accessions=hpo_accessions,
                                                   inheritance=inheritance, num_hpos=num_hpos,
                                                   pathogenicity=pathogenicity,
                                                   patient_id=patient_id, start=start, variant_class=variant_class)
        infile.close()
    return all_patient_data


def add_ml_metrics(variant_data):
    for patient_id, variant in variant_data.items():
        try:
            coordinates = 'chr' + variant.chr + ':' + variant.start + '-' + variant.end
            print(patient_id)
            var = get_one_variant({}, coordinates, variant.hpo_accessions, ret='Dictionary')
            variant.genes = var['genes']
            variant.hpo_matches = var['hpo_matches']
            variant.unique_matches = len(var['unique_matches'].keys())
            variant.unique_over_input = variant.unique_matches / variant.num_hpos
            variant.gene_matches = var['gene_matches']
            variant.tads = var['tads']
            variant.weighted_score = var['weighted_score']
            variant.length = int(variant.end) - int(variant.start)

            # Determine if the variant completely overlaps a dosage sensitive region
            variant.overlaps_hi, variant.overlaps_ts = overlaps_dosage_sensitive_region(variant.chr, variant.start,
                                                                                        variant.end)
            # Determine the number of dosage sensitive genes within all TADs affected by the variant
            variant.num_hi_genes, variant.num_ts_genes = number_dosage_sensitive_genes(variant.genes)

            variant.get_tad_boundaries()
            variant.create_length_based_parameters()

        except Exception as e:
            print(e)
            print('Failed: ' + patient_id)
            print(var)
            continue


def write_data(variant_data):
    with open('decipher_data_for_ml_12_1_22.txt', 'w') as outfile:
        outfile.write('\t'.join(
            ['Patient ID', 'Pathogenicity', 'Variant Class', 'Inheritance', 'Length', 'Genes', 'HPO Matches',
             'Gene Matches', 'Weighted Score', 'Unique Matches', 'Unique Over Input', 'HI Genes',
             'TS Genes', 'Overlaps HI Region', 'Overlaps TS Region', 'HPO Matches Per Mb', 'Unique Matches Per Mb',
             'Gene Matches Per Mb', 'Weighted Score Per Mb', 'HI Genes Per Mb', 'TS Genes Per Mb',
             'Genes Per Mb']
        ))
        outfile.write('\n')
        for variant in variant_data.values():
            outfile.write(variant.to_string())
            outfile.write('\n')
        outfile.close()


class GeneRegion:

    def __init__(self, gene_region, name, chr, start, end, hi, ts):
        self.gene_region = gene_region
        self.name = name
        self.chr = chr
        self.start = start
        self.end = end
        self.hi = hi
        self.ts = ts


hi_gene_data = {}
hi_region_data = {}


def read_hi_data():
    # tableExport.txt is derived from ClinGen Dosage Sensitivity page
    with open('home/management/commands/tableExport.txt', 'r') as infile:
        reader = csv.reader(infile, delimiter=',', quotechar='"')
        reader.next()
        for row in reader:
            gene_region = 'region'
            if 'G' in row[0]:
                gene_region = 'gene'
            gene_region_name = row[1]
            coordinates = row[3]
            hi_score = row[4]
            ts_score = row[5]
            if 'Sufficient Evidence' not in hi_score + ts_score:
                continue
            chromosome = coordinates.split(':')[0]
            start_end = coordinates.split(':')[1]
            start = start_end.split('-')[0]
            end = start_end.split('-')[1]
            region = GeneRegion(gene_region, gene_region_name, chromosome, start, end, hi_score, ts_score)
            if gene_region == 'gene':
                hi_gene_data[gene_region_name] = region
            if gene_region == 'region':
                if chromosome not in hi_region_data:
                    hi_region_data[chromosome] = []
                hi_region_data[chromosome].append(region)


def overlaps_dosage_sensitive_region(chr, start, end):
    regions = hi_region_data[chr]
    haploinsufficient = 0
    triplosensitive = 0
    for region in regions:
        if start <= region.start and end >= region.end:
            if 'Sufficient Evidence' in region.hi:
                haploinsufficient = 1
            if 'Sufficient Evidence' in region.ts:
                triplosensitive = 1
    return haploinsufficient, triplosensitive


def number_dosage_sensitive_genes(genes):
    num_hi = 0
    num_ts = 0
    for gene in genes:
        if gene.name in genes.keys():
            if 'Sufficient Evidence' in genes[gene.name].hi:
                num_hi += 1
            if 'Sufficient Evidence' in genes[gene.name].ts:
                num_ts += 1
    return num_hi, num_ts
