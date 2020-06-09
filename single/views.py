import datetime
from datetime import timedelta
from urllib.parse import unquote

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from home.forms import *
from home.clintad import get_single_data
from home.clintad import hpo_lookup
from home.clintad import GetTADs
from home.models import SingleViewer
from home.statistics import get_100_variants, get_one_variant


class single(TemplateView):
    template_name = 'single.html'

    def get(self, request):
        for key, value in request.session.items():
            print('{} => {}'.format(key, value))
        initial = {}
        for var in ['chromosome', 'start', 'end', 'phenotypes']:
            if request.session.get(var, None):
                initial[var] = request.session[var]
        form = SingleForm(initial=initial)

        if 'show_feedback' not in request.session.keys():
            request.session['show_feedback'] = True
        show_feedback = request.session.get('show_feedback')

        two_weeks = timezone.now() + timedelta(weeks=2)
        request.session.set_expiry(two_weeks)
        return render(request, self.template_name, {'form': form, 'navbar': 'single', 'show_feedback': show_feedback})

    def post(self, request):
        if request.POST.get('action') == "Submit":
            request.session['zoom'] = 0

            ip_address = request.META['REMOTE_ADDR']
            viewer = SingleViewer.objects.filter(ip_address=ip_address).first()
            if not viewer:
                viewer = SingleViewer.objects.create(ip_address=ip_address)
            viewer.views += 1
            viewer.save()
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
    if request.session.get('chromosome', None) and request.session.get('start', None) and request.session.get('end', None):
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
    response = get_100_variants(request, chromosome, start, end, phenotypes)
    return JsonResponse(response, safe=False)
