from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from core.choices import BOOLEAN_CHOICES_MU
from core.poemSupportRoutines import reverseWIP_poem, reassignForm, fixTag, fixTitles, reassignMu, fixDtlu, \
    naturalisePoemTitle
from core.utilitySupportRoutines import processUploads, versionCurrentWIPNote, get_Current_WIP_details, \
    createAFinishedVersionOfTheCurrentWIPPoem,  unsetTheCurrentWIP, createCategoryDownloads
from core.reportSupportRoutines import generateADetailedPoemReport, generate_poemList, generateCategoriesReport, \
    generateCategorizedPoemsReport, generateNotesReport, generate_LinksList
from core.generalSupportRoutines import  successMsg, issueMessage, isDemoUserAttemptingCCSA, scriptMessages, \
    IntPlusIntPositive, get_UserProfileIntoSessionValues, isNotDemoUser
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from next_prev import next_in_order, prev_in_order
from baton.admin import InputFilter
from django.db.models import F,Q
import os
from django.utils.html import mark_safe
import json
from django_mptt_admin.admin import DjangoMpttAdmin
from django.db import IntegrityError
from django.http import HttpResponse
from baton.admin import DropdownFilter, RelatedDropdownFilter
import collections
from maintenance.models import Profile
from taggit.models import Tag


global thePoemFilteredQuerySet,theFirstPoemId,thePreviousPoemId,theNextPoemId,theLastPoemId

def isNoID(theP):
    if theP is None:
        return 0
    else:
        return theP.id

def get_theCurrentPoemID(self, request):
    thePath = request.get_full_path()
    thePathContents = []
    thePathContents = thePath.split('/')
    if thePathContents[4]=='add':
        return 0
    else:
        return int(thePathContents[4])

def firstPreviousNextLastIds(self,request):
    global thePoemFilteredQuerySet, theFirstPoemId, thePreviousPoemId, theNextPoemId, theLastPoemId
    theCurrentPoemId=get_theCurrentPoemID(self, request)
    if theCurrentPoemId==0:
        theFirstPoemId=0
        thePreviousPoemId=0
        theNextPoemId=0
        theLastPoemId=0
    else:
        theCurrentPoem = Poem.objects.get(id=theCurrentPoemId)
        theFirstPoem = thePoemFilteredQuerySet.first()
        theFirstPoemId = isNoID(theFirstPoem)
        thePreviousPoem = prev_in_order(theCurrentPoem, qs=thePoemFilteredQuerySet)
        thePreviousPoemId = isNoID(thePreviousPoem)
        theNextPoem = next_in_order(theCurrentPoem, qs=thePoemFilteredQuerySet)
        theNextPoemId = isNoID(theNextPoem)
        theLastPoem = prev_in_order(theFirstPoem, qs=thePoemFilteredQuerySet, loop=True)
        theLastPoemId = isNoID(theLastPoem)
        if theFirstPoemId==theCurrentPoemId: theFirstPoemId=0
        if thePreviousPoemId==theFirstPoemId: thePreviousPoemId=0
        if theNextPoemId==theLastPoemId: theNextPoemId=0
        if theLastPoemId==theCurrentPoemId: theLastPoemId=0
    return

#=================  Link ==========================================================

from .models import Link

