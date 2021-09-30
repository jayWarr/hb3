import os

from django.conf import settings


def get_notes_filepath(filename, request):
    notesSubDir=os.path.join(settings.MEDIA_ROOT,'_notes')
    return os.path.join(notesSubDir,'poet_{}'.format(request.session['User_id']))
