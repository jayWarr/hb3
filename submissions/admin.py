import json

from baton.admin import (ChoicesDropdownFilter, DropdownFilter,
                         RelatedDropdownFilter)
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponseRedirect

from collection.models import Poem
from core.generalSupportRoutines import (isDemoUserAttemptingCCSA, pluralize,
                                         scriptMessages, successMsg)
from core.poemSupportRoutines import withdrawSubmissions
from core.reportSupportRoutines import generate_submissionsList
from core.utilitySupportRoutines import magsLastUpdated, updateMagazines

from .models import Submission

# =================  Submission ==============================================


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('magazine','poem','submittedOn','committedUntil','status','inEdition','expiredOn')
    fields=('magazine','poem',('submittedOn','committedUntil','status','inEdition','expiredOn'))
    date_hierarchy = ('committedUntil')
    search_fields = ('magazine',)
    list_filter = (('poem', admin.RelatedOnlyFieldListFilter),)
    suit_list_filter_horizontal =('poem',)
    actions = [withdrawSubmissions, generate_submissionsList]

    def get_form(self, request, obj=None, **kwargs):
        form = super(SubmissionAdmin, self).get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['magazine'].widget.attrs['style'] = 'width: 32em;'
            form.base_fields['poem'].widget.attrs['style'] = 'width: 32em;'
        return form

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Submission.objects.all()
        else:
            return Submission.objects.filter(poet=request.user)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # This is the case when obj is already created i.e. it's a change/edit
            return ['magazine', 'poem','expiredOn']
        else:
            return ['expiredOn']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "poem":
            qs = Poem.objects.filter(Q(poet=request.user) & ((Q(mu=False) & Q(nE2C=0) & Q(nS2M=0) & Q(niP=0)) | Q(mu=True)) & Q(wip=False))
            kwargs["queryset"] = qs
            if db_field.name == "magazine":
                kwargs["queryset"]=Magazine.objects.filter( Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID) )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModel='submission'
        if isDemoUserAttemptingCCSA(request, theModel, 'Save'): return
        theMagazine=Magazine.objects.get(id=obj.magazine_id)
        thePoem=Poem.objects.get(id=obj.poem_id)
        theID=u'%s to %s' % (thePoem.title,theMagazine.name)
        super().save_model(request, obj, form, change)
        successMsg(request, theModel, theID)
        return

admin.site.register(Submission, SubmissionAdmin)

class submissionInLine(admin.TabularInline):
    fields=('poem','submittedOn','committedUntil','status','inEdition','expiredOn')
    readonly_fields = ('poem', 'submittedOn', 'committedUntil', 'status', 'inEdition', 'expiredOn')
    model = Submission
    extra=0
    suit_classes = 'suit-tab suit-tab-submissions'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Submission.objects.all()
        else:
            return Submission.objects.filter(poet=request.user)



# =================  Magazine ========================================

from .models import Magazine


class MagazineAdmin(admin.ModelAdmin):
    list_display=('name','country','access')
    list_filter=(('country',ChoicesDropdownFilter),'access',)
    suit_list_filter_horizontal = ('country','access',)
    search_fields = ('name',)
    ordering=('name',)
    readonly_fields = ('noOfSubmissions',)
    inlines = (submissionInLine,)
    actions=[updateMagazines,magsLastUpdated]
    list_per_page = settings.LIST_PER_PAGE

    fieldsets = [
        (None, {
            'classes': ('suit-tab',  'suit-tab-submissions'),
            'fields': [('name','country'),('url','noOfSubmissions')],
        }),
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(MagazineAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['name'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['url'].widget.attrs['style'] = 'width: 50em;'
        return form

    # set queryset to user's default country
    def changelist_view(self, request, extra_context=None):
        if not request.META['QUERY_STRING'] and \
                not request.META.get('HTTP_REFERER', '').startswith(request.build_absolute_uri()):
            return HttpResponseRedirect(request.path + "?country__exact="+request.session['Country_preference'])
        return super(MagazineAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        actions = super(MagazineAdmin, self).get_actions(request)
        if request.user.is_superuser:
            pass
        else:
            del actions['updateMagazines']
        return actions

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Magazine.objects.all()
        else:
            # public publishers are 'owned' by Admin - private ones by the user
            return Magazine.objects.filter( Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID) )

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModel='magazine'
        if isDemoUserAttemptingCCSA(request, theModel, 'Save'): return
        theID=obj.name
        if not obj.pk: # new record
           obj.poet = request.user
           if not request.user.is_superuser:
                obj.access='Private'
        else:
            if obj.poet != request.user:
                scriptMessages(request, "Error: You can only change the magaziness that you added !")
                return
        super().save_model(request, obj, form, change)
        successMsg(request,theModel,theID)
        return

    def delete_model(self, request, obj):
        if isDemoUserAttemptingCCSA(request, "Magazine", 'Delete'): return
        if self.poet != request.user:
            msg = "Error: You can only delete the magazines that you added!"
            scriptMessages(request, msg)
            return
        else:
            return super().delete_model(self, request, obj)


    def delete_queryset(self,request,queryset):
        if isDemoUserAttemptingCCSA(request, "Magazine", 'Delete'): return
        nq = queryset.count()
        if not request.user.is_superuser:
            for q in queryset:
                if q.poet != request.user:
                    scriptMessages(request, "Error: You can only delete the magazines that you added!")
                    return
        super().delete_model(request, queryset)
        scriptMessages(request, u"Info: %s magazine%s deleted." % (nq, pluralize(nq)))
        return

    def baton_cl_rows_attributes(self, request, cl):
        # change the background colour of the magazine if it has/had submissions
        data = {}
        if request.session['highlight submissions']==0:
            pass
        else:
            rshs=request.session['highlight submissions']
            for subs in Submission.objects.filter(poet=request.user) :
                if subs.expiredOn==None:
                    if rshs==1 or rshs==3:
                        data[subs.magazine_id] = {'class': 'table-info',}
                else:
                    if rshs == 2 or rshs == 3:
                        data[subs.magazine_id] = {'class': 'table-secondary', }
        return json.dumps(data)

admin.site.register(Magazine, MagazineAdmin)

