
from cuser.middleware import CuserMiddleware
from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import JsonResponse

from collection.models import Poem

# search prefix
POEM_POET='±'
WIKI='§'

#=================ADMIN_SEARCH================
@staff_member_required
def admin_search(request):

    text = request.GET.get('text', None)
    searchFor = text[1:]
    res = []
    if text[0]==POEM_POET:                                        # search for poet or poem
        if request.session['Country_preference'] == 'GBR':
            res.append({
                'label': searchFor,
                'url': 'https://www.poetryfoundation.org/search?query='+ searchFor.replace(' ','+') ,
                'icon': 'fa fa-book-reader',
            })
        elif request.session['Country_preference'] == 'USA':
            res.append({
                'label': searchFor,
                'url': 'https://poets.org/search?combine='+ searchFor.replace(' ','%20') ,
                'icon': 'fa fa-book-reader',
            })
        else:
            pass
    elif text[0]==WIKI:                                      # wiki search
        res.append({
            'label': searchFor,
            'url': 'https://en.wikipedia.org/wiki/' + searchFor.replace(' ', '_'),
            'icon': 'fab fa-wikipedia-w',
        })
    else:                                                   # search local poems
        poems = Poem.objects.filter(poet=CuserMiddleware.get_user(), title__icontains=text)
        for p in poems:
            res.append({
                'label': p.title,
                'url': '/admin/collection/poem/%d/change/' % p.id,
                'icon': 'fa fa-edit',
            })
    return JsonResponse({
        'length': len(res),
        'data': res
    })
