from allauth.account.signals import email_confirmed
from cuser.middleware import CuserMiddleware
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_userforeignkey.models.fields import UserForeignKey
from embed_video.fields import EmbedVideoField
import os

from core.choices import (BOOLEAN_CHOICES_MU, BOOLEAN_CHOICES_OO,
                          BOOLEAN_CHOICES_SU, BOOLEAN_CHOICES_YN,
                          CANDIDATE_CHOICES, COUNTRIES, DOWNLOAD_CHOICES,
                          EDIT_TITLE, HIGHLIGHT_POEM_CHOICES, HIGHLIGHT_NOTE_CHOICES,
                          HIGHLIGHT_COMPETITION_CHOICES, HIGHLIGHT_SUBMISSION_CHOICES,
                          HIGHLIGHT_PUBLISHER_CHOICES,
                          LOGO_CHOICES, OS_CHOICES, PERIOD_CHOICES,
                          POEM_LISTING_CHOICES, RESOURCE_CHOICES,
                          WAIT_DAY_CHOICES)
from core.models import TimeStampModel
from core.validators import dropBoxExeValidator

# ================= PROFILE ========================================

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ftfg = models.BooleanField('First time flag', default=True)
    wd4c = models.IntegerField('Wait period for competitions entries', default=31, choices=WAIT_DAY_CHOICES)
    wd4s = models.IntegerField('Wait period for magazine submissions ', default=181, choices=WAIT_DAY_CHOICES)
    wd4p = models.IntegerField('Wait period for publishers response', default=271, choices=WAIT_DAY_CHOICES)
    dacw = models.IntegerField('Advanced days warning of competition closure', default=10,
                               validators=[MinValueValidator(0), MaxValueValidator(31)], help_text="Must be >=1 & <=31")
    dfmu = models.BooleanField('Default use', default=False,
                               help_text='Set either single or multiple use of a poem', choices=BOOLEAN_CHOICES_MU)
    hklr = models.DateField('Last HK run on', null=True, blank=True, editable=False)
    dutg = models.CharField('Default upload tag', max_length=50, default='_Upload_',
                            help_text='Automatically given to uploaded & imported poems')
    abtg = models.CharField('Assigned batch tag', max_length=50, default='_Assigned_')
    dfpf = models.ForeignKey('collection.PoeticForm', verbose_name='Default poetic form', on_delete=models.CASCADE,
                             default=1,
                             help_text='Applies to imported/actioned poems - can be left blank if unknown')
    enct = models.IntegerField('Handle titles', default=3, choices=EDIT_TITLE,
                               help_text="Standarise titles for consistency - applies to imported/actioned poems")
    ludt = models.CharField('Last upload details', max_length=80, default='_None_')
    wipp = models.ForeignKey('collection.Poem', verbose_name='Current WIP poem', blank=True, null=True, on_delete=models.SET_NULL)
    cnty = models.CharField('Country/All preference', max_length=3, choices=COUNTRIES, default='GBR')
    scty = models.CharField('Report competitions closing in country/all', max_length=3, choices=COUNTRIES, default='GBR')
    rbfr = models.BooleanField('Recieve bug fix reports', default=False, choices=BOOLEAN_CHOICES_YN)
    pldo = models.IntegerField('Poem listing display option', default=1, choices=POEM_LISTING_CHOICES)
    logo = models.CharField('Personal logo file', default='', max_length=150, null=True, blank=True)
    lgch = models.SmallIntegerField('Logo choice', default=0, choices=LOGO_CHOICES)
    hpom = models.SmallIntegerField('highlight poem(s)', default=0, choices=HIGHLIGHT_POEM_CHOICES)
    hnot = models.SmallIntegerField('highlight note', default=0, choices=HIGHLIGHT_NOTE_CHOICES)
    hcmp = models.SmallIntegerField('highlight competitions with entries', default=0, choices=HIGHLIGHT_COMPETITION_CHOICES)
    hsub = models.SmallIntegerField('highlight magazines with submissions', default=0, choices=HIGHLIGHT_SUBMISSION_CHOICES)
    hpub = models.SmallIntegerField('highlight publishers with content', default=0, choices=HIGHLIGHT_PUBLISHER_CHOICES)
    vsmg = models.BooleanField('Verbose system messages', default=True, choices=BOOLEAN_CHOICES_YN)


    def clean(self):
        if self.lgch==1 and (self.logo=='' or self.logo is None):
            raise ValidationError(u'Missing image file for personal logo. UPLOAD file and reset choice.')
        return

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# CREATE new user as staff in regular user group with default

# ----------used with allauth to Create New User Parameters--------------------
@receiver(email_confirmed)
def email_confirmed(request, email_address, **kwargs):
# -----------------------------------------------------------------------------
# get the new user reecord
    newUser = User.objects.get(email=email_address.email)

# update to set as staff user
    User.objects.filter(id=newUser.id).update(is_staff = True)

# put into the regular user group
    RegularGroup = Group.objects.get(id=settings.REGULAR_USER_GROUP)
    RegularGroup.user_set.add(newUser)

