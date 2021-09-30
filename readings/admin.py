from django.contrib import admin
from django.db.models import Q
from django.utils import timezone

from collection.models import Poem
from core.generalSupportRoutines import isDemoUserAttemptingCCSA
from core.reportSupportRoutines import generate_readingsList

from .models import Reading

# =================  Reading ==============================================


class ReadingAdmin(admin.ModelAdmin):
    list_display = ('event','poem')
    fields=('event','poem')
    ordering=('event','poem',)
    actions = [generate_readingsList]

    def get_form(self, request, obj=None, **kwargs):
        form = super(ReadingAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['event'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['poem'].widget.attrs['style'] = 'width: 50em;'
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            kwargs["queryset"] = Event.objects.filter(group__in=Group.objects.filter(user=request.user))
        if db_field.name == "poem":
            kwargs["queryset"] = Poem.objects.filter(Q(poet=request.user) & Q(wip=False))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Reading.objects.all()
        else:
            return Reading.objects.filter(poem__in=Poem.objects.filter(Q(poet=request.user) & Q(wip=False)))

    def save_model(self, request, obj, form, change):
        theModelName = 'reading'
        if isDemoUserAttemptingCCSA(request, theModelName, 'Save'): return
        theModelID = obj.poem
        if obj.pk is None: # new reading counts & status for the poem
            thePoem = Poem.objects.get(poet=request.user, title=theModelID)  # just in case another user has a poem of the same name!
            thePoem.nR += 1
            thePoem.dtlu = timezone.now()
            thePoem.save()
            super().save_model(request, obj, form, change)
        return

    def delete_model(self, request, obj):
        theModelName = 'reading'
        if isDemoUserAttemptingCCSA(request, theModelName, 'Save'): return
        theModelID = obj.poem
        thePoem = Poem.objects.get(self.poem_id)
        thePoem.nR -= 1
        thePoem.save()
        super().delete(self, request, obj)
        return


admin.site.register(Reading, ReadingAdmin)

class ReadingInline(admin.TabularInline):
    fields=('poem',)
    model = Reading
    extra = 0

    class Media:
        css = {
            'all': ('css/custom_admin.css',)  # Include extra css
        }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "poem":
            kwargs["queryset"] = Poem.objects.filter(poet=request.user ).order_by('title')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# =================  Event ==============================================

from .models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('group','name','type','heldOn','url')
    fields = ('group','name',('type','heldOn'),'url')
    inlines = (ReadingInline,)

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['group'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['name'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['url'].widget.attrs['style'] = 'width: 50em;'
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "group":
            kwargs["queryset"] = Group.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Event.objects.all()
        else:
            return Event.objects.filter(group__in=Group.objects.filter(user=request.user))


admin.site.register(Event, EventAdmin)

class EventInline(admin.TabularInline):
    fields=('name',)
    model = Event
    extra = 0

    class Media:
        css = {
            'all': ('css/custom_admin.css',)  # Include extra css
        }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "name":
            kwargs["queryset"] = Event.objects.filter(user=request.user ).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventInline, self).get_form(request, obj, **kwargs)
        form.base_fields['name'].widget.attrs['style'] = 'width: 80em;'
        return form

# =================  Group ========================================

from .models import Group


class GroupAdmin(admin.ModelAdmin):
    list_display=('name',)
    fields=('name','url')
    ordering=('name',)
    inlines=(EventInline,)


    def get_form(self, request, obj=None, **kwargs):
        form = super(GroupAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['name'].widget.attrs['style'] = 'width: 50em;'
        form.base_fields['url'].widget.attrs['style'] = 'width: 50em;'
        return form

    def save_model(self, request, obj, form, change):
        theModel='Group'
        if isDemoUserAttemptingCCSA(request, theModel, 'Save'): return
        if not obj.pk:
           obj.user = request.user
        super().save_model(request, obj, form, change)


    def get_queryset(self, request):
        if request.user.is_superuser:
            return Group.objects.all()
        else:
            return Group.objects.filter(user=request.user)

admin.site.register(Group, GroupAdmin)


