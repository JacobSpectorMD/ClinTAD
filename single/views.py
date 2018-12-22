from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from home.forms import *
from home.clintad import hpo_lookup
from urllib.parse import unquote
from home.clintad import GetTADs
from home.statistics import get_500_variants, get_one_variant
from home.clintad import get_single_data


class single(TemplateView):
    template_name = 'single.html'

    def get(self, request):
        initial = {}
        for var in ['chromosome', 'start', 'end', 'phenotypes']:
            if request.session.get(var, None):
                initial[var] = request.session[var]
        form = SingleForm(initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.POST.get('action') == "Submit":
            request.session['zoom'] = 0
        elif request.POST.get('action') == "out":
            try:
                request.session['zoom'] += 1
            except:
                request.session['zoom'] = 0
        elif request.POST.get('action') == "in":
            try:
                request.session['zoom'] -= 1
            except:
                request.session['zoom'] = 0
        if request.session['zoom'] < 0:
            request.session['zoom'] = 0

        form = SingleForm(request.POST)

        if form.is_valid():
            if form.cleaned_data['chromosome'] != "":
                request.session['chromosome'] = form.cleaned_data['chromosome']
                request.session['phenotypes'] = form.cleaned_data['phenotypes']
            if form.cleaned_data['start'] != "":
                request.session['start'] = form.cleaned_data['start']
            if form.cleaned_data['end'] != "":
                request.session['end'] = form.cleaned_data['end']

        form = SingleForm(request.POST)
        args = {'form': form, 'navbar': 'single'}
        return render(request, self.template_name, args)


def get_genes(request):
    data = get_single_data(request)
    return JsonResponse(data, safe=False)


def get_phenotypes(request):
    entered_string = unquote(request.META['QUERY_STRING'])
    hpo_list = hpo_lookup(entered_string)
    return JsonResponse(hpo_list, safe=False)


def statistics(request):
    chromosome = request.GET.get('chr')
    start = request.GET.get('start')
    end = request.GET.get('end')
    phenotypes = request.GET.get('phenotypes')
    form = SingleForm(initial={'chromosome': chromosome, 'start': start, 'end': end, 'phenotypes': phenotypes})
    return render(request, 'statistics.html', {'chromosome': chromosome, 'start': start, 'end': end,
                                               'phenotypes': phenotypes, 'form': form})


def get_variant(request):
    chromosome = request.POST.get('chromosome')
    start = request.POST.get('start')
    end = request.POST.get('end')
    phenotypes = request.POST.get('phenotypes')
    response = get_one_variant(request, chromosome, start, end, phenotypes)
    return JsonResponse(response, safe=False)


def get_variants(request):
    chromosome = request.POST.get('chromosome')
    start = request.POST.get('start')
    end = request.POST.get('end')
    phenotypes = request.POST.get('phenotypes')
    response = get_500_variants(request, chromosome, start, end, phenotypes)
    return JsonResponse(response, safe=False)
