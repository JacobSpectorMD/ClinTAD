import os
import json
import random
import re
import requests
import time

from home.models import *

from django.core.management.base import BaseCommand
from django.db import transaction


class HPO_temp:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.definition = ''
        self.comment = ''


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('elements', nargs='*')

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
            self.load_mim_titles()
            self.load_omim_inheritance()
            self.load_omim_to_hpo()
            print('Finished loading data!!')
        elif len(options['elements']) > 0:
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
            if 'ensembl_ids' in options['elements']:
                self.load_ensembl_ids()
            if 'omim_titles' in options['elements']:
                self.load_omim_titles()
            if 'omim_inheritance' in options['elements']:
                self.load_omim_inheritance()
            if 'omim_to_hpo' in options['elements']:
                self.load_omim_to_hpo()
            if 'omim_to_gene' in options['elements']:
                self.load_omim_to_gene()
        else:
            print('Please choose what data you would like to load')
            print('Example: python manage.py load chromosomes')
            print('Example: python manage.py load genes omim_inheritance')

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

    def load_ensembl_ids(self):
        with open('home/files/hgnc/hgnc_data.txt', 'r') as infile:
            for line in infile:
                if line[0] == '#':
                    continue
                col = line.split('\t')
                symbol = col[0]
                ensembl_id = col[7].strip().replace('ENSG', '')

                gene = Gene.objects.filter(name__iexact=symbol).first()
                if not gene:
                    continue
                if ensembl_id:
                    ensembl_id = int(ensembl_id)
                elif not ensembl_id:
                    if col[2] == 'Approved':
                        print('No Ensembl ID for ', symbol)
                    continue

                gene.ensembl_id = ensembl_id
                gene.save()

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

    def load_omim_titles(self):
        with open('home/files/omim/mimTitles.txt', 'r') as infile:
            omims = []
            for line in infile:
                col = line.split('\t')

                if line[0] == '#':
                    continue
                if col[0] in ['Caret', 'Asterisk']:
                    # Caret means entries have been removed
                    # Asterisk means they are genes
                    continue

                omim_number = int(col[1].strip())
                title = col[2].strip()
                omim = Omim.objects.filter(title=title).first()
                if not omim:
                    new_omim = Omim(omim_number=omim_number, title=title)
                    omims.append(new_omim) 
            Omim.objects.bulk_create(omims)

    def load_omim_inheritance(self):
        with open('home/files/omim/genemap2.txt', 'r') as infile:
            for line in infile:
                if line[0] == '#':
                    continue
                col = line.split('\t')

                # Find the inheritance for each OMIM number in the phenotype section
                phenotype_section = col[12]
                phenotypes = phenotype_section.split(';')
                for phenotype in phenotypes:
                    phenotype = phenotype.lower()
                    omim_search = re.search(r'\d{6}', phenotype)
                    if omim_search:
                        omim_number = omim_search.group(0)
                        omim = Omim.objects.filter(omim_number=omim_number).first()
                        if not omim:
                            continue
                        if omim.autosomal_recessive or omim.autosomal_dominant or omim.digenic_recessive or \
                        omim.digenic_dominant or omim.digenic or omim.multifactorial or omim.x_linked_recessive or \
                        omim.x_linked_dominant or omim.x_linked or omim.y_linked:
                            continue

                        time.sleep(random.randint(1000, 2000)/1000)
                        params = {'apiKey': '***REMOVED***', 'mimNumber': omim_number, 'format': 'json',
                                  'include': 'geneMap'}
                        response = requests.get("https://api.omim.org/api/entry", params=params)
                        entry = response.json()['omim']['entryList'][0]['entry']
                        try:
                            phenotype_map_list = entry['phenotypeMapList']
                            for phenotypeMap in phenotype_map_list:
                                phenotype_mim_number = phenotypeMap['phenotypeMap']['phenotypeMimNumber']
                                phenotype_inheritance = phenotypeMap['phenotypeMap']['phenotypeInheritance'].lower()

                                if 'autosomal recessive' in phenotype_inheritance:
                                    omim.autosomal_recessive = True
                                if 'autosomal dominant' in phenotype_inheritance:
                                    omim.autosomal_dominant = True
                                if 'digenic' in phenotype_inheritance:
                                    if 'digenic dominant' in phenotype_inheritance:
                                        omim.digenic_dominant = True
                                    if 'digenic recessive' in phenotype_inheritance:
                                        omim.digenic_recessive = True
                                    if 'digenic dominant' not in phenotype_inheritance and \
                                            'digenic recessive' not in phenotype_inheritance:
                                        omim.digenic = True
                                if 'multifactorial' in phenotype_inheritance:
                                    omim.multifactorial = True
                                if 'x-linked' in phenotype_inheritance:
                                    if 'x-linked dominant' in phenotype_inheritance:
                                        omim.x_linked_dominant = True
                                    if 'x-linked recessive' in phenotype_inheritance:
                                        omim.x_linked_recessive = True
                                    if 'x-linked dominant' not in phenotype_inheritance and \
                                            'x-linked recessive' not in phenotype_inheritance:
                                        omim.x_linked = True
                                if 'y-linked' in phenotype_inheritance:
                                    omim.y_linked = True
                                omim.save()
                                print(phenotype_mim_number, phenotype_inheritance)
                                print('AR:', omim.autosomal_recessive, 'AD:', omim.autosomal_dominant,
                                      'D:', omim.digenic, 'DR:', omim.digenic_recessive, 'DD:', omim.digenic_dominant,
                                      'M:', omim.multifactorial, 'X:', omim.x_linked, 'XR:', omim.x_linked_recessive,
                                      'XD:', omim.x_linked_dominant)
                        except:
                            print(omim_number, '- could not get inheritance.')

                        # entry = json.loads(response)
                        # print(entry.entryList.geneMap)

    def load_omim_to_hpo(self):
        with open('home/files/hpo/phenotype.hpoa', 'r') as infile:
            for line in infile:
                if line[0] == '#':
                    continue
                col = line.split('\t')
                if col[0] == 'DatabaseID' or 'OMIM:' not in col[0]:
                    continue
                omim_number = int(col[0].strip().replace('OMIM:', ''))
                print(omim_number)
                hpo_id = int(col[3].strip().replace('HP:', ''))
                omim = Omim.objects.filter(omim_number=omim_number).first()
                hpo = HPO.objects.filter(hpoid=hpo_id).first()
                if omim and hpo:
                    if hpo not in omim.hpos.all():
                        print('OMIM:', omim_number, 'HPO:', hpo_id)
                        omim.hpos.add(hpo)
                        omim.save()
            infile.close()

    def load_omim_to_gene(self):
        with open('home/files/omim/genemap2.txt', 'r') as infile:
            i = 0
            for line in infile:
                i += 1
                if i % 500 == 0:
                    print(i, line, end='')
                if line[0] == '#':
                    continue
                col = line.split('\t')

                ensembl_id = col[10]
                if ensembl_id:
                    ensembl_id = int(ensembl_id.replace('ENSG', ''))
                else:
                    continue

                gene = Gene.objects.filter(ensembl_id=ensembl_id).first()
                if not gene:
                    continue
                symbols = col[6]
                approved_symbols = col[8]
                all_symbols = symbols + approved_symbols
                if gene.name.lower() not in all_symbols.lower():
                    print('\033[91mWARNING - gene name ('+gene.name+') is not in the symbols column.\033[0m')
                    print(col)

                phenotypes = col[12].split(';')
                for phenotype in phenotypes:
                    omim_search = re.search(r'\d{6}', phenotype)
                    if omim_search:
                        omim_number = omim_search.group(0)
                    else:
                        continue

                    omim = Omim.objects.filter(omim_number=omim_number).first()
                    if not omim:
                        print('\033[91mWARNING - OMIM number '+omim_number+' does not exist.\033[0m')
                        continue
                    if omim not in gene.omims.all():
                        gene.omims.add(omim)
                        gene.save()

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
                tad_list.append(TAD(chromosome=chromosome, start=start, end=end))
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
