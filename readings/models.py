from django.conf import settings
from django.db import models
from django.utils import timezone

from collection.models import Poem
from core.choices import EVENT_CHOICES

# =============== GROUP ============================================

class Group(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, editable=False)
    name = models.CharField('group', max_length=80, unique=True)
    url = models.URLField('url',blank=True, null=True)

    def __str__(self):
        return self.name


# =============== EVENT ============================================

class Event(models.Model):
    group=models.ForeignKey(Group,verbose_name='group', on_delete=models.CASCADE)
    name = models.CharField('name', max_length=80)
    readings = models.ManyToManyField(Poem, through='Reading')
    type= models.SmallIntegerField('type', choices=EVENT_CHOICES)
    heldOn=models.DateField('held on')
    url = models.URLField('url', blank=True, null=True)

    class Meta:
        unique_together = ('group','name','type','heldOn')

    def __str__(self):
        for ev in EVENT_CHOICES:
            n,et = ev
            if n==self.type:
                eventType=et
        return u'%s: %s - %s on %s' % (self.group,self.name,eventType, self.heldOn)

# =============== READING ============================================

class Reading(models.Model):
    event=models.ForeignKey(Event,verbose_name='event', on_delete=models.CASCADE)
    poem = models.ForeignKey(Poem, verbose_name='poem', on_delete=models.CASCADE)

    class Meta:
        unique_together= ('event','poem')


    def __str__(self):
        return u'%s at event' % (self.poem)

