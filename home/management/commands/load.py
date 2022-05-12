"""
    This command is used to load all of the default data into the database, or to update the data if new files are
    obtained, e.g. a new file from Human Phenotype Ontology (HPO).

    To run this file use 'python manage.py load' in your virtual environment in the root directory for the project.
"""

import os
import random
import re
import requests
import time

from home.models import *

from django.core.management.base import BaseCommand
from django.db import transaction


class HpoTemp:
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
            self.create_builds()
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
            if 'builds' in options['elements']:
                self.create_builds()
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

    def create_builds(self):
        """
        Create the genome builds.
        """
        print('Loading builds.')
        ncbi36 = Build.objects.filter(name='NCBI36').first()
        if not ncbi36:
            Build.objects.create(long_name='hg18/NCBI36', name='NCBI36')

        grch37 = Build.objects.filter(name='GRCh37').first()
        if not grch37:
            Build.objects.create(long_name='hg19/GRCh37', name='GRCh37')

        grch38 = Build.objects.filter(name='GRCh38').first()
        if not grch38:
            Build.objects.create(long_name='hg38/GRCh38', name='GRCh38')
        print('Builds loaded.')

    def load_chromosomes(self):
        """
        This function creates chromosomes and adds/updates their length.
        """
        print('Loading chromosomes.')
        folder = 'home/files/chromosomes'
        files = os.listdir(folder)
        for file in files:
            with open(os.path.join(folder, file)) as infile:
                for line in infile:
                    col = line.split('\t')
                    if line.startswith('#') or len(col) != 3:
                        continue
                    number = col[0].replace('chr', '').upper()
                    build_name = col[1]
                    build = Build.objects.get(name=build_name)
                    length = int(col[2].replace(',', ''))
                    chromosome = Chromosome.objects.filter(build=build, number=number).first()
                    if not chromosome:
                        chromosome = Chromosome.objects.create(build=build, number=number)
                    chromosome.length = length
                    chromosome.save()
        print('Chromosomes loaded.')

    def load_genes(self):
        """
        This function reads the .gtf files from Ensembl to add genes and coordinates. For more information about the
        specific files used, see the home/files/genes/ReadMe.md file.
        """
        print('Loading genes.')
        folder = 'home/files/genes/'
        files = os.listdir(folder)
        for file in files:
            if '.gtf' not in file:
                continue
            build_name = file.split('.')[1]
            build = Build.objects.get(name__iexact=build_name)
            gene_dict = {gene.ensembl_id: gene for gene in Gene.objects.filter(build=build)}

            with open(os.path.join(folder, file), 'r') as infile:
                for line in infile:
                    if line.startswith('#'):
                        continue
                    col = line.strip().split('\t')
                    element_type = col[2]
                    if element_type != 'transcript' or len(col) < 8:
                        continue

                    # Skip anything that is not protein coding
                    gene_biotype = re.search(r'(?<=gene_biotype ").+?(?=")', line).group(0)
                    transcript_biotype = re.search(r'(?<=transcript_biotype ").+?(?=")', line).group(0)
                    if gene_biotype != 'protein_coding' or transcript_biotype != 'protein_coding':
                        continue

                    ensembl_id = re.search(r'(?<=gene_id ").+?(?=")', line).group(0)
                    ensembl_id = int(re.sub(r'\D', '', ensembl_id))
                    gene_search = re.search(r'(?<=gene_name ").+?(?=")', line)
                    if not gene_search:
                        gene_name = ''
                    else:
                        gene_name = gene_search.group(0)

                    chr_number = col[0]
                    start = int(col[3])
                    end = int(col[4])
                    chromosome = Chromosome.objects.filter(build=build, number=chr_number).first()
                    if not chromosome:
                        continue

                    if ensembl_id in gene_dict:
                        gene = gene_dict[ensembl_id]
                    else:
                        gene = Gene.objects.filter(build=build, ensembl_id=ensembl_id).first()
                        gene_dict[ensembl_id] = gene
                    print(build.name, gene_name, ensembl_id)

                    if gene is None:
                        gene = Gene.objects.create(build=build, chromosome=chromosome, ensembl_id=ensembl_id,
                                                   name=gene_name,
                                                   start=start, end=end, updated=True)
                        gene_dict[ensembl_id] = gene
                    elif gene:
                        updated = False
                        if gene_name and gene.name == '':
                            gene.name = gene_name
                            updated = True
                        if start < gene.start or not gene.updated:
                            gene.start = start
                            updated = True
                        if end > gene.end or not gene.updated:
                            gene.end = end
                            updated = True

                        if updated:
                            gene.updated = True
                            gene.save()
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
        build = Build.objects.get(name='GRCh37')
        track = Track.objects.filter(build=build, default=True, track_type='enhancer')
        if not track:
            track = Track.objects.create(build=build, default=True, label='VISTA', track_type='enhancer')

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
                    print(vista_element)
                    chromosome = Chromosome.objects.get(build=build, number=chromosome_num)
                    enhancer = Enhancer.objects.filter(build=build, vista_element=vista_element).first()
                    if not enhancer:
                        enhancer_list.append(
                            Enhancer(build=build, chromosome=chromosome, start=start, end=end, track=track,
                                     vista_element=vista_element))
            Enhancer.objects.bulk_create(enhancer_list)
        print('Enhancers loaded.')

    def load_hpos(self):
        print('Creating HPO objects.')
        # HPO.objects.all().delete()
        # hpo_list = []
        # hpo_objs = []
        # with open('home/files/hp-obo.txt', 'r') as infile:
        #     for i in range(29):
        #         infile.readline()
        #     for line in infile:
        #         if line.rstrip() == '[Term]':
        #             hpo = HpoTemp()
        #             hpo_list.append(hpo)
        #         if line[0:2] == 'id':
        #             hpo.id = int(line[7:].rstrip())
        #         if line[0:4] == 'name':
        #             hpo.name = line[6:].rstrip()
        #         if line[0:3] == 'def':
        #             col = line.rstrip().split('"')
        #             hpo.definition = col[1]
        #         if line[0:7] == 'comment':
        #             col = line.rstrip().split(':')
        #             hpo.comment = col[1]
        # for hpo in hpo_list:
        #     hpo_objs.append(HPO(hpoid=hpo.id, name=hpo.name, definition=hpo.definition, comment=hpo.comment))
        # HPO.objects.bulk_create(hpo_objs)
        print('HPO objects created.')

        print('Creating gene to HPO relationships.')
        # Create HPO to gene relationships
        with open('home/files/hpo/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt', 'r') as infile:
            infile.readline()
            old_gene_name = ''
            hpo_list = []
            for line in infile:
                col = line.split('\t')
                gene_name = col[1].strip()
                hpo_id = int(col[3].split(':')[1])

                # If the line represents a different gene, add all of the hpo phenotypes to the previous gene
                if old_gene_name != gene_name:
                    print(old_gene_name)
                    genes = Gene.objects.filter(name__iexact=old_gene_name)
                    for gene in genes:
                        gene.hpos.add(*hpo_list)
                        gene.save()
                    old_gene_name = gene_name
                    hpo_list = []

                hpo = HPO.objects.filter(hpoid=hpo_id).first()
                if hpo:
                    hpo_list.append(hpo)
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
            omim_dict = {}
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

                omim = Omim.objects.filter(omim_number=omim_number).first()
                if not omim:
                    # Add new omims to the list to be created
                    new_omim = Omim(omim_number=omim_number, title=title)
                    omims.append(new_omim)
                elif omim:
                    # Make sure exisiting omims are up-to-date
                    if omim.title != title:
                        omim.title = title
                        omim.save()

            Omim.objects.bulk_create(omims)
            infile.close()

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

                        time.sleep(random.randint(1000, 2000) / 1000)
                        params = {'apiKey': os.environ.get('OMIM_API_KEY'), 'mimNumber': omim_number, 'format': 'json',
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
                if len(col) < 13:
                    # Skip rows without phenotypes
                    continue

                symbols = col[6]
                if len(col) >= 9:
                    approved_symbols = col[8]
                else:
                    approved_symbols = ''
                all_symbols = symbols + approved_symbols

                if len(col) >= 11:
                    ensembl_id = col[10]
                else:
                    ensembl_id = None
                genes = None
                if ensembl_id:
                    ensembl_id = int(ensembl_id.replace('ENSG', ''))
                    genes = Gene.objects.filter(ensembl_id=ensembl_id)
                elif approved_symbols:
                    genes = Gene.objects.filter(name=approved_symbols)

                if not genes:
                    continue

                if genes.first().name.lower() not in all_symbols.lower():
                    print('\033[91mWARNING - gene name (' + gene.name + ') is not in the symbols column.\033[0m')
                    print(col)

                phenotypes = col[12].split(';')

                print('\n', approved_symbols, '(', ensembl_id, ')', end=' - ')
                for phenotype in phenotypes:
                    omim_search = re.search(r'\d{6}', phenotype)
                    if omim_search:
                        omim_number = omim_search.group(0)
                        print(omim_number)
                    else:
                        continue

                    omim = Omim.objects.filter(omim_number=omim_number).first()
                    if not omim:
                        print('\033[91mWARNING - OMIM number ' + omim_number + ' does not exist.\033[0m')
                        continue

                    for gene in genes:
                        if omim not in gene.omims.all():
                            gene.omims.add(omim)
                            gene.save()

    def load_tads(self):
        print('Loading in TAD boundaries.')
        # Load TAD boundaries
        folder = 'home/files/tads'
        files = os.listdir(folder)
        for file in files:
            if 'hg19_hESC_default' not in file or '.txt' not in file:
                continue
            file_name = file.replace('.txt', '')
            print(file_name)
            build_name = file.split('_')[0]
            build = Build.objects.get(long_name__icontains=build_name)

            if 'default' in file:
                track = Track.objects.filter(build=build, default=True, track_type='tad').first()
                if not track:
                    track = Track.objects.create(build=build, default=True, track_type='tad', label='TADs')
            else:
                track = Track.objects.filter(build=build, long_name=file_name, track_type='tad').first()
                if not track:
                    track = Track.objects.create(build=build, label=file.split('_')[1], long_name=file_name,
                                                 track_type='tad')
            has_tads = False
            if track.tads.count() > 0:
                has_tads = True
            with open(folder + '/' + file, 'r') as infile:
                line_count = 0
                for line in infile:
                    if line.strip() != '':
                        line_count += 1

                if line_count == track.tads.count():
                    continue

                infile.seek(0, 0)
                tad_list = []
                for line in infile:
                    col = line.split('\t')
                    if len(col) < 3:
                        continue
                    chr_num = col[0].upper().strip().replace('CHR', '')
                    chromosome = Chromosome.objects.get(build=build, number=chr_num)
                    start = int(col[1])
                    end = int(col[2])
                    if not has_tads:
                        tad_list.append(TAD(build=build, chromosome=chromosome, start=start, end=end, track=track))
                    elif has_tads:
                        tad = TAD.objects.filter(build=build, chromosome=chromosome, start=start, end=end,
                                                 track=track).first()
                        if not tad:
                            tad_list.append(TAD(build=build, chromosome=chromosome, start=start, end=end, track=track))
                TAD.objects.bulk_create(tad_list)
                infile.close()
        print('TAD boundaries loaded.')

    def load_cnvs(self):
        print('Loading CNVs from DGV.')

        folder = 'home/files/cnvs'
        files = os.listdir(folder)
        for file in files:
            if '.gff' not in file:
                continue

            with open(folder + '/' + file, 'r') as infile:
                build_name = file.split('.')[-2]
                build = Build.objects.filter(long_name__icontains=build_name).first()
                track = Track.objects.filter(build=build, default=True, track_type='cnv').first()
                if not track:
                    track = Track.objects.create(build=build, default=True, label='DGV', track_type='cnv')

                i = 0
                for line in infile:
                    line = line
                    col = line.split('\t')
                    variant_acc = re.search(r'(?<=ID=).+?(?=;)', line).group(0)
                    subtype = re.search(r'(?<=variant_sub_type=).+?(?=;)', line).group(0).lower()
                    chromosome_num = col[0].replace('chr', '')
                    outer_start = int(re.search(r'(?<=outer_start=).+?(?=;)', line).group(0))
                    inner_start = int(re.search(r'(?<=inner_start=).+?(?=;)', line).group(0))
                    inner_end = int(re.search(r'(?<=inner_end=).+?(?=;)', line).group(0))
                    outer_end = int(re.search(r'(?<=outer_end=).+?(?=;)', line).group(0))
                    studies = re.search(r'(?<=Studies=).+?(?=;)', line).group(0)
                    frequency = float(re.search(r'(?<=Frequency=).+?(?=%)', line).group(0))
                    sample_size_search = re.search(r'(?<=Number_of_unique_samples_tested=).+?(?=\s+)', line)
                    if sample_size_search:
                        sample_size = int(sample_size_search.group(0))
                    else:
                        sample_size = -1
                    chromosome = Chromosome.objects.get(build=build, number=chromosome_num)

                    variant = Variant.objects.filter(accession=variant_acc, build=build).first()
                    if not variant:
                        print(build.name, variant_acc)
                        Variant.objects.create(accession=variant_acc, build=build, chromosome=chromosome,
                                               outer_start=outer_start, inner_start=inner_start,
                                               inner_end=inner_end, outer_end=outer_end,
                                               subtype=subtype, study=studies, frequency=frequency,
                                               sample_size=sample_size, track=track)
                    # else:
                    #     variant.chromosome = chromosome
                    #     variant.outer_start = outer_start
                    #     variant.inner_start = inner_start
                    #     variant.inner_end = inner_end
                    #     variant.outer_end = outer_end
                    #     variant.subtype = subtype
                    #     variant.study = studies
                    #     variant.frequency = frequency
                    #     variant.sample_size = sample_size
                    #     variant.track = track
                    #     variant.save()
        print('CNVs from DGV loaded.')
