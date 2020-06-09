import json
import random
from statistics import mean

from django.core.management.base import BaseCommand

from home.clintad import GetTADs
from home.models import Gene, HPO
from home.statistics import get_n_variants
from user.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Find all genes with HPO for autism
        # hpo = HPO.objects.get(hpoid=717)
        # genes = Gene.objects.filter(hpos__in=[hpo]).all()
        # 
        # hpo_scores = {}
        # for gene in genes:
        #     for hpo in gene.hpos.all():
        #         if hpo.name not in hpo_scores:
        #             hpo_scores[hpo.name] = {'name': hpo.name, 'object': hpo, 'score': 1, 'random_scores': []}
        #         else:
        #             hpo_scores[hpo.name]['score'] += 1
        # 
        # all_genes = list(Gene.objects.all())
        # for _ in range(1000):
        #     if _ % 25 == 0:
        #         print(_)
        #     random_genes = random.sample(all_genes, 114)
        #     hpo_scores_run = {}
        #     for gene in random_genes:
        #         for hpo in gene.hpos.all():
        #             if hpo.name in hpo_scores:
        #                 if hpo.name not in hpo_scores_run:
        #                     hpo_scores_run[hpo.name] = 1
        #                 else:
        #                     hpo_scores_run[hpo.name] += 1
        # 
        #     for hpo_name, score in hpo_scores_run.items():
        #         hpo_scores[hpo_name]['random_scores'].append(score)
        # 
        # score_list = []
        # for score in hpo_scores.values():
        #     score['weighted_score'] = round(score['score'] * score['object'].weight, 2)
        #     if len(score['random_scores']) > 0:
        #         score['random_score_mean'] = mean(score['random_scores'])
        #         score['enriched'] = score['score'] / score['random_score_mean']
        #     else:
        #         score['random_score_mean'] = 0
        #         score['enriched'] = 0
        #     score_list.append(score)
        # score_list.sort(key=lambda x: x['score'], reverse=True)
        # 
        # outfile = open('home/management/commands/polygenic.txt', 'w')
        # for score in score_list:
        #     outfile.write(score['name']+'\t'+str(score['score'])+'\t'+str(score['enriched'])+'\n')
        # outfile.close()

        # infile = open('home/management/commands/polygenic.txt', 'r')
        # outfile = open('home/management/commands/high_scoring_hpos.txt', 'w')
        # for line in infile:
        #     col = line.split('\t')
        #     if float(col[2]) > 12:
        #         hpo = HPO.objects.get(name=col[0])
        #         outfile.write(str(hpo.hpoid)+'; ')

        enriched_hpos = {}
        infile = open('home/management/commands/polygenic.txt', 'r')
        for line in infile:
            col = line.split('\t')
            if float(col[2]) > 12:
                hpo_obj = HPO.objects.get(name=col[0].strip())
                enriched_hpos[hpo_obj.hpoid] = {'actual': 0, 'hpo': hpo_obj.hpoid}
        infile.close()

        user = User.objects.get(email='jacobdspector@gmail.com')
        fake_request = Request(user)

        # i = 0
        # with open('home/management/commands/asd_cnvs_unique.txt', 'r') as infile:
        #     outfile = open('home/management/commands/asd_cnvs_unique2.txt', 'a')
        # 
        #     cnvs = {}
        #     for line in infile:
        #         i += 1
        #         print(i)
        #         col = line.split('\t')
        #         chr = col[0].replace('chr', '')
        #         start = col[1].strip()
        #         end = col[2].strip()
        # 
        #         tad_data = json.loads(GetTADs(fake_request, '1', chr, start, end, '[]', 0, source_function='single'))
        # 
        #         near_autism = False
        #         for gene in tad_data['genes']:
        #             for phenotype in gene['phenotypes']:
        #                 hpo = phenotype['hpo']
        #                 if int(hpo) == 717:  # Skip any CNVs near a gene associated with autism
        #                     near_autism = True
        #                     break
        #             if near_autism:
        #                 break
        #         if near_autism:
        #             continue
        #         if str(chr+start+end) not in cnvs:
        #             outfile.write(chr+'\t'+start+'\t'+end+'\n')
        #         cnvs[chr+start+end] = {'chr': chr, 'start': start, 'end': end}

        with open('home/management/commands/asd_cnvs_unique2.txt', 'r') as infile:
            i = 0
            for line in infile:
                i+=1
                print(i)
                col = line.split('\t')
                chr = col[0].replace('chr', '')
                start = col[1].strip()
                end = col[2].strip()

                tad_data = json.loads(GetTADs(fake_request, '1', chr, start, end, '[]', 0, source_function='single'))
                for gene in tad_data['genes']:
                    for phenotype in gene['phenotypes']:
                        hpo = int(phenotype['hpo'])
                        if hpo in enriched_hpos:
                            enriched_hpos[hpo]['actual'] += 1
            infile.close()

        enriched_list = list(enriched_hpos.values())
        enriched_list.sort(key=lambda x: x['hpo'])
        with open('home/management/commands/asd_results.txt', 'a') as outfile:
            hpos = [str(hpo['hpo']) for hpo in enriched_list]
            outfile.write('\t'.join(hpos))
            outfile.write('\n')
            scores = [str(hpo['actual']) for hpo in enriched_list]
            outfile.write('\t'.join(scores))
            outfile.write('\n')
            outfile.close()

        for _ in range(100):
            print(_)
            hpo_dict = {}
            for hpo in enriched_hpos:
                hpo_dict[hpo] = {'hpo': hpo, 'actual': 0}
            with open('home/management/commands/asd_cnvs_unique2.txt', 'r') as infile:
                for line in infile:
                    col = line.split('\t')
                    chr = col[0].replace('chr', '')
                    start = col[1].strip()
                    end = col[2].strip()

                    tad_data = get_n_variants(fake_request, chr, start, end, '[]', 1)[0]
                    for gene in tad_data['genes']:
                        for phenotype in gene['phenotypes']:
                            hpo = int(phenotype['hpo'])
                            if hpo in hpo_dict:
                                hpo_dict[hpo]['actual'] += 1
                infile.close()

            hpo_list = list(hpo_dict.values())
            hpo_list.sort(key=lambda x: x['hpo'])
            with open('home/management/commands/asd_results.txt', 'a') as outfile:
                scores = [str(hpo['actual']) for hpo in hpo_list]
                outfile.write('\t'.join(scores))
                outfile.write('\n')
                outfile.close()


class Request:
    def __init__(self, user):
        self.user = user