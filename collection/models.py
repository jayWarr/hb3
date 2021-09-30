from ckeditor.fields import RichTextField
from cuser.middleware import CuserMiddleware
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.db.models import F
from django.db.models.signals import (post_delete, post_save, pre_delete)
from django.dispatch import receiver
from django_userforeignkey.models.fields import UserForeignKey
from mptt.models import MPTTModel, TreeForeignKey

from taggit.managers import TaggableManager

from core.choices import (BOOLEAN_CHOICES_MU, BOOLEAN_CHOICES_YN,
                          NOTE_SUBTYPE_CHOICES, NOTE_TYPE_CHOICES,
                          UPLOAD_CHOICES, URL_TYPE_CHOICES)
from core.models import TimeStampModel
from core.validators import (uploadImageFileValidator,
                             uploadTextFileValidator)
import os


# =================  POETIC FORM ========================================

class PoeticForm(models.Model):
    name = models.CharField('form', max_length=30, unique=True, blank=True, null=True)
    reference = models.URLField('reference', blank=True, null=True, max_length=255)

    class Meta:
        ordering = ([F('name').asc(nulls_first=True)],)

    def __str__(self):
        return self.name


# =================  POEM ================================================

class Poem(models.Model):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,
                          limit_choices_to=CuserMiddleware.get_user())
    title = models.CharField('Title', max_length=100,
                             help_text='Must be unique.')
    dtlu = models.DateField('Last', auto_now_add=True)
    form = models.ForeignKey(PoeticForm, verbose_name='form', on_delete=models.PROTECT, default=1, blank=True,
                             help_text='Can be left blank')
    wip = models.BooleanField('WIP', default=False, help_text='Set True will be automatically excluded as an ESP candidate')
    create = models.BooleanField('Create', default=False, choices=BOOLEAN_CHOICES_YN,
                                 help_text="Set to Yes to have a new, current WIP poem note automatically created. Leave as NO if registering an alraqdy exiting poem.")
    mu = models.BooleanField('Multiple use', default=False, choices=BOOLEAN_CHOICES_MU, help_text='Defaults to profile setting')
    nE2C = models.PositiveSmallIntegerField('Entries', default=0)
    nEE2C = models.PositiveSmallIntegerField('Expired entries', default=0)
    nS2M = models.PositiveSmallIntegerField('Submissions', default=0)
    nES2M = models.PositiveSmallIntegerField('Expired submissions', default=0)
    cCdt = models.BooleanField('Current', default=False)
    hCdt = models.BooleanField('Historical', default=False)
    niP = models.PositiveSmallIntegerField('Publications', default=0)
    nR = models.PositiveSmallIntegerField('Readings', default=0)
    hbu = models.BooleanField('Used', default=False)
    tags = TaggableManager('Tags', blank=True,help_text='Comma delimited identifying words or phrases' )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Poem"
        verbose_name_plural = 'Poems'
        unique_together = ('poet', 'title',)


# =================  Upload ================================================

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/poet_<id>/Uploads/<filename>
    prefix = os.path.join('poet_{}'.format(instance.poet_id),'Uploads')
    return os.path.join(prefix, filename)


class Upload(models.Model):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,
                          limit_choices_to=CuserMiddleware.get_user())
    description = models.CharField('Description', max_length=80, blank=False)
    type = models.SmallIntegerField('Type', default=0, choices=UPLOAD_CHOICES)
    document = models.FileField('Titles document', upload_to=user_directory_path, validators=[uploadTextFileValidator],
                                max_length=150, default='', blank=True,
                                help_text="Must be a hummingbird utility produced text file less than 1MB size")
    logo = models.ImageField('Personal logo', upload_to=user_directory_path, validators=[uploadImageFileValidator],
                             max_length=150, default='', blank=True,
                             help_text="Must be an image file with less than 128w x 128h px diemensionss & less than 40KB size")

    def __str__(self):
        if self.type == 0:
            return u'%s: %s' % (self.document, self.description)
        else:
            return u'%s: %s' % (self.logo, self.description)

    def clean(self):
        if self.type == 0:  # titles document
            if self.document == '' or self.document is None:
                raise ValidationError('Missing titles document.')
        else:  # logo
            if self.logo == '' or self.logo is None:
                raise ValidationError('Missing logo image.')
        if self.document != '' and self.logo != '':
            raise ValidationError(
                'A document & a logo have both been specified. Only one of them is allowed and it must match the type.')


