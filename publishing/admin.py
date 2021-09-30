from baton.admin import (ChoicesDropdownFilter, DropdownFilter,
                         RelatedDropdownFilter)
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponseRedirect

from collection.models import Poem
from core.generalSupportRoutines import (isDemoUserAttemptingCCSA,
                                         scriptMessages, successMsg)
from core.reportSupportRoutines import generate_contentsList
from core.utilitySupportRoutines import pubsLastUpdated, updatePublishers

from .models import Content

import json

# =================  Content ========================================


class ContentAdmin(admin.ModelAdmin):
    list_display=('publication','poem')
    fields=('publication','poem')
    actions = [generate_contentsList]

    def get_form(self, request, obj=None, **kwargs):
        form = super(ContentAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['publication'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['poem'].widget.attrs['style'] = 'width: 50em;'
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "publication":
            kwargs["queryset"] = Publication.objects.filter(Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID))
        if db_field.name == "poem":
            qs = Poem.objects.filter(Q(poet=request.user) & ((Q(mu=False) & Q(nE2C=0) & Q(nS2M=0) & Q(niP=0)) | Q(mu=True)) & Q(wip=False))
            kwargs["queryset"] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def get_queryset(self, request):
        if request.user.is_superuser:
            return Content.objects.all()
        else:
            return Content.objects.filter(poem__in=Poem.objects.filter(poet=request.user))

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModel='content'
        if isDemoUserAttemptingCCSA(request, theModel,  'Save'): return
        thePublication=Publication.objects.get(id=obj.publication_id)
        thePoem=Poem.objects.get(id=obj.poem_id)
        theID=u'%s of %s' % (thePublication.name,thePoem.title)
        super().save_model(request, obj, form, change)
        successMsg(request, theModel, theID)
        return

admin.site.register(Content, ContentAdmin)

class ContentInline(admin.TabularInline):
    fields=('poem',)
    model = Content
    extra = 0

    class Media:
        css = {
            'all': ('css/custom_admin.css',)  # Include extra css
        }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "poem":
            kwargs["queryset"] = Poem.objects.filter(poet=request.user ).order_by('title')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# =================  Publication ========================================

from .models import Publication


class PublicationAdmin(admin.ModelAdmin):
    list_display=('name','type','publisher','publishedOn')
    fields=('name',('publisher','publishedOn','type','isbn'))
    inlines = (ContentInline,)
    list_per_page = settings.LIST_PER_PAGE
    actions = (generate_contentsList, )


    def get_form(self, request, obj=None, **kwargs):
        form = super(PublicationAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['name'].widget.attrs['style'] = 'width: 50em;'
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "publisher":
            kwargs["queryset"] = Publisher.objects.filter( Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Publication.objects.all()
        else:
            return Publication.objects.filter(( Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID)))

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModel='publication'
        if isDemoUserAttemptingCCSA(request, theModel, 'Save'): return
        theID=obj.name
        if not obj.pk:
            obj.poet_id = request.user.id
        super().save_model(request, obj, form, change)
        successMsg(request,theModel,theID)
        return

admin.site.register(Publication, PublicationAdmin)

class PublicationInline(admin.TabularInline):
    fields=('name',)
    model = Publication
    extra = 0

    class Media:
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }

    def get_form(self, request, obj=None, **kwargs):
        form = super(PublicationInline, self).get_form(request, obj, **kwargs)
        form.base_fields['name'].widget.attrs['style'] = 'width: 100em;'
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "name":
            kwargs["queryset"] = Publication.objects.filter(publisher__in=Publisher.objects.filter(poet=request.user)).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# =================  Publlisher ========================================

from .models import Publisher


class PublisherAdmin(admin.ModelAdmin):
    list_display=('name','country','access')
    fields=(('name','country'),'url')
    list_filter=(('country', ChoicesDropdownFilter),'access',)
    suit_list_filter_horizontal = ('country','access',)
    ordering=('name',)
    search_fields = ('name',)
    actions = [updatePublishers, pubsLastUpdated]
    inlines = (PublicationInline,)
    list_per_page = settings.LIST_PER_PAGE

    def get_form(self, request, obj=None, **kwargs):
        form = super(PublisherAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['name'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['url'].widget.attrs['style'] = 'width: 50em;'
        return form

    # set queryset to user's default country
    def changelist_view(self, request, extra_context=None):
        if not request.META['QUERY_STRING'] and \
                not request.META.get('HTTP_REFERER', '').startswith(request.build_absolute_uri()):
            return HttpResponseRedirect(request.path + "?country__exact="+request.session['Country_preference'])
        return super(PublisherAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        actions = super(PublisherAdmin, self).get_actions(request)
        if request.user.is_superuser:
            pass
        else:
            del actions['updatePublishers']
        return actions

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Publisher.objects.all()
        else:
            # public publishers are 'owned' by Admin - private ones by the user
            return Publisher.objects.filter( Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID) )

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModel='publisher'
        theID=obj.name
        if isNotDemoUser(request,theModel,theID):
            if not obj.pk: # new record
               obj.poet = request.user
               if not request.user.is_superuser:
                    obj.access = 'Private'
            else:
                if obj.poet != request.user:
                    msg= "Error: You can only change the publishers that you added!",
                    scriptMessages(request, msg)
                    return
            super().save_model(request, obj, form, change)
            successMsg(request, theModel, theID)
        return

    def delete_queryset(self,request,queryset):
        if not request.user.is_superuser:
            for q in queryset:
                if q.poet != request.user:
                    msg="Error: You can only delete the publishers that you added!"
                    scriptMessages(request, msg)
                    return
        return super().delete_model(request, queryset)

    def baton_cl_rows_attributes(self, request, cl):
        data = {}
        if request.session['highlight publishers'] == 0:
            pass
        else:
            print('====looking for publishers')
            rshp = request.session['highlight publishers']
            uid=request.session['User_id']
            # change the background colour of the publisher if
            # it has published content in a publication
            publishers=[]
            for cntnt in Content.objects.all():
                poem_id=cntnt.poem_id
                thePoem=Poem.objects.get(id=poem_id)
                if thePoem.poet_id==uid:
                    publication_id=cntnt.publication_id
                    thePublication=Publication.objects.get(id=publication_id)
                    thePublisher_id=thePublication.publisher_id
                    publishers.append(thePublisher_id)
            if len(publishers)!=0:
               publishers = list(dict.fromkeys(publishers))
               for pubs in publishers:
                   data[pubs] = {'class': 'table-info', }
        return json.dumps(data)


admin.site.register(Publisher, PublisherAdmin)



