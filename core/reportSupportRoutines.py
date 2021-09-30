from io import BytesIO

import xhtml2pdf.pisa as pisa
from cuser.middleware import CuserMiddleware
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template

from collection.models import Categorize, Poem, Link, Note
from core.generalSupportRoutines import (dateTimeNow, issueMessage,
                                         scriptMessages)
from entries.models import Entry
from publishing.models import Content
from readings.models import Reading
from submissions.models import Submission


def get_Logo(request):
    if request.session['logo choice'] == 0:
        logo = settings.LOGO
    elif request.session['logo choice'] == 1:
        logo = request.session['logo']
    else:
        logo = None
    return logo


def generateReport(theContext, templateName, reportName):
    template = get_template(u'reports/%s.html' % templateName)
    html = template.render(theContext)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
    if not pdf.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    else:
        return HttpResponse(u'Error Rendering PDF - attempting to generate a %s report' % reportName, status=400)


def generateCategorizedPoemsReport(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    theCatList = queryset.values_list('id', flat=True)
    pwc = Categorize.objects.filter(category__in=theCatList)
    logo = get_Logo(request)
    context = {
        'userName': userName,
        'dateTimeNow': dateTimeNow(),
        'pwc': pwc,
        'logo': logo,
    }
    return generateReport(context, 'categorizedPoemsList', 'categorized poems listing')


generateCategorizedPoemsReport.short_description = "Categorized Poems listing report"


def generateCategoriesReport(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    logo = get_Logo(request)
    catList = queryset
    context = {
        'userName': userName,
        'dateTimeNow': dateTimeNow(),
        'catList': catList,
        'logo': logo,
    }
    return generateReport(context, 'categoriesList', 'categoriesList')


generateCategoriesReport.short_description = "Categories listing report"


def generateNotesReport(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    logo = get_Logo(request)
    notesList = queryset
    context = {
        'userName': userName,
        'dateTimeNow': dateTimeNow(),
        'logo': logo,
        'notesList': notesList
    }
    return generateReport(context, 'notesList', 'notes listing')

generateNotesReport.short_description = "Notes listing report"


def generateADetailedPoemReport(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    html = ''
    first = True
    logo = get_Logo(request)
    for qs in queryset:
        theFirst = first
        notTheFirst = not first
        if first == True: first = False
        poem_id = qs.id
        poem = get_object_or_404(Poem, id=poem_id)
        theNotes = Note.objects.filter(poem_id=poem_id).order_by('-updated')
        theLinks = Link.objects.filter(poem_id=poem_id).order_by('-updated')
        theEntries = Entry.objects.filter(poem_id=poem_id).order_by('-enteredOn')
        theSubmissions = Submission.objects.filter(poem_id=poem_id).order_by('-submittedOn')
        theContents = Content.objects.filter(poem_id=poem_id).order_by('publication')
        theReadings = Reading.objects.filter(poem_id=poem_id).order_by('event')
        theCategories = Categorize.objects.filter(poem_id=poem_id).order_by('category')
        hasPorR = (poem.nR>0 or poem.niP>0)
        hasEnt =  (poem.nE2C>0 or poem.nEE2C>0)
        hasSub =  (poem.nS2M>0  or poem.nES2M>0)
        hasEntorSub = (hasEnt or hasSub)
        hasSum =  (hasPorR or hasEntorSub)
        context = {
            'userName': userName,
            'dateTimeNow': dateTimeNow(),
            'theFirst': theFirst,
            'notTheFirst': notTheFirst,
            'logo': logo,
            'poem': poem,
            'hasPorR': hasPorR,
            'hasEnt' : hasEnt,
            'hasSub' : hasSub,
            'hasEntorSub' : hasEntorSub,
            'hasSum' : hasSum,
            'theNotes': theNotes,
            'theLinks': theLinks,
            'theEntries': theEntries,
            'theSubmissions': theSubmissions,
            'thePublications': theContents,
            'theReadings': theReadings,
            'theCategories': theCategories,
            'staticRoot': settings.STATICFILES_DIR
        }
        template = get_template('reports/poemDetail.html')
        html += template.render(context)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
    if not pdf.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    else:
        return HttpResponse("Error Rendering PDF - attempting to generate a detail poem report", status=400)


generateADetailedPoemReport.short_description = "Detailed report"


def generate_poemList(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    logo = get_Logo(request)
    poemList = queryset
    context = {
        'userName':     userName,
        'dateTimeNow':  dateTimeNow(),
        'poemList':     poemList,
        'logo':         logo,
    }
    return generateReport(context, 'poemList', 'poem list')

generate_poemList.short_description = "Listing report"

def generate_LinksList(self,request,queryset):
    user = CuserMiddleware.get_user()
    userName=user.username
    linksList = queryset
    tl=[]
    for q in queryset:
        if q.tags is None:
            tl.append('')
        else:
            tl.append(u",  ".join(o.name for o in  q.tags.all()))
    logo = get_Logo(request)
    context = {
        'userName': userName,
        'dateTimeNow': dateTimeNow(),
        'linksList': linksList,
        'taglist' : tl,
        'logo': logo,
    }
    return generateReport(context, 'linksList', 'link list')

generate_LinksList.short_description = "Listing report"



def generate_entriesList(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    logo = get_Logo(request)
    entriesList = queryset
    context = {
        'userName': userName,
        'dateTimeNow': dateTimeNow(),
        'entriesList': entriesList,
        'logo': logo,
    }
    return generateReport(context, 'entriesList', 'entries list')

generate_entriesList.short_description = "Listing report"


def generate_submissionsList(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    logo = get_Logo(request)
    submissionsList = queryset
    context = {
        'userName': userName,
        'dateTimeNow': dateTimeNow(),
        'submissionsList': submissionsList,
        'logo': logo,
    }
    return generateReport(context, 'submissionsList', 'submissions to magazines list')

generate_submissionsList.short_description = "Listing report"


def generate_contentsList(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    logo = get_Logo(request)
    publicationsList = queryset
    publicationIds = publicationsList.values_list('id', flat=True)
    contentsList = Content.objects.filter(publication__in=publicationIds)
    context = {
        'userName': userName,
        'dateTimeNow': dateTimeNow(),
        'contentsList': contentsList,
        'logo': logo,
    }
    return generateReport(context, 'contentsList', 'contents for publications list')

generate_contentsList.short_description = "Listing report"


def generate_readingsList(self, request, queryset):
    user = CuserMiddleware.get_user()
    userName = user.username
    logo = get_Logo(request)
    readingsList = queryset
    context = {
        'userName': userName,
        'dateTimeNow': dateTimeNow(),
        'readingsList': readingsList,
        'logo': logo,
    }
    return generateReport(context, 'readingsList', 'readings for events list')

generate_readingsList.short_description = "Listing report"