class LinkAdmin(admin.ModelAdmin):
    list_display = ('poem','type','url')
    fields =('poem','type','url')
    ordering = ( 'poem','type')
    list_filter = (('poem', admin.RelatedOnlyFieldListFilter),'type')
    search_fields = ('poem',)
    actions = (generate_LinksList,)

    def get_form(self, request, obj=None, **kwargs):
        form = super(LinkAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['url'].widget.attrs['style'] = 'width: 50em;'
        return form

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Link.objects.all()
        else:
            return Link.objects.filter(poem__in=Poem.objects.filter(poet=request.user))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'poem':
            kwargs['queryset'] = Poem.objects.filter(poet=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModelName='link'
        thePoem=Poem.objects.get(id=obj.poem_id)
        theModelID=thePoem.title
        if isNotDemoUser(request, theModelName,theModelID):
            super().save_model(request, obj, form, change)
            successMsg(request,theModelName,theModelID)
        return


admin.site.register(Link,LinkAdmin)

class LinkInline(admin.TabularInline):
    fields = ('type','url')
    readonly_fields = ('type','url')
    model = Link
    extra = 0
    classes = ('grp-collapse grp-open',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



# =================  Note ================================================
from .models import Note
class NoteAdmin(admin.ModelAdmin):
    fields=(('created','updated'),('type','subtype'), 'poem','topic','content')
    list_display=('poem','type','subtype','topic','updated')
    list_filter = (('poem', admin.RelatedOnlyFieldListFilter),'type','subtype','topic')
    ordering = ('poem','type','subtype','updated')
    actions = (versionCurrentWIPNote, createAFinishedVersionOfTheCurrentWIPPoem, generateNotesReport, )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            # if wip or version only content can be changed
            if obj.type=='_wip_' or obj.type=='_vrn_':
                return ['created', 'updated', 'type', 'subtype','poem','topic',]
        return ['created', 'updated', 'type', ]


    def get_queryset(self, request):
        if request.user.is_superuser:
            qs = Note.objects.all()
        else:
            qs = Note.objects.filter(poet=request.user)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'poem':
            kwargs['queryset'] = Poem.objects.filter(poet=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(NoteAdmin, self).get_form(request, obj, **kwargs)
    #     # if not obj:
    #     form.base_fields['poem'].widget.attrs['style'] = 'width: 52em;'
    #     form.base_fields['topic'].widget.attrs['style'] = 'width: 52em;'
    #     return form


# highlight current WIP Note if set in profile
    def baton_cl_rows_attributes(self, request, cl):
        if request.session['highlight note']==0:
            pass
        else:
            wip_id=int(request.session['Current_WIP_poem'])
            data = {}
            try:
                wipNote=Note.objects.filter(poem_id=wip_id).filter(type='_wip_').order_by('-updated')[0]
                data[wipNote.id] = {'class': 'table-info', }
                return json.dumps(data)
            except IOError:
                pass
        return

admin.site.register(Note, NoteAdmin)


class NoteInline(admin.TabularInline):
    fields=('created','type','subtype','topic')
    readonly_fields = ('created','type','subtype','topic')
    model = Note
    extra = 0
    classes = ('grp-collapse grp-open',)
    verbose_name = ''

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



#=================  CATEGORIZE & CATEGORY ========================================

from .models import Categorize
class CategorizeAdmin(admin.ModelAdmin):
    fields=('poem','category')
    list_display = ('poem', 'category')
    list_filter = ('category',)

    def get_queryset(self, request):
        if request.user.is_superuser:
            qs = Categorize.objects.all()
        else:
            qs = Categorize.objects.filter(poet=request.user)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "poem":
            qs = Poem.objects.filter(poet=request.user).order_by('title')
            kwargs["queryset"] = qs
        if db_field.name == "category":
            qs = Category.objects.filter(poet=request.user).order_by('name')
            kwargs["queryset"]= qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        theModelName = 'Categorize'
        if isDemoUserAttemptingCCSA(request, theModelName, 'Save'): return
        super().save_model(request, obj, form, change)
        return

admin.site.register(Categorize, CategorizeAdmin)

class CategorizeInline(admin.TabularInline):
    fields = ('category',)
    readonly_fields = ('category',)
    model = Categorize
    extra = 0
    classes = ('grp-collapse grp-open',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class PoemCatInline(admin.TabularInline):
    fields = ('poem',)
    model = Categorize
    extra = 0
    classes = ('grp-collapse grp-open',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "poem":
            kwargs["queryset"] = Poem.objects.filter(poet=request.user ).order_by('title')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

#------------------  CATEGORY -----------------------------------


from .models import Category
class CategoryAdmin(DjangoMpttAdmin):
    item_label_field_name = 'title_for_admin'
    fields = ( 'name', 'parent','count')
    readonly_fields = ('slug', 'count')
    inlines = (PoemCatInline,)
    list_display = ( 'name', 'parent','count')
    ordering = ( 'name', 'parent','count')
    actions = (generateCategoriesReport, generateCategorizedPoemsReport, createCategoryDownloads,)
    list_per_page = settings.LIST_PER_PAGE


    def filter_tree_queryset(self, queryset, request):
        return queryset.filter(poet=request.user)

    def get_queryset(self, request):
        if request.user.is_superuser:
            qs = Category.objects.all()
        else:
            qs = Category.objects.filter(poet=request.user).order_by('name')
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "name":
            root = Category.objects.get(name=request.session['User_name'])
            kwargs["queryset"]  = root.get_descendants(include_self=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        theModelName = 'Category'
        if isDemoUserAttemptingCCSA(request, theModelName, 'Save'): return
        super().save_model(request, obj, form, change)
        return

admin.site.register(Category,CategoryAdmin)



#=================  POETIC FORM ===================================================

from .models import PoeticForm

class PoeticFormAdmin(admin.ModelAdmin):
    list_display = ('name','reference','id')
    search_fields = ('name',)
    ordering = ('id','name',)
    list_per_page = settings.LIST_PER_PAGE

    def get_form(self, request, obj=None, **kwargs):
        form = super(PoeticFormAdmin, self).get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['reference'].widget.attrs['style'] = 'width: 50em;'
        return form

admin.site.register(PoeticForm,PoeticFormAdmin)

#=================  POEM ==========================================================

from entries.models import Entry
class EntryInline(admin.TabularInline):
    fields=('competition','enteredOn','committedUntil','place','expiredOn')
    readonly_fields=('competition','enteredOn','committedUntil','place','expiredOn')
    model = Entry
    extra = 0
    classes = ('grp-collapse grp-open',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

from submissions.models import Submission

class SubmissionInline(admin.TabularInline):
    fields = ('magazine', 'submittedOn', 'committedUntil', 'status', 'inEdition','expiredOn')
    readonly_fields = ('magazine', 'submittedOn', 'committedUntil', 'status', 'inEdition','expiredOn')
    model = Submission
    extra = 0
    classes = ('grp-collapse grp-open',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

from publishing.models import Content
class ContentInline(admin.TabularInline):
    fields=('publication',)
    readonly_fields = ('publication',)
    model = Content
    extra = 0
    classes = ('grp-collapse grp-open',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

from readings.models import Reading
class ReadingInline(admin.TabularInline):
    fields=('event',)
    readonly_fields = ('event',)
    model = Reading
    extra = 0
    classes = ('grp-collapse grp-open',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

#-----------------Filter poem useage---------------------------------------
class usedPoemsFilter(InputFilter):
# filter the poem useage by summing the entries, submissions & publications
    parameter_name = 'total used'
    title = ' the ESP sum [ {=} | < | > | >= | <= | != ]  [ 0 . . . 9 ]'

    def queryset(self, request, queryset):
        if self.value() is None: return None
        exp1Allowed=['=','>','<']
        exp2Allowed=['!=','>=','=>','<=','=<']
        equals=False
        greaterthan=False
        lessthan=False
        notequal=False
        greaterthanorequal=False
        lessthanorequal=False
        lsv=len(self.value())
        if lsv==1:
            equals=True
            try:
                search_number = int(self.value())
            except:
                return None
        elif lsv==2:
            exp=self.value()[0]
            if exp not in exp1Allowed: return None
            if exp==exp1Allowed[0]:
                equals = True
            elif exp==exp1Allowed[1]:
                greaterthan=True
            else:
                lessthan=True
            search_number = int(self.value()[1])
        elif lsv == 3:
            exp = self.value()[:2]
            if exp not in exp2Allowed: return None
            if exp==exp2Allowed[0]:
                notequal=True
            elif exp==exp2Allowed[1] or exp==exp==exp2Allowed[2]:
                greaterthanorequal=True
            elif exp == exp2Allowed[3] or exp == exp == exp2Allowed[4]:
                lessthanorequal = True
            search_number = int(self.value()[2])
        if search_number<0 or search_number>10: return None
        p0 = queryset.annotate(total=F('nE2C') + F('nS2M') + F('niP')).values('total', 'id')
        p1=[]
        for q in p0:
            if (
               (equals and q['total']==search_number)\
                or (greaterthan and q['total']>search_number)\
                or (lessthan and q['total']<search_number)\
                or (notequal and q['total']!=search_number)\
                or (greaterthanorequal and q['total']>=search_number) \
                or (lessthanorequal and q['total'] <= search_number) \
                ): p1.append(q['id'])
        if len(p1)==0: return None
        p1.sort()
        q1=queryset.filter(pk__in=p1)
        return q1

class categoryPoemFilter(admin.SimpleListFilter):
    # filter the poem useage by category
    parameter_name = 'category'
    title = 'category'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            qs1 = Categorize.objects.all().values_list('category', flat=True)
        else:
            qs1 = Categorize.objects.filter(poet=request.user).values_list('category', flat=True)
        qs2=list(dict.fromkeys(list(qs1)))
        q3=[]
        for q in qs2:
            c=Category.objects.get(id=q)
            q3.append((c.name, _(c.name)))
        sorted_by_name = sorted(q3, key=lambda tup: tup[0])
        return sorted_by_name

    def queryset(self, request, queryset):
        if self.value() is not None:
            scws = self.value().split()
            scw=[s.capitalize() for s in scws]
            sc1 = scw[0]
            nscw=len(scw)
            if nscw==1:
                twoCat=False
            else:
                twoCat=True
                if nscw==2:
                    ao=True
                    sc2=scw[1]
                else:
                    sc2=scw[2]
                    if scw[1]=='And' or scw[1]=='&':
                        ao=True
                    elif scw[1]=='Or' or scw[1]=='|':
                        ao=False
                    else:
                        issueMessage(request, u"Warning: Category filtering has failed - could not recognize: '%s' as 'and, &, or, |'" % scw[1] )
                        return
            try:
                if twoCat:
                    theCat = Category.objects.filter(Q(poet=request.user) & (Q(name__icontains=sc1) | Q(name__icontains=sc2))).values_list('id', flat=True)
                else:
                    theCat = Category.objects.filter(poet=request.user, name__icontains=sc1).values_list('id',flat=True)
                try:
                    # get the poem ids with this category
                    p1 = Categorize.objects.filter(category_id__in=theCat).values_list('poem_id',flat=True)
                    if twoCat:
                        if ao: # retrieve duplicates
                            p1=[item for item, count in collections.Counter(p1).items() if count > 1]
                        else: # Or so remove duplicates
                            p1 = list(dict.fromkeys(p1))
                except Exception as e:
                    issueMessage(request, u"Warning: Category filtering failed ! '%s (%s)' % (e.message, type(e)")
                    return None
                if len(p1)==0:
                    issueMessage(request, u"Warning: Category filtering failed - no poems found.")
                    return
                 # filter these poems out of current queryset
                q1=queryset.filter(pk__in=p1)
                return q1
            except Exception as e:
                    issueMessage(request, u"Warning: Category filtering failed ! '%s (%s)' % (e.message, type(e)")
        return None

#=================  USER TAG FILTER ===================================================

class userTagsFilter(admin.SimpleListFilter):
    title=_('tags')
    parameter_name='tags'

    def lookups(self,request, model_admin):
        if request.user.is_superuser:
            plist=Poem.objects.all()
        else:
            plist=Poem.objects.filter(poet=request.user)
        tags=Tag.objects.filter(poem__in=plist).distinct()
        tags=sorted(tags)
        tt=[]
        for t in tags:
            tt.append((t.name, _(t.name)))
        return tuple(tt)

    def queryset(self,request,queryset):
        if self.value():
            return queryset.filter(tags__name__in=[self.value()])
        return queryset

#-----------------------------------------------------------------------

class muFilter(admin.SimpleListFilter):
    title = _('Use')
    parameter_name = 'mu'

    def lookups(self,request, model_admin):
        return BOOLEAN_CHOICES_MU

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(mu=self.value())
        return queryset

#----------------------------------------------------------------------

from .models import Poem

class PoemAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    date_hierarchy = ('dtlu')
    readonly_fields = ('dtlu','nE2C','nEE2C','nS2M','nES2M','niP','nR','cCdt', 'hCdt','hbu')
    ordering = ('title', 'dtlu')
    inlines = (NoteInline,CategorizeInline, EntryInline,SubmissionInline,ContentInline, ReadingInline, LinkInline,)
    exclude = ('poem',)
    actions = [reverseWIP_poem, fixTitles, fixDtlu, fixTag, reassignForm, reassignMu, generate_poemList, generateADetailedPoemReport]
    list_per_page = settings.LIST_PER_PAGE

    # baton_form_includes = [
    #     ('collection/poemAddChange.html', 'hbu', 'below',)
    # ]

    # highlight poem(s) dependent on profile setting
    def baton_cl_rows_attributes(self, request, cl):
        data = {}
        if request.session['highlight poem'] == 0:
            pass
        elif request.session['highlight poem'] == 1:
            if request.session['has_Current_WIP_poem'] == True:
                theWIPPoem_id = int(request.session['Current_WIP_poem'])
                data[theWIPPoem_id] = {'class': 'table-info', }
        else:
            dmu = request.session['Default_multiple_use']
            pMUneDMU = Poem.objects.filter(poet=request.user).exclude(mu=dmu)
            for p in pMUneDMU:
                data[p.id] = {'class': 'table-secondary', }
        return json.dumps(data)

    def cat_list(self,obj):
        catz=Categorize.objects.filter(poem_id=obj.id)
        if len(catz)==0: return ''
        cl = ''
        for c in catz:
            cat=Category.objects.get(id=c.category_id)
            cl += u'%s, ' % cat.name
        return cl[:-2]

    def current_Entries_Submissions(self,obj):
        return u'%s %s' % (obj.nE2C,obj.nS2M)

    def historical_Entries_Submissions(self,obj):
        return u'%s %s' % (obj.nEE2C,obj.nES2M)

    def number_of_Publications_Readings(self,obj):
        return u'%s %s' % (obj.niP, obj.nR)

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    # construct the fieldset classes by removing the ones that are not needed
    def get_fieldsets(self, request, obj=None):
        global theCurrentCounts
        theCurrentCounts=[]
        global theExpiredCounts
        theExpiredCounts=[]
        global theClasses
        theClasses = ['baton-tabs-init', 'baton-tab-inline-note','baton-tab-inline-categorize','baton-tab-inline-entry', 'baton-tab-inline-submission', 'baton-tab-inline-content',
                        'baton-tab-inline-reading',  'baton-tab-inline-link']
        theEditedClasses=theClasses.copy()
        fieldsList= ['create',('title', 'mu'), ('wip', 'form','tags'), ('cCdt','nE2C','nS2M', 'hCdt','nEE2C','nES2M', 'hbu','niP','nR','dtlu'),]
        # check that dealing with existing poem
        if obj is not None:                  # poem exists
            fieldsList = fieldsList[1:]  # nb don't need create field
            noteCount=Note.objects.filter(poem_id=obj.id).count()
            categoryCount = Categorize.objects.filter(poem_id=obj.id).count()
            linkCount= Link.objects.filter(poem_id=obj.id).count()
            theCurrentCounts=[0,noteCount,categoryCount, obj.nE2C,obj.nS2M,obj.niP, obj.nR,linkCount]
            theExpiredCounts=[0,obj.nEE2C,obj.nES2M]
            theIndex=-1
            for theClass in theClasses:
                theIndex+=1
                if theIndex>0 and theCurrentCounts[theIndex]==0:
                    theEditedClasses.remove(theClass)
        return [
            ('Details', {
                'fields': fieldsList,
                'classes': tuple(theEditedClasses),
            }),
            ]

    def get_inline_instances(self, request, obj=None):
        allInlines = super(PoemAdmin, self).get_inline_instances(request, obj)
        global theCurrentCounts
        global theClasses
        filteredInlines=[]
        if obj!=None:
            theIndex=-1
            for theClass in theClasses:
                theIndex+=1
                if theIndex > 0 and theCurrentCounts[theIndex] > 0:
                    filteredInlines.append(allInlines[theIndex-1])
        return filteredInlines


    def get_form(self, request, obj=None, **kwargs):
        form = super(PoemAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['title'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['tags'].widget.attrs['style'] = 'width: 29em;'
        return form

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if request.POST.get('_viewnext'):
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_text(obj._meta.verbose_name),
                    'obj': force_text(obj)})
            next = obj.__class__.objects.filter(id__gt=obj.id).order_by('id')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("/admin/collection/poem/%s/change/" % next[0].pk)
        return super(PoemAdmin, self).response_change(request, obj)

    def get_ordering(self, request):
        if request.user.is_superuser:
            ordering = ('poet','title', 'dtlu')
        else:
            ordering = ('title','dtlu')
        return ordering

    def get_list_filter(self, request):
        if request.session['poem listing display'] == 1:
            list_filter = ['cCdt', 'hCdt', 'hbu', 'wip', categoryPoemFilter, userTagsFilter,]
        elif request.session['poem listing display'] == 2:
            list_filter = [('nE2C',DropdownFilter),
                           ('nS2M',DropdownFilter),
                           ('niP',DropdownFilter),
                           ('nR',DropdownFilter),
                           'wip',
                           muFilter,
                           categoryPoemFilter,
                           userTagsFilter,
                           ('form',RelatedDropdownFilter),
                           usedPoemsFilter,
                           ]
        else:
            list_filter = ['wip',
                           categoryPoemFilter,
                           userTagsFilter,
                           usedPoemsFilter,
                           ]
        return list_filter

    def get_list_display(self, request):
        if request.session['poem listing display']==1:
            list_display = ['title', 'cCdt', 'hCdt', 'hbu']
        elif request.session['poem listing display']==2:
            list_display = ['title', 'dtlu', 'nE2C', 'nS2M', 'niP', 'nR', 'wip','cat_list','tag_list']
        else:
            list_display = ['title', 'current_Entries_Submissions', 'historical_Entries_Submissions', 'number_of_Publications_Readings', 'wip', 'cat_list', 'tag_list']
        if request.user.is_superuser: list_display.insert(0,'poet')
        return list_display


    def get_actions(self, request):
        actions = super(PoemAdmin, self).get_actions(request)
        if request.session['poem listing display']==1:
            del actions['fixDtlu']
            del actions['reassignForm']
            del actions['reassignMu']
        return actions

    def get_queryset(self, request):
        if request.user.is_superuser:
            qs = Poem.objects.all().prefetch_related('tags')
        else:
            qs = Poem.objects.filter(poet=request.user).prefetch_related('tags')
        return qs

    def message_user(self, *args):
        pass

# 24-Feb-21 fixed to trap non-unique poeet+title
# because could not make the standard unique together setting work
# 25-May-21 implemented create current WIP profile change & inital note

    def save_model(self, request, obj, form, change):
        if isDemoUserAttemptingCCSA(request, 'poem', 'Save'): return
        # is this a new poem or an old one being updated ?th atcre
        isNewPoem=(obj.pk is None)
        if isNewPoem and obj.mu==None:
            obj.mu = request.session['Default_multiple_use']
        # fix title - wether new or not
        handleTitle = request.session['Handle_titles']
        theInputPoemTitle = obj.title
        # strip off leading & trailing spaces
        ss=theInputPoemTitle.strip()
        if handleTitle == 0:        # leave as is
            tt = ss
        elif handleTitle == 1:      # capitalize 1st letter
            tt = ss.capitalize()
        elif handleTitle == 2:      # lowercase
            tt = ss.lower()
        elif handleTitle == 3:      # naturalise
            tt = naturalisePoemTitle(ss)
        obj.title = tt
        # if existing poem re-calculate current candidate, historical candidate & has been used
        if not isNewPoem:
            obj.cCdt = IntPlusIntPositive(obj.nE2C,obj.nS2M)
            obj.hCdt = IntPlusIntPositive(obj.nEE2C, obj.nES2M)
            obj.hbu  = IntPlusIntPositive(obj.niP, obj.nR)
        try:
            super(PoemAdmin, self).save_model(request, obj, form, change)
            # exception if CREATING poem
            if obj.create:
                scriptMessages(request, u"Info: The poem '%s'will be made the current WIP with an initial _00 note awaiting text" % obj.title)
                up = Profile.objects.get(user_id=request.session['User_id'])
                latestPoem=Poem.objects.all().order_by('-id')[0]
                pO = latestPoem.id
                up.wipp = latestPoem
                up.save()
                # update the request.session user parameters
                get_UserProfileIntoSessionValues(request)
                # create the current WIP nate
                with open(settings.INITIAL_POEM_DRAFT, 'r') as f:
                    tempContent = f.read()
                # theContent = tempContent % {"title": obj.title}
                theContent = tempContent % obj.title

                Note.objects.create(poem=latestPoem, type='_wip_', topic='_00', content=theContent)
                get_Current_WIP_details(request)
                # correct the poem's create & wip flags
                obj.create = False
                obj.wip = True
                super(PoemAdmin, self).save_model(request, obj, form, change)
            else:
                successMsg(request,'poem', obj.title)
            return
        except IntegrityError as saveException:
            issueMessage(request,
                "Error: The registration attempt of the new poem '%s' (or change to an existing one) has been rejected because the title is not unique." % obj.title)
            return

    def delete_queryset(self, request, queryset):
        # to ensure that if the queryset contains current wip
        # its removed from the profile & session
        try:
            wip_id = int(request.session['Current_WIP_poem'])
            # look for wip in queryset
            for qs in queryset:
                if qs.id==wip_id:
                    # remove from profile
                    up=Profile.objects.get(user_id=request.session['User_id'])
                    up.wipp_id = None
                    up.save()
                    # remove from session
                    request.session['Current_WIP_poem']=None
                    request.session['has_Current_WIP_poem']=False
                    request.session['Current_WIP_title'] = None
                    request.session['Current_WIP_note_URL'] = None
                    break
        except:
            pass
        queryset.delete()
        return


    def process_exception(self, request, exception):
        if isinstance(exception, IntegrityError):
            return HttpResponse("😨 IntegrityError")

    def get_title(self,instance):
        return mark_safe('<span class="span-title%d">%s</span>' % (instance.title))
    get_title.short_description = 'title'


    def changelist_view(self, request, extra_context=None):
        global thePoemFilteredQuerySet, theFirstPoemId, thePreviousPoemId, theNextPoemId, theLastPoemId
        response = super(PoemAdmin, self).changelist_view(request, extra_context)
        # need line below to handle correctly the first-previous-next-last button press
        try:
            thePoemFilteredQuerySet = response.context_data["cl"].queryset
        except:
            pass
        return response


    def render_change_form(self, request, context, *args, **kwargs):
        #need to update the context to show the additional buttons dependent on position of current poem in list
        global thePoemFilteredQuerySet, theFirstPoemId, thePreviousPoemId, theNextPoemId, theLastPoemId
        firstPreviousNextLastIds(self, request)
        context.update({'show_first': (theFirstPoemId!=0)})
        context.update({'show_previous': (thePreviousPoemId!=0)})
        context.update({'show_next': (theNextPoemId!=0)})
        context.update({'show_last': (theLastPoemId!=0)})
        return super().render_change_form(request, context, *args, **kwargs)

    def response_post_save_change(self, request, obj):
    # to deal with first-previous-next-last button press with and without filtering
        global thePoemFilteredQuerySet, theFirstPoemId, thePreviousPoemId, theNextPoemId, theLastPoemId

        thePath=request.get_full_path()
        thePathContents=[]
        thePathContents=thePath.split('/')

        if '_first_Poem' in request.POST:
            theReplacement=str(theFirstPoemId)
        elif '_previous_Poem' in request.POST:
            theReplacement=str(thePreviousPoemId)
        elif '_next_Poem' in request.POST:
            theReplacement=str(theNextPoemId)
        elif '_last_Poem' in request.POST:
            theReplacement=str(theLastPoemId)
        else:
            # Otherwise, use default behavior
            return super().response_post_save_change(request, obj)
        # And redirect
        thePathContents[4]=theReplacement
        theNewPath='/'.join(thePathContents)
        return HttpResponseRedirect(theNewPath)

admin.site.register(Poem,PoemAdmin)

#=================  UPLOAD ==========================================================

from .models import Upload

class UploadAdmin(admin.ModelAdmin):
    fields = ( 'description', 'type', 'document', 'logo')
    actions = [processUploads]


    # baton_form_includes = [
    #     ('collection/uploadAddOr.html', 'document', 'below',),
    #     ('collection/uploadAddNB.html', 'logo', 'below', )
    # ]

    def get_list_display(self, request):
        if request.user.is_superuser:
            list_display = ('poet', 'description','type',  'document', 'logo')
        else:
            list_display = ( 'description','type', 'document', 'logo')
        return list_display

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Upload.objects.all()
        else:
            return Upload.objects.filter(poet=request.user)

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        theModelName='upload'
        if isDemoUserAttemptingCCSA(request, theModelName, 'Save'): return
        theModelID=obj.description
        # AOK
        super().save_model(request, obj, form, change)
        successMsg(request,theModelName,theModelID)
        return

admin.site.register(Upload,UploadAdmin)

