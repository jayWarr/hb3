import json
from datetime import datetime, timedelta, timezone

from baton.admin import (ChoicesDropdownFilter, DropdownFilter, InputFilter,
                         RelatedDropdownFilter)
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponseRedirect

from collection.models import Poem
from core.generalSupportRoutines import (isDemoUserAttemptingCCSA,
                                         scriptMessages, successMsg)
from core.poemSupportRoutines import withdrawEntries
from core.reportSupportRoutines import generate_entriesList
from core.utilitySupportRoutines import (compsLastUpdated,
                                         theAlert4CompsClosing,
                                         updateAllCompetitions)

from .models import Entry

# =================  ENTRY ==============================================


class EntryAdmin(admin.ModelAdmin):
    list_display = ('competition','poem','enteredOn','committedUntil','place','expiredOn')
    fields=('competition','poem',('enteredOn','committedUntil','place','expiredOn'))
    date_hierarchy =  ('committedUntil')
    search_fields = ('competition',)
    list_filter = (('poem', admin.RelatedOnlyFieldListFilter),)
    suit_list_filter_horizontal =('poem',)
    actions= [withdrawEntries, generate_entriesList]


    def get_form(self, request, obj=None, **kwargs):
        form = super(EntryAdmin, self).get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['poem'].widget.attrs['style'] = 'width: 32em;'
            form.base_fields['competition'].widget.attrs['style'] = 'width: 32em;'
        return form


    def get_queryset(self, request):
        if request.user.is_superuser:
            return Entry.objects.all()
        else:
            return Entry.objects.filter(poet=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "poem":
            qs = Poem.objects.filter(Q(poet=request.user) & ((Q(mu=False) & Q(nE2C=0) & Q(nS2M=0) & Q(niP=0)) | Q(mu=True)) & Q(wip=False))
            kwargs["queryset"] = qs
        if db_field.name == "competition":
            kwargs["queryset"]=Competition.objects.filter( Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID) )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self,request,obj=None):
        if obj: #This is the case when obj is already created i.e. it's a change/edit
            return ['competition','poem','expiredOn']
        else:
            return ['expiredOn']

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModelName = 'Entry'
        if isDemoUserAttemptingCCSA(request, theModelName,  'Save'): return
        comp=Competition.objects.get(id=obj.competition_id)
        compName=comp.name
        poemID=obj.poem_id
        poem=Poem.objects.get(id=poemID)
        poemTitle=poem.title
        theID = u'%s to %s' % (poemTitle, compName)
        super().save_model(request, obj, form, change)
        successMsg(request,theModelName, theID)
        return

admin.site.register(Entry, EntryAdmin)

class entryInline(admin.TabularInline):
    fields=('poem','enteredOn','committedUntil','place','expiredOn')
    readonly_fields=('poem','enteredOn','committedUntil','place','expiredOn')
    model = Entry
    extra = 0
    suit_classes = 'suit-tab suit-tab-entries'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Entry.objects.all()
        else:
            return Entry.objects.filter(poet=request.user)

# =================  COMPETITION ========================================

class closingCompetitionsFilter(InputFilter):
    # filter the competitions by <= the number of losing dayd
    parameter_name = 'number of closing days'
    title = 'closing within the next number of days'

    def queryset(self, request, queryset):
        if self.value() is None: return None
        try:
            withinClosingDays=int(self.value())
        except:
            scriptMessages(request, u"Error: '%s' ??? Expected a number of days for the filter window" % self.value())
            return None
        if withinClosingDays<0 or withinClosingDays>31:
            scriptMessages(request, u"Error: %s ??? Within closing days filter number must be >=0 and <=31" % withinClosingDays)
            return None
        nowDate = datetime.now().date()
        endWindowDate = nowDate + timedelta(days=withinClosingDays)
        # get competitons that are closing
        compsClosing = queryset.filter(closingDate__gte=nowDate, closingDate__lte=endWindowDate )
        if compsClosing.count()==0: return None
        return compsClosing

from .models import Competition


class CompetitionAdmin(admin.ModelAdmin):
    list_display=('name','closingDate','entryFee','prize','country','access')
    list_filter=( closingCompetitionsFilter,
                  ('entryFee',DropdownFilter),
                  ('prize',DropdownFilter),
                  ('country',ChoicesDropdownFilter),
                   'access' )
    search_fields = ('name',)
    ordering = ('name','closingDate','entryFee','prize')
    date_hierarchy = ('closingDate')
    inlines = (entryInline,)
    actions = [updateAllCompetitions, compsLastUpdated]
    readonly_fields = ('noOfEntries',)
    list_per_page = settings.LIST_PER_PAGE

    fieldsets = [
        (None, {
            'classes': ('suit-tab',  'suit-tab-entries'),
            'fields': [('name','country'),('closingDate','entryFee','prize','noOfEntries'),'url'],
        }),
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(CompetitionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['name'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['url'].widget.attrs['style'] = 'width: 50em;'
        return form


    # set queryset to user's default country
    def changelist_view(self, request, extra_context=None):
        if not request.META['QUERY_STRING'] and \
                not request.META.get('HTTP_REFERER', '').startswith(request.build_absolute_uri()):
            return HttpResponseRedirect(request.path + "?country__exact="+request.session['Country_preference'])
        return super(CompetitionAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Competition.objects.all()
        else:
            return Competition.objects.filter(Q(poet=request.user) | Q(poet=settings.THE_ADMIN_ID))

    def get_actions(self, request):
        actions = super(CompetitionAdmin, self).get_actions(request)
        if request.user.is_superuser:
            pass
        else:
            # do not allow regular user the action to bulk delete competitions
            del actions['delete_selected']
        return actions

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModel="competition"
        theID=obj.name
        if isDemoUserAttemptingCCSA(request, theModel, 'Save'): return
        if not obj.pk: # new record
           obj.poet = request.user
           if not request.user.is_superuser:
                obj.access = 'Private'
        else:
            if obj.poet != request.user:
                msg="Error: You can only change the competitions that you added! I.e. the private competitions."
                scriptMessages(request,msg)
                return
        super().save_model(request, obj, form, change)
        successMsg(request, theModel,theID)
        return

    def delete_model(self, request, obj):
        if isDemoUserAttemptingCCSA(request, "Competition", 'Delete'): return
        if self.poet != request.user:
            msg = "Error: You can only delete the competitions that you added!"
            scriptMessages(request, msg)
            return
        else:
            return super().delete_model(self, request, obj)

    def delete_queryset(self,request,queryset):
        if isDemoUserAttemptingCCSA(request, "Competitions", 'Delete'): return
        if not request.user.is_superuser:
            for q in queryset:
                if q.poet != request.user:
                    msg="Error: You can only delete the competitions that you added!"
                    scriptMessages(request, msg)
                    return
        return super().delete_model(request, queryset)

    def baton_cl_rows_attributes(self, request, cl):
        data = {}
        if request.session['highlight competitions'] == 0:
            pass
        else:
            rshc = request.session['highlight competitions']
        # change the background colour of the competition if it has/had entries
            data = {}
            for ents in Entry.objects.filter(poet=request.user) :
                if ents.expiredOn==None:
                    if rshc == 1 or rshc == 3:
                        data[ents.competition_id] = {'class': 'table-info',}
                else:
                    if rshc == 2 or rshc == 3:
                        data[ents.competition_id] = {'class': 'table-secondary', }
        return json.dumps(data)


admin.site.register(Competition, CompetitionAdmin)

