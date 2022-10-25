import datetime
import json

from django.core import management
from django.core.management.base import BaseCommand
from home.statistics import get_one_variant


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Read in the patient data
        patient_data = read_patient_data()

        # Get all of the metric for machine learning
        add_ml_metrics(patient_data)

        # Write the data to a file
        write_data(patient_data)


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

            all_patient_data[patient_id] = {
                'patient_id': col[0],
                'chr': col[1],
                'start': col[2],
                'end': col[3],
                'genotype': col[5],
                'variant_class': col[6],
                'inheritance': col[7],
                'pathogenicity': col[8],
                'hpo_accessions': col[11].strip(),
                'num_hpos': len(hpo_accessions.split('|'))
            }
        infile.close()
    return all_patient_data


def add_ml_metrics(patient_data):
    for patient_id, pd in patient_data.items():
        try:
            coordinates = 'chr' + pd['chr'] + ':' + pd['start'] + '-' + pd['end']
            print(patient_id)
            var = get_one_variant({}, coordinates, pd['hpo_accessions'], ret='Dictionary')
            pd['hpo_matches'] = var['hpo_matches']
            # pd['unique_matches'] = var['unique_matches']
            pd['unique_matches'] = len(var['unique_matches'].keys())
            pd['unique_over_input'] = pd['unique_matches'] / pd['num_hpos']
            pd['gene_matches'] = var['gene_matches']
            pd['tads'] = var['tads']
            pd['weighted_score'] = var['weighted_score']
            pd['length'] = int(pd['end']) - int(pd['start'])
            print(pd)
        except Exception as e:
            print(e)
            print('Failed: ' + patient_id)
            print(var)
            continue


def write_data(patient_data):
    with open('decipher_data_for_ml.txt', 'w') as outfile:
        outfile.write('\t'.join(
            ['Patient ID', 'Pathogenicity', 'Variant Class', 'Inheritance', 'Length', 'HPO Matches', 'Gene Matches',
             'Weighted Match Score', 'Unique Matches', 'Unique HPO Matches/Input HPOs']))
        outfile.write('\n')
        for p in patient_data.values():
            outfile.write('\t'.join([
                p['patient_id'],
                p['pathogenicity'],
                p['variant_class'],
                p['inheritance'],
                str(p['length']),
                str(p['hpo_matches']),
                str(p['gene_matches']),
                str(p['weighted_score']),
                str(p['unique_matches']),
                str(p['unique_over_input'])
            ]))
            outfile.write('\n')
        outfile.close()
