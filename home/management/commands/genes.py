from home.models import *
import re
import json

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('elements', nargs='*')

    def handle(self, *args, **options):
        gene_dict = {}
        with open('home/management/commands/gene_files/Homo_sapiens.GRCh37.87.gtf', 'r') as in_file:
            for line in in_file :
                if line.startswith('#'):
                    continue
                col = line.split('\t')
                chr = col[0].lower()
                e_type = col[2].lower()
                use_line = False
                if chr.isdigit() or chr in ['x','y']:
                    use_line = True
                if e_type != 'transcript':
                    use_line = False
                if not use_line:
                    continue
                start = int (col[3])
                # print(line)
                end = int (col[4])
                t_name = col[8].lower()
                gene_search = re.search(r'gene_name ".+?"', t_name)
                gene_name = gene_search.group(0).replace('gene_name "' , '').replace('"', '')
                transcript_search = re.search(r'transcript_biotype ".+?"', t_name)
                transcript_biotype = transcript_search.group(0).replace('transcript_biotype "' , '').replace('"', '')
                if transcript_biotype != 'protein_coding':
                    continue
                if gene_name not in gene_dict:
                    gene_dict[gene_name] = [chr, start, end]
                else:
                    if start < gene_dict[gene_name][1]:
                        gene_dict[gene_name][1] = start
                    if end > gene_dict[gene_name][2]:
                        gene_dict[gene_name][2] = end

        # write these to file for gene in gene_dict.values 
        with open('home/management/commands/gene_files/geneFile.txt', 'w') as f:    
            f.write(json.dumps(gene_dict))
