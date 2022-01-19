import json
from urllib.parse import unquote

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from home.forms import *
from home.helper import parse_coordinates, parse_phenotypes
from home.clintad import get_single_data
from home.clintad import hpo_lookup
from home.models import SingleViewer
from home.statistics import get_100_variants, get_one_variant


def single(request):
    template_name = 'single.html'

    if 'show_feedback' not in request.session.keys():
        request.session['show_feedback'] = True
    show_feedback = request.session.get('show_feedback')

    if request.method == 'GET':
        coordinates = request.session.get('coordinates', 'null')
        phenotypes = request.session.get('phenotypes', '')
        return render(request, template_name, {'coordinates': coordinates, 'phenotypes': phenotypes, 'navbar': 'single',
                                               'show_feedback': show_feedback})


def submit_query(request):
    """
    Updates the coordinates and phenotypes using data posted by the user, then returns the gene/TAD data for their 
    request.

    Request Parameters
        coordinates: str
            Chromosome coordinates in UCSC format, e.g. "chr1:1000000-2000000"
        phenotypes: str
            A list of HPO IDs in integer and/or HPO ID format separated by commas, e.g. "HP:0410034, 717"
    """
    coordinates = request.POST.get('coordinates', None)
    if not coordinates:
        return JsonResponse({})
    request.session['coordinates'] = request.POST.get('coordinates', None)
    request.session['phenotypes'] = request.POST.get('phenotypes', '')
    request.session['zoom'] = 0
    return get_genes(request)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip


def get_genes(request):
    if request.session.get('coordinates', None):
        data = get_single_data(request)
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({}, safe=False)


def get_phenotypes(request):
    entered_string = unquote(request.META['QUERY_STRING'])
    hpo_list = hpo_lookup(entered_string)
    return JsonResponse(hpo_list, safe=False)


def hide_feedback(request):
    request.session['show_feedback'] = False
    return HttpResponse('', 200)


def statistics(request):
    coordinates = request.GET.get('coordinates', 'null')
    phenotypes = request.GET.get('phenotypes', '')
    return render(request, 'statistics.html', {'coordinates': coordinates, 'phenotypes': phenotypes})


def get_variant(request):
    coordinates = request.POST.get('coordinates', None)
    phenotypes = request.POST.get('phenotypes', '')
    response = get_one_variant(request, coordinates, phenotypes)
    return JsonResponse(response, safe=False)


def get_variants(request):
    coordinates = request.POST.get('coordinates', None)
    phenotypes = request.POST.get('phenotypes', '')
    response = get_100_variants(request, coordinates, phenotypes)
    return JsonResponse(response, safe=False)


def zoom(request):
    direction = request.POST.get('zoom', None)
    if not direction:
        return JsonResponse({})

    if direction == 'in':
        if request.session['zoom'] == 0:
            return JsonResponse({})
        request.session['zoom'] -= 1
    elif direction == 'out':
        request.session['zoom'] += 1

    return get_genes(request)