@receiver(pre_delete, sender='collection.Upload', dispatch_uid="file_upload_delete")
def delete_upload(sender, instance, **kwargs):
    if instance.type == 0:
        theFile = str(instance.document)
        theFullPathFile = os.path.join(settings.MEDIA_ROOT, theFile)
        os.remove(theFullPathFile)
    # DON'T delete logo
    return


# =================  Category & Categorization ================================================

class Category(MPTTModel):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,
                          limit_choices_to=CuserMiddleware.get_user())
    name = models.CharField(max_length=50)
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                            db_index=True)
    slug = models.SlugField(null=True, blank=True, editable=False)
    count = models.PositiveSmallIntegerField('count', default=0, editable=False)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super().delete(*args, **kwargs)

    def clean_name(self):
        try:
            newCat = Category.objects.filter(poet=self.poet, name=self.name, parent=self.parent)
            raise ValidationError('This parent-name category already exists.')
        except:
            return self.cleaned_data['name'].capitalize()

    class MPTTMeta:
        order_insertion_by = ['parent', 'name']

    class Meta:
        unique_together = ('name', 'parent', 'slug', 'poet')
        verbose_name_plural = 'categories'

    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except:
            ancestors = []
        else:
            ancestors = [i.slug for i in ancestors]
        slugs = []
        for i in range(len(ancestors)):
            slugs.append('/'.join(ancestors[:i + 1]))
        return slugs

    def __str__(self):
        return self.name
        # code suspended since it disrupts the auto incrementsing of the count
        # names = self.name
        # ancestors=self.get_ancestors(ascending=True)
        # anc= [i.name for i in ancestors]
        # ancCount=len(anc)
        # if ancCount>1:
        #     for i in range (ancCount-1):
        #         names+= u'.....%s' % anc[i]
        # return names

    @property
    def title_for_admin(self):
        return '%s  [%s]  ' % (self.name, self.count)


class Categorize(models.Model):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,
                          limit_choices_to=CuserMiddleware.get_user())
    poem = models.ForeignKey(Poem, verbose_name='poem', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name='category', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('poet', 'poem', 'category',))
        ordering = ('poem', 'category')
        verbose_name_plural = 'Categorized'

    def __str__(self):
        return ''


@receiver(post_save, sender='collection.Categorize', dispatch_uid='categorize_poem')
def incrementCategoryCount(sender, instance, **kwargs):
    theCat = Category.objects.filter(poet=instance.poet, name=instance.category)[0]
    theCat.count += 1
    theCat.save()
    ancestors = theCat.get_ancestors()
    for anc in ancestors:
        anc.count += 1
        anc.save()
    return


@receiver(post_delete, sender='collection.Categorize', dispatch_uid='de_categorize_poem')
def decrementCategoryCount(sender, instance, **kwargs):
    theCat = Category.objects.filter(poet=instance.poet, name=instance.category)[0]
    theCat.count -= 1
    theCat.save()
    ancestors = theCat.get_ancestors()
    for anc in ancestors:
        anc.count -= 1
        anc.save()
    return


# =================  Note ================================================

class Note(TimeStampModel):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,
                          limit_choices_to=CuserMiddleware.get_user())
    poem = models.ForeignKey(Poem, verbose_name='poem', on_delete=models.CASCADE)
    type = models.CharField('type', choices=NOTE_TYPE_CHOICES, max_length=5, blank=True, null=True)
    subtype = models.CharField('subType', choices=NOTE_SUBTYPE_CHOICES, max_length=5, null=True, blank=True)
    topic = models.CharField('topic', max_length=120, blank=True, null=True)
    content = RichTextField('text', blank=True)

    def __str__(self):
        return ''
    #     identity = ''
    #     theType = self.get_type_display()
    #     theSubtype = self.get_subtype_display()
    #     theTopic = self.topic
    #     if theType is not None: identity = theType
    #     if theSubtype is not None: identity += u' %s' % theSubtype
    #     if theTopic is not None: identity += u': %s' % theTopic
    #     return '  %s - %s' % (self.poem,identity)

#=================  LINK ================================================

class Link(TimeStampModel):
    poem=models.ForeignKey(Poem, verbose_name='poem',on_delete=models.CASCADE, )
    type=models.CharField('type', choices=URL_TYPE_CHOICES, max_length=5, default='docmt')
    url = models.URLField('url')

    class Meta:
        unique_together = ('poem', 'url')

    def __str__(self):
        return ''

    def summary(self):
        cdt = self.created
        cfdt = cdt.strftime(settings.FORMAT_DATETIME)
        mdt = self.updated
        mfdt = mdt.strftime(settings.FORMAT_DATETIME)
        return " {}/n link to {} created {} updated {}".format(self.poem, self.type, cfdt, mfdt)
