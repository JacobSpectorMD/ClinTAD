import json
from axes.decorators import axes_dispatch

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.generic import CreateView, FormView
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from home.models import Track, UT
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
            default_tracks = Track.objects.filter(default=True)
            for track in default_tracks:
                UT.objects.create(active=True, track=track, user=user)

            domain = get_current_site(request).domain
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = account_activation_token.make_token(user)
            activation_link = "http://{domain}/user/activate/{uid}/{token}/".format(domain=domain, uid=uid, token=token)

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
    public_tracks = [track.to_dict() for track in Track.objects.filter(public=True)]
    return render(request, 'tracks.html', {'form': TrackForm,
                                           'public_tracks': json.dumps(public_tracks),
                                           'tracks': json.dumps(request.user.track_manager.track_json())})


def new_track(request):
    data = create_track(request)
    status = 200
    if 'error' in data.keys():
        status = 500
    return JsonResponse(data, status=status)


def edit_track(request):
    ut_id = request.POST.get('ut_id')
    ut = UT.objects.get(user=request.user, id=int(ut_id))
    ut.edit(request)
    return HttpResponse('')


def delete_track(request):
    user_track_id = request.GET.get('userTrackId', None)
    if not user_track_id:
        return HttpResponse('')

    ut = UT.objects.get(user=request.user, id=int(user_track_id))
    if request.user != ut.user:  # Only allow users to delete their own tracks
        return HttpResponse('')

    ut.remove(request)
    return HttpResponse('')


def add_track(request):
    track_id = request.POST.get('id')
    track = Track.objects.get(id=track_id)
    user_track = UT.objects.filter(track=track, user=request.user).first()
    if not user_track:
        user_track = UT.objects.create(track=track, user=request.user)
    return JsonResponse(user_track.to_dict())


def update_user_track(request):
    user_track_id = request.POST.get('user_track_id')
    active = json.loads(request.POST.get('active'))

    user_track = UT.objects.get(id=user_track_id)
    if request.user != user_track.user:
        return

    if active:
        user_track.active = True
    elif not active:
        user_track.active = False

    # Make tracks of different builds inactive if the track is a TAD track.
    # Allow only one TAD track to be active at a time
    if user_track.track.track_type == 'tad' and active:
        other_build_tracks = UT.objects.filter(user=request.user, active=True).exclude(
            track__build=user_track.track.build)
        other_build_tracks.update(active=False)
        other_tad_tracks = UT.objects.filter(user=request.user, track__track_type='tad').exclude(
            id=user_track_id)
        other_tad_tracks.update(active=False)
    user_track.save()

    return JsonResponse(user_track.to_dict())
