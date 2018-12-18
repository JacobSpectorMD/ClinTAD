from django.http import HttpResponse
from django.shortcuts import redirect
from home.models import Track, Element, Chromosome, UT
from user.forms import TrackForm


def create_track(request):
    user = request.user
    form = TrackForm(request.POST, request.FILES)
    if form.is_valid():
        build = form.cleaned_data['build']
        label = form.cleaned_data['label']
        track_type = form.cleaned_data['track_type']
        details = form.cleaned_data['details']
        uploaded_file = form.cleaned_data['uploaded_file']

        track = Track.objects.create(creator_id=user.id, build=build, label=label, track_type=track_type,
                                     details=details)
        track.subscribers.add(user)
        UT.objects.create(user=user, track=track)
        file_data = uploaded_file.read().decode("utf-8")
        lines = file_data.split("\n")
        for line in lines:
            line = line.strip()
            col = line.split('\t')
            chromosome = Chromosome.objects.get(number=col[0].upper())
            start = int(col[1])
            if col[2] != '':
                end = int(col[2])
            else:
                end = -1
            element = Element.objects.create(track=track, chromosome=chromosome, start=start, end=end)
    return redirect('/user/tracks/')
