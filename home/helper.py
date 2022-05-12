import re


def parse_coordinates(coordinates):
    try:
        coordinates = coordinates.lower().replace(',', '').replace('–', '-')
        re.sub(r'\s+', '', coordinates)
        chromosome = coordinates.split(':')[0].replace('chr', '').upper()
        numbers = coordinates.split(':')[1]
        start = numbers.split('-')[0]
        end = numbers.split('-')[1]
        return chromosome, start, end
    except:
        return None


def parse_phenotypes(phenotype_string):
    """
    Parses phenotypes submitted by the user into an array.

    Parameters
        phenotype_string: str
            A list of phenotypes in HPO ID and/or integer format, e.g. "HP:0410034, 717".
    """
    re.sub(r'\s+', '', phenotype_string)
    phenotype_list = []
    phenotypes_split = phenotype_string.split(',')
    for phenotype in phenotypes_split:
        try:
            phenotype = phenotype.lower().replace('hp:', '')
            phenotype = int(phenotype)
            phenotype_list.append(phenotype)
        except:
            continue
    return phenotype_list
