from urllib.parse import unquote

from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db import transaction

from home.forms import *
from home.clintad import GetTADs, hpo_lookup
from home.models import Case
from home.statistics_old import GetStatistics
from home.clintad_multiple import process_multiple_patients


def cases(request):
    cases = [case.to_dict() for case in Case.objects.all()]
    return render(request, 'cases.html', {'cases': cases})


# Views for the pages home, single, multiple, about and contact
def home(request):
    return redirect('/single')
    # template_name = 'home.html'
    #
    # def get(self, request):
    #     return render(request, self.template_name, {'navbar': 'home'})


class demonstration(TemplateView):
    template_name = 'single.html'

    def get(self, request):
        request.session['zoom'] = 0
        request.session['chromosome'] = "6"
        request.session['start'] = "33202640"
        request.session['end'] = "33429672"
        request.session['phenotypes'] = "HP:0001263, HP:0011342, HP:0011343, HP:0000823, HP:0100702, " \
                                    "HP:0000718, HP:0000717, HP:0000729, HP:0002315, HP:0002076, HP:0000735," \
                                    "HP:0025161, HP:0025160, HP:0002232, HP:0001596, HP:0001595, HP:0002209," \
                                    "HP:0002231, HP:0000771, HP:0008202"
        genes = GetTADs(request, '', request.session['chromosome'], request.session['start'], request.session['end'],
                        request.session['phenotypes'], request.session['zoom'])
        request.session['genes'] = genes

        form = SingleForm(initial={"chromosome": "6", "start":"33202640", "end": "33429672", "phenotypes":"HP:0001263,"
                                   "HP:0011342, HP:0011343, HP:0000823, HP:0100702, HP:0000718, HP:0000717, "
                                   "HP:0000729, HP:0002315, HP:0002076, HP:0000735, HP:0025161, HP:0025160, "
                                   "HP:0002232, HP:0001596, HP:0001595, HP:0002209, HP:0002231, HP:0000771, "
                                   "HP:0008202"})
        return render(request, self.template_name, {'form': form, 'navbar': 'single'})

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
                if request.session['zoom'] > 0:
                    request.session['zoom'] -= 1
            except:
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
            genes = GetTADs(request, '', request.session['chromosome'], request.session['start'], request.session['end'],
                            request.session['phenotypes'], request.session['zoom'])
            request.session['genes'] = genes

        return render(request, self.template_name, {'form': form, 'navbar': 'single'})


class multiple(TemplateView):
    template_name = 'multiple.html'

    def get(self, request):
        multiple_input = MultiLineForm()
        return render(request, self.template_name, {'navbar': 'multiple', 'multiple_form': multiple_input})

    def post(self, request):
        multiple_form = MultiLineForm(request.POST)
        if multiple_form.is_valid():
            multiple_text = multiple_form.cleaned_data['multiple']
        multiple_patients_results = process_multiple_patients(request, multiple_text)
        response = HttpResponse(multiple_patients_results)
        response['Content-Disposition'] = 'attachment; filename="results.txt"'
        return response


def multiple_submit(request):
    clintad_data = process_multiple_patients(request)
    return JsonResponse({'status': 'success', 'clintad_data': clintad_data})


class about(TemplateView):
    template_name = 'about.html'

    def get(self, request):
        return render(request, self.template_name, {'navbar': 'about'})


class data(TemplateView):
    template_name = 'data.html'

    def get(self, request):
        return render(request, self.template_name, {'navbar': 'data'})


class contact(TemplateView):
    template_name = 'contact.html'

    def get(self, request):
        return render(request, self.template_name, {'navbar': 'contact'})


def get_genes(request):
    genes = request.session['genes']
    return JsonResponse(genes, safe=False)


def get_phenotypes(request):
    entered_string = unquote(request.META['QUERY_STRING'])
    hpo_list = hpo_lookup(entered_string)
    return JsonResponse(hpo_list, safe=False);


def clear_data(request):
    if 'genes' in request.session:
        del request.session['genes']
    return JsonResponse({'status': 'Success'}, safe=False);


def statistics(request):
    form = SingleForm(request.POST)

    if form.is_valid():
        chromosome_text = form.cleaned_data['chromosome']
        start_text = form.cleaned_data['start']
        end_text = form.cleaned_data['end']
        phenotypes_text = form.cleaned_data['phenotypes']
        results = GetStatistics(request, chromosome_text, start_text, end_text, phenotypes_text, request.session['zoom'])
        response = HttpResponse(results)
        response['Content-Disposition'] = 'attachment; filename="results.txt"'
        return response


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def set_announcement(request):
    request.session['announcement'] = False
    return JsonResponse({})


@login_required(login_url='/login/')
@transaction.atomic
def update_profile(request):

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return render(request, 'profile.html', {'user_form': user_form,
                            'profile_form': profile_form})
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form})