# setup the user profile parameters with defaults
    Profile.objects.create(user=newUser.id)

# setup up/down load sub-dirs for user
    prefix= os.path.join(settings.MEDIA_ROOT, 'poet_{}'.format(newUser.id))
    os.mkdir(os.path.join(prefix, 'Downloads'))
    os.mkdir(os.path.join(prefix, 'Uploads'))

    return

# =================  SYSTEM PARAMETERs - a single record =================

class SystemParameters(TimeStampModel):

    # --------------------- maintenance parameters -----------------------------
    mmoo = models.BooleanField('Maintenance mode', default=False, choices=BOOLEAN_CHOICES_OO, help_text="WARNING: seeting this to ON switches off the website!")
    mmso = models.DateTimeField('Switched at',blank=True, null=True, help_text='automatically updated')
    mmno = models.SmallIntegerField('Number of', default=1)
    mmpd = models.CharField('Period', max_length=1, choices=PERIOD_CHOICES, default='H')
    mmer = models.DateTimeField('Estimated return',null=True, blank=True, help_text='automatically updated')
    mmmg = models.CharField('Maintenance mode message', null=True, blank=True, max_length=120)
    # ---------------------------------------------------------------------------
    aumg = models.CharField('Sign on message', default='_NONE_', max_length=120)
    vnno = models.CharField('Application Version number', max_length=10, default='0.0.5')
    vndt = models.DateField('Application Version date', null=True, blank=True)
    vncd = models.CharField('Application Version candidate', default='δ', max_length=1, choices=CANDIDATE_CHOICES)
    cplu = models.DateField('Competitions last updated')
    cpui = models.SmallIntegerField("Competitions update interval", default=31,choices=WAIT_DAY_CHOICES)
    mzlu = models.DateField('Magazines last updated')
    mzui = models.SmallIntegerField("Magazines update interval", default=61,choices=WAIT_DAY_CHOICES)
    pblu = models.DateField('Publications last updated')
    pbui = models.SmallIntegerField("Publications update interval", default=91,choices=WAIT_DAY_CHOICES)
    eaer = models.BooleanField('Email admin error report', default=False, choices=BOOLEAN_CHOICES_YN)
    eubr = models.BooleanField('Email user bug fix report', default=False, choices=BOOLEAN_CHOICES_YN)


    class Meta:
        verbose_name_plural = "System parameters"

    def __str__(self):
        return u'Version: %s, dated: %s, candidate: %s' % (self.vnno,self.vndt, self.vncd)


# =================  Web-RESOURCE =======================================

class webResource(TimeStampModel):
    country=models.CharField('country', max_length=3,choices=COUNTRIES,default='GBR')
    type=models.SmallIntegerField('type',choices=RESOURCE_CHOICES)
    noOfUpdates=models.SmallIntegerField('#Updates', default=0, help_text='number of times updated')
    additions=models.SmallIntegerField('#additions', default=0, help_text='additions made last update')
    updateInterval = models.IntegerField('interval', default=31, choices=WAIT_DAY_CHOICES,help_text='update period')
    refSource = models.URLField('reference source')
    reflink =models.CharField('reference link', max_length=100)

# =================  INFORMATION VIDEO ================================================

class InformationVideo(TimeStampModel):
    subject = models.CharField('Subject', max_length=100, blank=True, default='_NONE_'  )
    video = EmbedVideoField('Video',help_text='[ CTRL ] + click to view')
    theOrder = models.PositiveIntegerField('Order', default=0, blank=False, null=False)


    def __str__(self):
        return u'%s video link' %  (self.subject)

    class Meta:
        verbose_name="Information video"
        verbose_name_plural = "Information video"
        ordering = ['theOrder', ]

# =================  DOWNLOADs================================================


#  this model is READ ONLY by the users
#  records will  be created
#  either by ADMIN          - e.g. utilities
#  OR
#  by application process   - e.g. category updates
#  N.B. files placed/created by Admin will be accessible by everyone

def user_directory_path():
    # file will be downloaded from MEDIA_ROOT/poet_<id>/Downloads/<filename>
    return os.path.join(settings.MEDIA_ROOT, 'poet_{}'.format(CuserMiddleware.get_user().id),'Downloads')

class Download(TimeStampModel):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,
                          limit_choices_to=CuserMiddleware.get_user())
    type = models.SmallIntegerField('Type', choices=DOWNLOAD_CHOICES)
    description = models.CharField('Description', max_length=80, blank=False)
    os=models.CharField('OS', max_length=8, choices=OS_CHOICES)
    file = models.FilePathField('File', path=user_directory_path)


# =================  Context Help ================================================

class Help(TimeStampModel):
    context=models.CharField('Context',max_length=100, unique=True)
    lookup=models.CharField('Lookup',max_length=100, blank=True, null=True)

    def __str__(self):
        if self.lookup == None: self.lookup = ''
        return u'Context: %s - lookup: %s' %  (self.context,self.lookup)

    class Meta:
        verbose_name_plural = "Help"
