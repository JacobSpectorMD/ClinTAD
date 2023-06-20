from django.http import HttpResponse
from django.shortcuts import redirect
from home.models import Build, Track, Element, Chromosome, UT
from user.forms import TrackForm


def create_track(request):
    user = request.user
    build = request.POST.get('build', None)
    label = request.POST.get('label', None)
    author_last_name = request.POST.get('author_last_name', '')
    pubmed_id = request.POST.get('pubmed_id', None)
    article_name = request.POST.get('article_name', '')
    track_type = request.POST.get('trackType', None)

    details = request.POST.get('details', '')
    uploaded_file = request.FILES.get('file', None)
    build = Build.objects.filter(name=build).first()
    if not build or not label or not track_type or not uploaded_file:
        return {
            'error': 'Please make sure you have filled in information for the build, track name, track type, '
                     'and uploaded a file.'
        }
    track = Track.objects.create(author_last_name=author_last_name, creator_id=user.id, build=build, label=label,
                                 creator=user, pubmed_id=pubmed_id, article_name=article_name, track_type=track_type,
                                 details=details)
    try:
        track.subscribers.add(user)
        UT.objects.create(user=user, track=track)
        file_data = uploaded_file.read().decode("utf-8")
        lines = file_data.split("\n")
        element_list = []
        for line in lines:
            line = line.strip()
            if not line or "NUMBER" in line.upper() or "START" in line.upper():
                continue
            col = line.split('\t')
            chromosome_num = col[0].upper().replace('CHR', '')
            chromosome = Chromosome.objects.get(build=build, number=chromosome_num)
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
            element_list.append(Element(build=build, track=track, chromosome=chromosome, start=start, end=end, label=label,
                                        details=details))
        Element.objects.bulk_create(element_list)
        return track.to_dict()
    except Exception as e:
        print(e)
        track.delete()
        return {'error': 'Something went wrong when creating your track'}
    return {'error': 'Something went wrong when creating your track'}
