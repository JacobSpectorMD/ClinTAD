import json
from axes.decorators import axes_dispatch

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse, JsonResponse
from django.views.generic import CreateView, FormView
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from home.models import UT
from .tokens import account_activation_token
from user.forms import RegisterForm, LoginForm, TrackForm
from user.models import Profile, TrackManager, User
from user.track_creator import create_track


@axes_dispatch
def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print(form)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=email, password=raw_password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('/user/tracks')
            else:
                messages.add_message(request, messages.INFO, "The login information you entered was invalid. "
                                     "After 5 unsuccessful login attempts your account will be locked for 1 hour.")
                return redirect('/user/login')


def logout_view(request):
    logout(request)
    return redirect('/')


def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            raw_password = form.cleaned_data['password1']
            user = User.objects.create_user(email=email, name=name, password=raw_password)

            Profile.objects.create(user=user)
            TrackManager.objects.create(user=user)

            domain = get_current_site(request).domain
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = account_activation_token.make_token(user)
            activation_link = "http://{domain}/user/activate/{uid}/{token}/".format(domain=domain, uid=uid, token=token)
            print(activation_link)
            msg = EmailMultiAlternatives(
                subject="Account Activation - ClinTAD",
                body="Please click on the following link to activate your account: \n" + activation_link,
                from_email="ClinTAD <clinicaltad@gmail.com>",
                to=[email],
                reply_to=["ClinTAD <clinicaltad@gmail.com>"])
            html = render_to_string('activation_email.html', {
                'activation_link': activation_link,
            })

            msg.attach_alternative(html, "text/html")
            msg.send()
            return redirect('/user/registration_sent/')
        else:
            return render(request, 'register.html', {'form': form})


def registration_sent(request):
    return render(request, 'registration_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    print(account_activation_token.check_token(user, token))
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='axes.backends.AxesBackend')
        return redirect('/')


def tracks(request):
    return render(request, 'tracks.html', {'form': TrackForm,
                                           'tracks': json.dumps(request.user.track_manager.track_json())})


def new_track(request):
    data = create_track(request)
    return JsonResponse(data)


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