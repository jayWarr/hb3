from datetime import datetime, timedelta

from cuser.middleware import CuserMiddleware
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey

from collection.models import Poem
from core.choices import (COUNTRIES, PP_CHOICES, SC_SUFFIX,
                          SUBMISSION_STATUS_CHOICES, lookupChoiceText)
from core.poemSupportRoutines import isInEligible
from maintenance.models import Profile

# =================  MAGAZINE ========================================

class Magazine(models.Model):
    # ADMIN owns all public cmagazines, local user owns all private (non-public) magazines
    poet = UserForeignKey(auto_user_add=True, editable=False,limit_choices_to=CuserMiddleware.get_user())
    name = models.CharField('magazine', max_length=80, unique=True)
    submissions=models.ManyToManyField(Poem, through='Submission')
    url = models.URLField('url')
    access = models.CharField('access', max_length=7,default='Public', editable=False, choices=PP_CHOICES,help_text="Magazinemags= access - default is public, alternative is private")
    country = models.CharField('country', max_length=3, choices=COUNTRIES, default='GBR')
    noOfSubmissions = models.PositiveSmallIntegerField('number of submissions', default=0)

    def __str__(self):
        return self.name


# =================  SUBMISSION ========================================

class Submission(models.Model):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,limit_choices_to=CuserMiddleware.get_user())
    magazine=models.ForeignKey(Magazine, verbose_name='magazine', on_delete=models.CASCADE)
    poem=models.ForeignKey(Poem, verbose_name='poem', on_delete=models.CASCADE)
    submittedOn = models.DateField('submitted on', default=timezone.now)
    committedUntil = models.DateField('committed until', blank=True, null=True, help_text='Leave blank for the date to be calculated.' )
    status = models.CharField('status', choices=SUBMISSION_STATUS_CHOICES, default='sbmttd', max_length=6)
    inEdition= models.DateField('in edition',null=True,blank=True)
    expiredOn = models.DateField('expired on',null=True,blank=True)

    class Meta:
        ordering = (('magazine'),('poem'),('submittedOn'),('committedUntil'),)
        unique_together=('magazine','poem')
        verbose_name_plural='submissions'

    def __str__(self):
        return ''
        # return u'poem: %s was submitted to magazine: %s' % (self.poem,self.magazine)

    def summary(self):
        return u'%s: %s %s the magazine: %s - committed until %s' % (
                self.poem, self.status, SC_SUFFIX(SUBMISSION_STATUS_CHOICES.index(self.status)),
                self.magazine, self.committedUntil)

    def save(self, *args, **kwargs):
        # get poet id from poem & the wait days from user parameters
        thePoem = Poem.objects.get(id=self.poem_id)
        thePoet = thePoem.poet
        theUP = Profile.objects.get(user=thePoet)
        submissionWaitDays=theUP.wd4s
        if self.committedUntil is None and thePoem.mu==False:
            # don't et the committed until date if this is a multiple use poem
            # the date is not necessary since it is always available
            # if sinle use & if not already set by user - set the committed until date
            cuDate = datetime.today() + timedelta(days=submissionWaitDays)
            self.committedUntil = cuDate
        if self.pk is None: # new submission counts & status for the poem
            if isInEligible(thePoem): return
            # update the no of submission to the magazine
            theMagazine=Magazine.objects.get(id=self.magazine_id)
            theMagazine.noOfSubmissions += 1
            theMagazine.save()
            # new submssion - update submission count
            thePoem.nS2M += 1
            thePoem.dtlu=timezone.now()
            thePoem.save()
        else:
            textName,index=lookupChoiceText(SUBMISSION_STATUS_CHOICES,self.status)
            if index>=2 and self.expiredOn==None: # submission has finished so expire
                self.expireSubmission()
                return
        super(Submission, self).save(*args, **kwargs)

    def delete(self,*args, **kwargs):
        self.decrementSubmissions()
        self.expireSubmission('deletd')
        super(Submission, self).delete(*args, **kwargs)

    def decrementSubmissions(self):
        theMag=Magazine.objects.get(id=self.magazine_id)
        theMag.noOfSubmissions -= 1
        theMag.save()

    def withdrawSubmission(self):
        self.decrementSubmissions()
        self.expireSubmission('wthdrn')

    def hasSubmissionExpired(self,theStatus): # check for expiration & expire if necessary
        if self.expiredOn==None and self.committedUntil<datetime.today():
            self.expireSubmission(theStatus)

    def expireSubmission(self,theStatus):
        if theStatus!='deletd':
            self.expiredOn=datetime.today()
            self.status=theStatus
            self.save()
          # update the entry counts & status for the poem
        thePoem=Poem.objects.get(id=self.poem_id)
        thePoem.nS2M-=1
        thePoem.nES2M +=1
        thePoem.save()

    def clean(self, *args, **kwargs):
        if self.pk is not None:  # this is a CHANGE
            orig = Submission.objects.get(pk=self.pk)
            poemChange = (orig.poem != self.poem)
            magazineChange=(orig.magazine != self.magazine)
            submittedOnChange = (orig.submittedOn != self.submittedOn)
            committedUntilChange = (orig.committedUntil != self.committedUntil)
            if magazineChange:
                raise ValidationError({'magazine': ValidationError(
                    "You cannot change the magazine! You must delete the submission re-set it.",
                    code='invalid'), })
            if poemChange:
                raise ValidationError({'poem': ValidationError(
                    "You cannot change the poem! You must delete the submission re-set it.",
                    code='invalid'), })
            if submittedOnChange:
                if self.submittedOn > self.committedUntil:
                    raise ValidationError({'submittedOn': ValidationError(
                        'The submitted date must be before the commited until date !', code='invalid'), })
            if committedUntilChange:
                if self.committedUntil < self.submittedOn:
                    raise ValidationError({'committedUntil': ValidationError(
                        'The committed until date must be after the sumitted date !',
                        code='invalid'), })
        else:  # this is new
            if self.committedUntil is not None:
                if self.submittedOn > self.committedUntil:
                    raise ValidationError({'submittedOn': ValidationError(
                        'The submitted date must be before the commited until date !',
                        code='invalid'), })
                if self.committedUntil < self.submittedOn:
                    raise ValidationError({'committedUntil': ValidationError(
                        'The committed until date must be after the sumitted date !',
                        code='invalid'), })


