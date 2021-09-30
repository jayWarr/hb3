from cuser.middleware import CuserMiddleware
from django.db import models
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey
from isbn_field import ISBNField

from collection.models import Poem
from core.choices import COUNTRIES, PP_CHOICES, PUBLICATION_CHOICES
from core.models import TimeStampModel

# =================  PUBLISHER ==========================================

class Publisher(models.Model):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,limit_choices_to=CuserMiddleware.get_user())
    name = models.CharField('Publisher', max_length=80, unique=True)
    url = models.URLField('url', blank=True)
    access = models.CharField('access', max_length=7,default='Public', editable=False, choices=PP_CHOICES,help_text="Publisherp access - default is public, alternative is private")
    country = models.CharField('country', max_length=3, choices=COUNTRIES, default='GBR')

    class Meta:
        ordering = (('name',))

    def __str__(self):
        return self.name

# =================  PUBLICATION ========================================

class Publication(models.Model):
    poet = UserForeignKey(auto_user_add=True, on_delete=models.CASCADE, editable=False,limit_choices_to=CuserMiddleware.get_user())
    publisher=models.ForeignKey(Publisher,verbose_name='publisher',on_delete=models.CASCADE)
    name = models.CharField('Publication', max_length=80, unique=True)
    contents = models.ManyToManyField(Poem, through='Content')
    type = models.PositiveIntegerField('type', choices=PUBLICATION_CHOICES)
    publishedOn = models.DateField('published on',default=timezone.now)
    isbn = ISBNField('ISBN',max_length=17, blank=True, default='')

    class Meta:
        ordering = (('name'),('type'),('publisher'),)

    def __str__(self):
        for pc in PUBLICATION_CHOICES:
            n,pt = pc
            if n==self.type:
                pubType=pt
        thePublisher=Publisher.objects.get(id=self.publisher_id).name
        return u"the %s '%s' published by %s" % (pubType, self.name, thePublisher)
        # return ''


# =================  CONTENT ========================================

class Content(TimeStampModel):
    publication=models.ForeignKey(Publication, verbose_name='publication',on_delete=models.CASCADE)
    poem=models.ForeignKey(Poem, verbose_name='poem',on_delete=models.CASCADE)

    class Meta:
        ordering = (('publication'),('poem'),)
        unique_together = ('publication','poem')

    def save(self, *args, **kwargs):
        if self.pk is None: # new submission counts & status for the poem
            user=CuserMiddleware.get_user()
            thePoem = Poem.objects.get(title=self.poem, poet=user)
            thePoem.niP += 1
            thePoem.dtlu=timezone.now()
            thePoem.save()
        super(Content, self).save(*args, **kwargs)

    def __str__(self):
        return ''
        # return u'%s as content for' % (self.poem)

    def delete(self, *args, **kwargs):
        thePoem=Poem.objects.get(self.poem_id)
        thePoem.niP -=1
        thePoem.save()
        super(Content, self).delete(*args, **kwargs)
