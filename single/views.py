import numpy as np
import pickle
from sklearn.ensemble import GradientBoostingClassifier
from urllib.parse import unquote

from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from home.clintad import get_single_data
from home.clintad import hpo_lookup
from home.statistics import get_100_variants, get_one_variant
from home.models import Build, Case


@requires_csrf_token
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


@requires_csrf_token
def example(request):
    template_name = 'single.html'

    if request.method == 'GET':
        build = request.GET.get('build', None)
        coordinates = request.GET.get('coordinates', None)
        phenotypes = request.GET.get('phenotypes', '')

        if not build or not coordinates:
            return redirect('/single/')

        return render(request, template_name, {
            'build': build, 'coordinates': coordinates, 'phenotypes': phenotypes, 'navbar': 'single'
        })


def submit_case(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to submit a case.'}, status=500)

    if request.method == 'POST':
        try:
            build_name = request.POST.get('build')
            comments = request.POST.get('comments')
            coordinates = request.POST.get('coordinates')
            evidence = request.POST.get('evidence')
            phenotypes = request.POST.get('phenotypes')
            pubmed_ids = request.POST.get('pubmeds')
            build = Build.objects.get(name=build_name)
            case = Case.objects.create(build=build, comments=comments, coordinates=coordinates, evidence=evidence,
                                       phenotypes_text=phenotypes, pubmed_ids=pubmed_ids, submitter=request.user,
                                       submitter_name=request.user.name, submitter_email=request.user.email)
            return JsonResponse(case.to_dict())
        except:
            return JsonResponse({'error': 'Something went wrong when processing your case. Please correct any errors '
                                          'and try again.'}, status=500)


def submitted_case(request):
    return render(request, 'submitted_case.html')


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
    coordinates = request.GET.get('coordinates', None)
    if not coordinates:
        return JsonResponse({})
    request.session['coordinates'] = request.GET.get('coordinates', None)
    request.session['phenotypes'] = request.GET.get('phenotypes', '')
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


def ml_prediction(request):
    coordinates = request.GET.get('coordinates', 'null')
    phenotypes = request.GET.get('phenotypes', '')
    return render(request, 'ml_prediction.html', {'coordinates': coordinates, 'phenotypes': phenotypes})


def predict(request):
    coordinates = request.GET.get('coordinates', 'null')
    phenotypes = request.GET.get('phenotypes', '')
    with open('single/cnv_model.sav', 'rb') as model_file:
        model = pickle.load(model_file)
    new_array = np.zeros(20)
    new_array[0] = 500000
    # print(new_array)
    # print(model.predict([new_array]), model.predict_proba([new_array]))
    prediction = model.predict([new_array])
    if prediction[0] == 1:
        pathogenicity = 'Pathogenic'
    else:
        pathogenicity = 'Not Pathogenic'
    print(prediction[0])
    return JsonResponse({'pathogenicity': pathogenicity})


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
