import io
import json
import os

from django.db.models import Q

from home.helper import parse_coordinates, parse_phenotypes
from home.models import Chromosome, Enhancer, Gene, TAD, Track, UT, Variant

module_dir = os.path.dirname(__file__)  # get current directory
hpo_path = os.path.join(module_dir, 'files/hpo_list.txt')


class TempGene:
    def __init__(self, name, start, end):
        self.autosomal_dominant = {}
        self.autosomal_recessive = {}
        self.end = end
        self.name = name
        self.matches = []
        self.phenotypes = []
        self.phenotype_score = 0
        self.start = start
        self.weighted_score = 0
        self.x_linked_dominant = {}
        self.x_linked_recessive = {}

    def to_dict(self):
        return {'autosomal_recessive': self.autosomal_recessive, 'autosomal_dominant': self.autosomal_dominant,
                'name': self.name, 'start': self.start, 'end': self.end, 'phenotypes': self.phenotypes,
                'phenotype_score': self.phenotype_score, 'matches': self.matches,
                'weighted_score': self.weighted_score, 'x_linked_recessive': self.x_linked_recessive,
                'x_linked_dominant': self.x_linked_dominant}


def get_single_data(request):
    chromosome, start, end = parse_coordinates(request.session['coordinates'])
    phenotypes = parse_phenotypes(request.session['phenotypes'])

    data_str = GetTADs(request, '', chromosome, start, end, phenotypes, request.session['zoom'])
    data = json.loads(data_str)

    data['tracks'] = []
    if request.user.is_authenticated:
        active_tracks = [ut for ut in UT.objects.filter(user=request.user, active=True)
                                        .exclude(track__track_type='TAD')]
        for track in active_tracks:
            data['tracks'].append(get_track_data(track, request.session['chromosome'], data['minimum']['coord'],
                                                 data['maximum']['coord']))
        data['default_enhancers'] = request.user.track_manager.default_enhancers
        data['default_tads'] = request.user.track_manager.default_tads
        data['default_cnvs'] = request.user.track_manager.default_cnvs
    else:
        data['default_enhancers'] = True
        data['default_tads'] = True
        data['default_cnvs'] = True

    return json.dumps(data)


def get_track_data(ut, chromosome_number, minimum_coordinate, maximum_coordinate):
    chromosome = Chromosome.objects.get(number=chromosome_number)
    elements = ut.track.elements.filter(Q(start__range=(minimum_coordinate, maximum_coordinate)) |
                                        Q(end__range=(minimum_coordinate, maximum_coordinate)))\
                                .filter(chromosome=chromosome).all()
    element_list = [element.to_dict() for element in elements]
    return {'label': ut.track.label, 'color': ut.color, 'elements': element_list}


