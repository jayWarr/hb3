from datetime import datetime, timedelta

from cuser.middleware import CuserMiddleware
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey

from collection.models import Poem
from core.choices import COUNTRIES, PLACE_CHOICES, PP_CHOICES, lookupChoiceText
from core.poemSupportRoutines import isInEligible
from maintenance.models import Profile

# =================  COMPETITION ========================================

class Competition(models.Model):
    # ADMIN owns all public competitions, local user owns all private (non-public) competitions
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,limit_choices_to=CuserMiddleware.get_user())
    name = models.CharField('competition', max_length=80, unique=True)
    entries=models.ManyToManyField(Poem, through='Entry')
    closingDate=models.DateField('closing date')
    url = models.URLField('url')
    access = models.CharField('access', max_length=7,default='Public', editable=False, choices=PP_CHOICES,help_text="Competition access - default is public, alternative is private")
    entryFee=models.CharField('entry fee', max_length=40)
    prize = models.CharField('prize', max_length=40, blank=True)
    country=models.CharField('country', max_length=3,choices=COUNTRIES,default='GBR')
    noOfEntries=models.PositiveSmallIntegerField('number of entries',default=0)

    def __str__(self):
        return self.name




# =================  ENTRY ==============================================

class Entry(models.Model):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,limit_choices_to=CuserMiddleware.get_user())
    competition = models.ForeignKey(Competition, verbose_name='competition', on_delete=models.CASCADE)
    poem = models.ForeignKey(Poem, verbose_name='poem', on_delete=models.CASCADE)
    enteredOn = models.DateField('entered on', default=timezone.now)
    committedUntil = models.DateField('committed until', blank=True, null=True,
                                      help_text='Leave empty for the date to be calculated using the default wait days.')
    place = models.CharField('placement', max_length=4, choices=PLACE_CHOICES, default='ukn')
    expiredOn=models.DateField('expired on', blank=True, null=True)

    class Meta:
        ordering = (('competition'), ('poem'),('enteredOn'),('committedUntil'),)
        unique_together  = ('competition','poem')
        verbose_name_plural = "Entries"

    def __str__(self):
        return ''
         # return u'poem: %s is an entry to competition: %s' % (self.poem,self.competition)

    def delete(self,*args, **kwargs):
        self.decrementCompEntry()
        self.expireEntry('dlt')
        super(Entry, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # get competition
        theCompetition = Competition.objects.get(name=self.competition)
        # get poet id from poem & the wait days from user parameters
        thePoem = Poem.objects.get(id=self.poem_id)
        thePoet = thePoem.poet
        theUP = Profile.objects.get(user=thePoet)
        entryWaitdays = theUP.wd4c
        if self.committedUntil is None and thePoem.mu==False:
            # don't et the committed until date if this is a multiple use poem
            # the date is not necessary since it is always available
            # if single use & if not already set by user - set the committed until date
            cuDate = theCompetition.closingDate + timedelta(days=entryWaitdays)
            self.committedUntil = cuDate
        if self.pk is None: # this is a new competition entry
            if isInEligible(thePoem): return
            # update the no of entries to the competition
            theCompetition.noOfEntries += 1
            theCompetition.save()
            # new entry - update entry counts
            thePoem.nE2C += 1
            thePoem.dtlu=timezone.now()
            thePoem.save()
        else:
            if self.place!="ukn" and not self.expiredOn: # entry has finished so expire
                self.expireEntry()
                return
        super(Entry, self).save(*args, **kwargs)

    def decrementCompEntry(self):
        theComp=Competition.objects.get(id=self.competition_id)
        theComp.noOfEntries -=1
        theComp.save()

    def withdrawEntry(self):
        self.decrementCompEntry()
        self.expireEntry('wtd')

    def hasEntryExpired(self): # check for expiration & expire if necessary
        if self.expiredOn==None  and self.committedUntil<datetime.today():
            self.expireEntry('unp')

    def expireEntry(self,placement):
        if placement!='dlt':
            self.expiredOn=datetime.now()
            self.place=placement
            self.save()
        # update the entry counts & status for the poem
        thePoem=Poem.objects.get(id=self.poem_id)
        thePoem.nE2C-=1
        thePoem.nEE2C +=1
        thePoem.save()

    def clean(self, *args, **kwargs):
        if self.pk is not None:  # this is a CHANGE
            orig = Entry.objects.get(pk=self.pk)
            poemChange = (orig.poem != self.poem)
            competitionChange = (orig.competition != self.competition)
            committedUntilChange = (orig.committedUntil != self.committedUntil)
            if competitionChange:
                raise ValidationError({'competition': ValidationError(
                    "You cannot change the competition! You must delete the original entry and re-submit the new entry.",
                    code='invalid'), })
            if poemChange:
                raise ValidationError({'poem': ValidationError(
                    "You cannot change the poem! You must delete the original entry and re-submit the new entry.",
                    code='invalid'), })
            if committedUntilChange:
                if self.committedUntil < self.enteredOn:
                    raise ValidationError({'committedUntil': ValidationError(
                        'The committed until date must be after the entered date !',
                        code='invalid'), })
        else:  # this is new
            if self.committedUntil is not None:
                if self.committedUntil < datetime.today():
                    raise ValidationError({'committedUntil': ValidationError(
                        'The committed until date must be after today !',
                        code='invalid'), })
        return
