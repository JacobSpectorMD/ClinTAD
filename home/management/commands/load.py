from django.core.management.base import BaseCommand
from home.models import *
import os
import json


class HPO_temp:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.definition = ''
        self.comment = ''


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('elements', nargs='+')

    def handle(self, *args, **options):
        options['elements'] = [x.lower() for x in options['elements']]
        if 'all' in options['elements']:
            print('Loading all required data.')
            self.load_chromosomes()
            self.load_genes()
            self.load_enhancers()
            self.load_hpos()
            self.load_tads()
            self.load_cnvs()
            print('Finished loading data!!')
        else:
            if 'chromosomes' in options['elements']:
                self.load_chromosomes()
            if 'enhancers' in options['elements']:
                self.load_enhancers()
            if 'tads' in options['elements']:
                self.load_tads()
            if 'genes' in options['elements']:
                self.load_genes()
            if 'hpos' in options['elements']:
                self.load_hpos()
            if 'cnvs' in options['elements']:
                self.load_cnvs()

    def load_chromosomes(self):
        print('Loading chromosomes.')
        Chromosome.objects.all().delete()
        with open('home/files/chromosomeLengthsHG19.txt', 'r') as infile:
            for line in infile:
                col = line.split('\t')
                chr = col[0].replace('chr', '')
                print(chr)
                length = int(col[1])
                chromosome = Chromosome.objects.filter(number=chr).first()
                if chromosome is None:
                    chromosome = Chromosome(number=chr.upper(), length=length)
                    chromosome.save()
        print('Chromosomes loaded.')

    def load_genes(self):
        print('Loading genes.')
        path = 'home/files/genes/'
        files = os.listdir(path)
        for file in files:
            gene_list = []
            with open(path+file, 'r') as infile:
                for line in infile:
                    col = line.rstrip().split('\t')
                    chr_number = col[0]
                    chromosome = Chromosome.objects.get(number=chr_number)
                    start = col[1]
                    end = col[2]
                    name = col[3].strip()
                    gene = Gene.objects.filter(name=name).first()
                    if gene is None:
                        gene_list.append(Gene(chromosome=chromosome, name=name, start=start, end=end))
            Gene.objects.bulk_create(gene_list)
        print('Genes loaded.')

    def load_enhancers(self):
        print('Loading enhancers.')
        Enhancer.objects.all().delete()
        with open('home/files/vista enhancers.txt', 'r') as infile:
            enhancer_list = []
            for line in infile:
                if line[0] != '>':
                    continue
                cell = line.split('|')
                if 'human' in cell[0].lower() and 'positive' in cell[3]:
                    chr_coord = cell[1].split(':')
                    chromosome_num = chr_coord[0].replace('chr', '')
                    coords = chr_coord[1].split('-')
                    start, end = int(coords[0]), int(coords[1])

                    vista_element = int(cell[2].replace('element', ''))
                    chromosome = Chromosome.objects.get(number=chromosome_num)
                    enhancer_list.append(Enhancer(chromosome=chromosome, start=start, end=end,
                                                 vista_element=vista_element))
            Enhancer.objects.bulk_create(enhancer_list)
        print('Enhancers loaded.')

    def load_hpos(self):
        print('Creating HPO objects.')
        HPO.objects.all().delete()
        hpo_list = []
        hpo_objs = []
        with open('home/files/hp-obo.txt', 'r') as infile:
            for i in range(29):
                infile.readline()
            for line in infile:
                if line.rstrip() == '[Term]':
                    hpo = HPO_temp()
                    hpo_list.append(hpo)
                if line[0:2] == 'id':
                    hpo.id = int(line[7:].rstrip())
                if line[0:4] == 'name':
                    hpo.name = line[6:].rstrip()
                if line[0:3] == 'def':
                    col = line.rstrip().split('"')
                    hpo.definition = col[1]
                if line[0:7] == 'comment':
                    col = line.rstrip().split(':')
                    hpo.comment = col[1]
        for hpo in hpo_list:
            hpo_objs.append(HPO(hpoid=hpo.id, name=hpo.name, definition=hpo.definition, comment=hpo.comment))
        HPO.objects.bulk_create(hpo_objs)
        print('HPO objects created.')

        print('Creating gene to HPO relationships.')
        # Create HPO to gene relationships
        with open('home/files/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt', 'r') as infile:
            infile.readline()
            for line in infile:
                col = line.split('\t')
                gene_name = col[1].strip()
                hpo_id = col[3].split(':')
                hpo_id = int(hpo_id[1])
                try:
                    gene = Gene.objects.get(name=gene_name)
                    hpo = HPO.objects.get(hpoid=hpo_id)
                    gene.hpos.add(hpo)
                    gene.save()
                except:
                    print(gene_name+' does not exist.')
            print('Gene to HPO relationships created.')

        print('Loading in weighted scores for HPOs.')
        with open('home/files/hpo_weights.txt', 'r') as infile:
            for line in infile:
                cell = line.split('\t')
                hpo_id = int(cell[0])
                hpo_weight = float(cell[1])
                hpo = HPO.objects.get(hpoid=hpo_id)
                hpo.weight = hpo_weight
                print(hpo)
                hpo.save()
        print('Weighted scores for HPOs loaded.')

    def load_tads(self):
        print('Loading in TAD boundaries.')
        # Load TAD boundaries
        TAD.objects.all().delete()
        tad_list = []
        with open('home/files/boundary.txt', 'r') as infile:
            for line in infile:
                col = line.split('\t')
                chr_num = col[0].strip().replace('chr', '')
                chromosome = Chromosome.objects.get(number=chr_num)
                start = int(col[1])
                end = int(col[2])
                tad_list.append(TAD(chromosome=chromosome, start=end, end=end))
        TAD.objects.bulk_create(tad_list)
        print('TAD boundaries loaded.')

    def load_cnvs(self):
        print('Loading CNVs from DGV.')
        Variant.objects.all().delete()
        variant_list = []
        with open('home/files/Gold Standard Variants.txt', 'r') as infile:
            # The first line has the column names, skip it
            infile.readline()

            i = 0
            for line in infile:
                line = line.rstrip()
                col = line.split('\t')
                variant_acc = col[0]
                subtype = col[1]
                chromosome_num = col[2]
                outer_start = int(col[3])
                inner_start = int(col[4])
                inner_end = int(col[5])
                outer_end = int(col[6])
                studies = col[7]
                frequency = float(col[8])
                sample_size = int(col[9])
                chromosome = Chromosome.objects.get(number=chromosome_num)
                variant_list.append(Variant(chromosome=chromosome, outer_start=outer_start, inner_start=inner_start,
                                    inner_end=inner_end, outer_end=outer_end, subtype=subtype, accession=variant_acc,
                                    study=studies, frequency=frequency, sample_size=sample_size))
                if len(variant_list) >= 1000:
                    print(i+1)
                    Variant.objects.bulk_create(variant_list)
                    variant_list = []
                i += 1
            if len(variant_list) > 0:
                Variant.objects.bulk_create(variant_list)
        print('CNVs from DGV loaded.')
