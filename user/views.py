import json
from axes.decorators import axes_dispatch

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse
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
        return super(LoginView, self).form_invalid(form)


@axes_dispatch
def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
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
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            raw_password = form.cleaned_data['password1']
            user = User.objects.create_user(name=name, email=email, password=raw_password)

            Profile.objects.create(user=user)
            TrackManager.objects.create(user=user)
            token = default_token_generator.make_token(user)
            user.token = token
            user.save()
            mail_subject = 'Activate your ClinTAD account'
            current_site = get_current_site(request)
            message = render_to_string('activation_email.html',
                                       {'user': user, 'domain': current_site.domain,
                                        'uid': urlsafe_base64_encode(force_bytes(user.id)).decode(),
                                        'token': token})
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()
            messages.add_message(request, messages.INFO, 'An email has been sent to your email address. Please click on'
                                                         ' the link to activate your account.')
        return redirect('/user/login')


# def reset_password(request):
#     if request.method == 'GET':
#         form = PasswordResetForm()
#         return render(request, 'register.html', {'form': form})
#     if request.method == 'POST':
#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             user = User.objects.get(email=email)
#             token = default_token_generator.make_token(user)
#             user.token = token
#             user.save()
#             mail_subject = 'Reset your ClinTAD password'
#             current_site = get_current_site(request)
#             message = render_to_string('activation_email.html',
#                                        {'user': user, 'domain': current_site.domain,
#                                         'uid': urlsafe_base64_encode(force_bytes(user.id)).decode(),
#                                         'token': token})
#             email = EmailMessage(mail_subject, message, to=[user.email])
#             email.send()


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and user.token == token:
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/')

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