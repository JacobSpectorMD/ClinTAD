from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, FormView
from django.shortcuts import render, redirect
from user.forms import RegisterForm, LoginForm, TrackForm
from django.http import HttpResponse
from user.track_creator import create_track
from home.models import UT
import json


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = '/user/login/'


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'
    success_url = '/'

    def form_valid(self, form):
        request = self.request
        email = form.cleaned_data.get('email')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=email, password=raw_password)
        if user is not None:
            login(request, user)
            return redirect('/')
        return super(LoginView, self).form_invalid()


def tracks(request):
    return render(request, 'tracks.html', {'form': TrackForm,
                                           'tracks': json.dumps(request.user.track_manager.track_json())})


def new_track(request):
    return create_track(request)


def edit_track(request):
    ut_id = request.POST.get('ut_id')
    ut = UT.objects.get(user=request.user, id=int(ut_id))
    ut.edit(request)
    return HttpResponse('')


def delete_track(request):
    ut_id = request.POST.get('ut_id')
    ut = UT.objects.get(user=request.user, id=int(ut_id))
    ut.remove(request)
    return HttpResponse('')


def default_enhancers(request):
    active = request.POST.get('active')
    if active == 'true':
        request.user.track_manager.default_enhancers = True
    else:
        request.user.track_manager.default_enhancers = False
    request.user.track_manager.save()
    return HttpResponse('')


def default_cnvs(request):
    active = request.POST.get('active')
    if active == 'true':
        request.user.track_manager.default_cnvs = True
    else:
        request.user.track_manager.default_cnvs = False
    request.user.track_manager.save()
    return HttpResponse('')


def default_tads(request):
    active = request.POST.get('active')
    if active == 'true':
        request.user.track_manager.default_tads = True
    else:
        request.user.track_manager.default_tads = False
    other_tads = UT.objects.filter(user=request.user, track__track_type='TAD').all()
    for track in other_tads:
        track.active = False
        track.save()
    request.user.track_manager.save()
    return HttpResponse('')