def GetTADs(request, case_id, chromosome_input, CNV_start, CNV_end, phenotypes, zoom, source_function='single'):
    chromosome_input = chromosome_input.upper().strip().replace("CHR", "")
    chromosome = Chromosome.objects.filter(number=chromosome_input).first()
    chromosome_length = chromosome.length
    patient_CNV_start = int(CNV_start.replace(',', ''))
    patient_CNV_end = int(CNV_end.replace(',', ''))

    # If the user zooms -> increase search distance
    if zoom > 0:
        search_distance = 1000000 * (2 ** zoom)
        search_start = patient_CNV_start - search_distance
        search_end = patient_CNV_end + search_distance
        if search_start < 0:
            search_start = 0
        if search_end > chromosome_length:
            search_end = chromosome_length
    else:
        search_start = patient_CNV_start
        search_end = patient_CNV_end

    # Finds the nearest left and right TAD boundary
    custom_tad_track = None
    if request.user.is_authenticated:
        custom_tad_track = request.user.get_tad_track()
    if custom_tad_track:
        left_tad = custom_tad_track.track.elements.filter(start__lte=search_start, chromosome=chromosome)\
            .order_by('start').last()
        right_tad = custom_tad_track.track.elements.filter(end__gte=search_end, chromosome=chromosome)\
            .order_by('end').first()
    else:
        left_tad = TAD.objects.filter(start__lte=search_start, chromosome=chromosome).order_by('start').last()
        right_tad = TAD.objects.filter(end__gte=search_end, chromosome=chromosome).order_by('end').first()

    # If the CNV start/end is less than/greater than the TAD boundaries, use the start/end of the chromosome
    if left_tad is None:
            minimum_coordinate = 0
            min_type = "chromosome"
    else:
        minimum_coordinate = left_tad.start
        min_type = "boundary"

    if right_tad is None:
        maximum_coordinate = chromosome_length
        max_type = "chromosome"
    else:
        maximum_coordinate = right_tad.end
        max_type = "boundary"

    # Process phenotype input
    phenotype_list = []
    for phenotype in phenotypes:
        phenotype_list.append(phenotype)

    # Get enhancers
    enhancers = Enhancer.objects.filter(Q(start__range=(minimum_coordinate, maximum_coordinate)) |
                                Q(end__range=(minimum_coordinate, maximum_coordinate))).filter(chromosome=chromosome).all()
    enhancer_list = [enhancer.to_dict() for enhancer in enhancers]

    # Get benign variants
    variants = Variant.objects.filter(Q(outer_start__range=(minimum_coordinate, maximum_coordinate)) |
                                      Q(outer_end__range=(minimum_coordinate, maximum_coordinate)) |
                                      Q(outer_start__lte=minimum_coordinate, outer_end__gte=maximum_coordinate))\
                              .filter(chromosome=chromosome).order_by('outer_start').all()
    variant_list = [variant.to_dict() for variant in variants]

    # Get all genes that are within the search area
    genes = Gene.objects.filter(Q(start__range=(minimum_coordinate, maximum_coordinate)) |
                                Q(end__range=(minimum_coordinate, maximum_coordinate)) |
                                Q(start__lte=minimum_coordinate, end__gte=maximum_coordinate))\
                        .filter(chromosome=chromosome).all()

    if custom_tad_track:
        tads = custom_tad_track.track.elements.filter(chromosome=chromosome).filter(start__gte=minimum_coordinate)\
            .filter(end__lte=maximum_coordinate).all()
    else:
        tads = TAD.objects.filter(chromosome=chromosome).filter(start__gte=minimum_coordinate)\
                  .filter(end__lte=maximum_coordinate).all()

    # For every gene in the area, determine if there are HPO matches
    gene_list = []
    hpo_matches = 0
    for gene in genes:
        new_gene = TempGene(name=gene.name, start=gene.start, end=gene.end)
        hpos = gene.hpos.all()
        for hpo in hpos:
            new_gene.phenotypes.append({'hpo': hpo.hpoid, 'name': hpo.name})
            if hpo.hpoid in phenotype_list:
                new_gene.matches.append({'hpo': hpo.hpoid, 'name': hpo.name})
                new_gene.phenotype_score += 1
                new_gene.weighted_score += hpo.weight
                hpo_matches += 1

                # Only get OMIM and inheritance data for multiple
                if source_function == 'multiple':
                    for omim in hpo.omims.filter(genes=gene).all():
                        if omim.autosomal_recessive:
                            new_gene.autosomal_recessive[str(omim.omim_number)] = True
                        if omim.autosomal_dominant:
                            new_gene.autosomal_dominant[str(omim.omim_number)] = True
                        if omim.x_linked_recessive:
                            new_gene.x_linked_recessive[str(omim.omim_number)] = True
                        if omim.x_linked_dominant:
                            new_gene.x_linked_dominant[str(omim.omim_number)] = True
        gene_list.append(new_gene.to_dict())

    gene_matches = 0
    total_weighted_score = 0
    for gene in gene_list:
        if gene['phenotype_score'] > 0:
            gene_matches += 1
            total_weighted_score += gene['weighted_score']

    gene_dict = {
        'case_id': case_id,
        'chromosome': chromosome.number,
        'cnv_start': patient_CNV_start,
        'cnv_end': patient_CNV_end,
        'enhancers': enhancer_list,
        'gene_matches': gene_matches,
        'genes': gene_list,
        'hpo_matches': hpo_matches,
        'minimum': {'coord': minimum_coordinate, 'type': min_type},
        'maximum': {'coord': maximum_coordinate, 'type': max_type},
        'phenotypes': ', '.join([str(phenotype) for phenotype in phenotype_list]),
        'tads': [tad.to_dict() for tad in tads],
        'variants': variant_list,
        'weighted_score': total_weighted_score
    }
    return json.dumps(gene_dict)


def hpo_lookup(entered_string):
    class phenotype_class():
        def __init__(self, d):
            self.__dict__ = d

    HPOs_to_return = []
    array_to_return =[]
    with io.open(hpo_path, 'r', encoding='utf-8-sig') as f:
        list_of_hpo = json.load(f, encoding="ANSI")
    f.close()

    words = entered_string.split()
    for i in range(len(list_of_hpo)):
        current_phenotype = phenotype_class(list_of_hpo[i])
        score = 0
        for word in words:
            if word.upper() in str(current_phenotype.__dict__).upper():
                score += 1
        current_phenotype.score = score
        if score >= len(words):
            HPOs_to_return.append(current_phenotype)

    HPOs_to_return.sort(key = lambda x: x.score, reverse=True)
    for HPO in HPOs_to_return:
        array_to_return.append(HPO.id)

    # If the match is in the description or comment and not the HPO name/title, move it to the bottom
    for i in range(len(array_to_return)):
        in_title = False
        for word in words:
            if word.upper() in array_to_return[i].upper():
                in_title = True
        if not in_title:
            j = i
            while j < len(array_to_return)-1:
                j+=1
                for word in words:
                    if word.upper() in array_to_return[j].upper():
                        array_to_return[i], array_to_return[j] = array_to_return[j], array_to_return[i]
                        break
            
    return (array_to_return)
