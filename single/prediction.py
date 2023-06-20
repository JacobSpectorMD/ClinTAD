import numpy as np
import pickle

from home.helper import parse_coordinates, parse_phenotypes
from home.management.commands.ml_decipher import add_ml_metrics, Variant


class Prediction:
    feature_dict = {
        0: 'variant_class',
        1: 'inheritance',
        2: 'length',
        3: 'num_genes',
        4: 'hpo_matches',
        5: 'gene_matches',
        6: 'weighted_score',
        7: 'unique_matches',
        8: 'unique_over_input',
        9: 'num_hi_genes',
        10: 'num_ts_genes',
        11: 'overlaps_hi',
        12: 'overlaps_ts',
        13: 'hpo_matches_per_mb',
        14: 'unique_matches_per_mb',
        15: 'gene_matches_per_mb',
        16: 'weighted_score_per_mb',
        17: 'num_hi_genes_per_mb',
        18: 'num_ts_genes_per_mb',
        19: 'num_genes_per_mb'
    }

    def __init__(self, coordinates, phenotypes, inheritance):
        print(coordinates, phenotypes, inheritance)
        self.coordinates = coordinates
        self.inheritance = inheritance
        self.phenotypes = phenotypes

        chromosome, start, end = parse_coordinates(coordinates)
        self.variant = Variant(chr=chromosome, end=end, start=start, hpo_accessions=phenotypes, inheritance=inheritance,
                               num_hpos=len(parse_phenotypes(phenotypes)), variant_class=1)

    def get_feature_values(self):
        feature_values = np.zeros(20)
        for i in range(20):
            feature_name = self.feature_dict[i]
            try:
                feature_values[i] = getattr(self.variant, feature_name)
            except TypeError:
                method = getattr(self.variant, feature_name)
                feature_values[i] = method()
        print(feature_values)
        return feature_values

    def predict(self):
        add_ml_metrics(self.variant)
        feature_values = self.get_feature_values()
        with open('single/cnv_model.sav', 'rb') as model_file:
            model = pickle.load(model_file)
            model_file.close()
        prediction = model.predict([feature_values])
        if prediction[0] == 1:
            pathogenicity = 'Pathogenic'
        else:
            pathogenicity = 'Not Pathogenic'
        print(model.predict_proba([feature_values]))
        print(prediction[0], pathogenicity)
        return pathogenicity
