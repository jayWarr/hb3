from datetime import datetime, timedelta

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.db.models import Q
from maintenance_mode.core import set_maintenance_mode

from collection.models import Note, Poem
from core.generalSupportRoutines import (get_UserProfileIntoSessionValues,
                                         isDemoUserAttemptingCCSA,
                                         scriptMessages, successMsg)
from core.utilitySupportRoutines import (get_Current_WIP_details,
                                         removeClosedCompetitions,
                                         updateMagazines, updatePublishers,
                                         updateUKComps, updateUSAComps,
                                         downloadDownloads)

from .models import Profile
from django.conf import settings
import os

#=================  USER PROFILE =================================================


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)

    def get_list_display(self, request):
        list_display = (
        'user', 'wd4c', 'wd4s', 'wd4p', 'dacw', 'dfmu', 'hklr', 'dutg', 'abtg', 'dfpf', 'enct', 'ludt', 'wipp',
        'cnty', 'scty', 'rbfr', 'pldo', 'lgch','vsmg','hpom','hnot','hcmp','hsub','hpub')
        if request.user.is_superuser:
            list_display += 'logo'
        return list_display

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return 	('user','ftfg','wd4c','wd4s','wd4p','dacw','dfmu', 'dfpf','enct','ludt','wipp', 'cnty','scty','rbfr','pldo', 'lgch','logo','vsmg', ('hpom','hnot','hcmp','hsub','hpub'))
        else:
            return 	('user',('wipp','pldo'),('dfmu','enct'),('wd4c','wd4s'),('wd4p','dacw'), ('dutg','abtg'),('dfpf','ludt'),('cnty','scty'),('rbfr','lgch', 'vsmg'),('hpom','hnot'),('hcmp','hsub','hpub'))

    def get_actions(self, request):
        actions = super(ProfileAdmin, self).get_actions(request)
        if request.user.is_superuser:
            pass
        else:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Profile.objects.all()
        else:
            return Profile.objects.filter(user=request.user)

    def message_user(self, *args):
        pass


    def save_model(self, request, obj, form, change):
        theModelName = 'profile'
        theModelID = request.session['User_name']
        if isDemoUserAttemptingCCSA(request, theModelName, 'Save'): return
        super().save_model(request, obj, form, change)
        successMsg(request, theModelName, theModelID)
        # update the request.session user parameters
        get_UserProfileIntoSessionValues(request)
        get_Current_WIP_details(request)
        return


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "wipp":
            kwargs["queryset"] = Poem.objects.filter(Q(poet=request.user) & Q(wip=True))
            # poemIds=Note.objects.filter(Q(poet=request.user) & Q(type='_wip_')).values_list('poem_id', flat=True)
            # kwargs["queryset"]=Poem.objects.filter(id__in=poemIds)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Profile, ProfileAdmin)


#=================  SYSTEM PARAMETERs - N.B. ONLY ADMIN HAS ACCESS  TO CHANGE  ======

from .models import SystemParameters


class  SystemParametersAdmin(admin.ModelAdmin):

    fields=('mmoo','mmso','mmno','mmpd','mmer','mmmg','aumg','vnno','vndt','vncd','cplu','cpui','mzlu','mzui','pblu','pbui','eaer','eubr')
    read_only=('updated',)
    actions = None

    def get_list_display(self, request):
        list_display=['aumg','vnno','vndt','vncd','cplu','cpui','mzlu','mzui','pblu','pbui','eaer','eubr']
        if request.user.is_superuser:
            list_display=['mmoo','mmso','mmno','mmpd','mmer','mmmg']+list_display
        return list_display


    def save_model(self, request, obj, form, change):
        # set maintenance mode to turn off/on Site mode
        set_maintenance_mode(obj.mmoo)
        if obj.mmoo:	# ON
            # calculate switch back on date time
            nowTime=datetime.now()
            obj.mmso=nowTime
            if obj.mmpd=="M":
                obj.mmer= nowTime+timedelta(minutes=obj.mmno)
            elif obj.mmpd=="H":
                obj.mmer= nowTime+timedelta(hours=obj.mmno)
            elif obj.mmpd == "D":
                obj.mmer = nowTime + timedelta(days=obj.mmno)
            elif obj.mmpd == "W":
                obj.mmer = nowTime + timedelta(weeks=obj.mmno)
        else:  # OFF
            obj.mmso=None
            obj.mmer=None
            obj.mmmg=None
        super().save_model(request, obj, form, change)
        return

admin.site.register(SystemParameters, SystemParametersAdmin)


# =================  Web-RESOURCE N.B. ONLY VISIBLE TO ADMIN ==============================

from .models import webResource


class webResourceAdmin(admin.ModelAdmin):
    list_display = ('type','country', 'noOfUpdates','updateInterval', 'additions', 'updated')
    fields=('type','country','noOfUpdates','updateInterval','additions','refSource','reflink')
    read_only = ('updated',)
    ordering=('type','country')
    actions = [updateUKComps, updateUSAComps, removeClosedCompetitions, updateMagazines,updatePublishers]

admin.site.register(webResource,webResourceAdmin)



#=================  Information Video ================================================

from .models import InformationVideo


class InformationVideoAdmin(SortableAdminMixin,admin.ModelAdmin):
    list_display=('subject','video','updated')

    def get_form(self, request, obj=None, **kwargs):
        form = super(InformationVideoAdmin, self).get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            form.base_fields['subject'].widget.attrs['style'] = 'width: 50em;'
            form.base_fields['video'].widget.attrs['style'] = 'width: 50em;'
        return form

admin.site.register(InformationVideo,InformationVideoAdmin)

# =================  DOWNLOADs ================================================

#  this model is READ ONLY by the users
#  records will  be created
#  either by ADMIN          - e.g. utilities
#  OR
#  by application process   - e.g. category updates
#  N.B. files placed/created by Admin will be accessible by everyone

from .models import Download

class DownloadAdmin(admin.ModelAdmin):
    # read_only = ('updated',)
    ordering = ('os','type', 'updated')
    actions = (downloadDownloads,)

    def get_queryset(self, request):
        theOS = request.user_agent.os.family
        # msg=u"OS is %s" % theOS
        # scriptMessages(request,msg)
        if request.user.is_superuser:
            return Download.objects.all()
        else:
            return Download.objects.filter((Q(poet=request.user) | Q(poet_id=settings.THE_ADMIN_ID)) &  (Q(os=theOS) | Q(os='All')) )


    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('description','poet','os','type','created','updated')
        else:
            return ('description','type','created','updated')

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('os','type','description', 'file')
        else:
            return ('type','description', 'file')

    def get_ordering(self, request):
        if request.user.is_superuser:
            return ('os','type','updated',)
        else:
            return ('type', 'updated',)

    def delete_queryset(self, request, queryset):
        # NB this also deletes the files referenced by the download
        if request.user.is_superuser:
            for q in queryset:
                os.remove(q.file)
            queryset.delete()
        else:
            # don't allow user to delete admin downloads
            msg = ''
            for q in queryset:
                if q.poet_id == settings.THE_ADMIN_ID:
                    if msg=='': msg+='Error: You cannot delete: '
                    msg += u' %s,' % q.description
                else:
                    os.remove(q.file)
                    q.delete()
            if msg!='': scriptMessages(request, msg)

admin.site.register(Download, DownloadAdmin)

#=================  HELP ================================================

from .models import Help

class HelpAdmin(admin.ModelAdmin):
    list_display=('context','lookup','updated')
    ordering=('context','lookup')

admin.site.register(Help,HelpAdmin)
