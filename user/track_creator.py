from django.http import HttpResponse
from django.shortcuts import redirect
from home.models import Track, Element, Chromosome, UT
from user.forms import TrackForm


def create_track(request):
    user = request.user
    build = request.POST.get('build', None)
    label = request.POST.get('label', None)
    track_type = request.POST.get('trackType', None)

    print(track_type)
    details = request.POST.get('details', '')
    uploaded_file = request.FILES.get('file', None)
    if not build or not label or not track_type or not uploaded_file:
        return {}

    track = Track.objects.create(creator_id=user.id, build=build, label=label, track_type=track_type,
                                 details=details)
    try:
        track.subscribers.add(user)
        UT.objects.create(user=user, track=track)
        file_data = uploaded_file.read().decode("utf-8")
        lines = file_data.split("\n")
        element_list = []
        for line in lines:
            if "NUMBER" in line.upper() or "START" in line.upper():
                continue
            line = line.strip()
            col = line.split('\t')
            chromosome_num = col[0].replace('CHR', '').upper()
            chromosome = Chromosome.objects.get(number=chromosome_num)
            start = int(col[1].replace(',', ''))
            if col[2] != '':
                end = int(col[2].replace(',', ''))
            else:
                end = -1
            if len(col) >= 4:
                label = col[3]
            else:
                label = ''
            if len(col) >= 5:
                details = col[4]
            else:
                details = ''
            element_list.append(Element(track=track, chromosome=chromosome, start=start, end=end, label=label,
                                             details=details))
        Element.objects.bulk_create(element_list)
        return track.to_dict()
    except Exception as e:
        print(e)
        track.delete()
        return {}
    return {}
