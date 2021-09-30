import os
from urllib.parse import unquote

from cuser.middleware import CuserMiddleware
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _
from PIL import Image


def uploadValidator(value):
    return value

def uploadTextFileValidator(value):
    if value.name=='' or value.name is None: return
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != ".txt":
        raise ValidationError(u"This is not a titles document.")
    elif value.size > 1048576:
        raise ValidationError("The maximum document size that can be uploaded is 1MB")
    else:
        return value

def uploadImageFileValidator(value):
    if value.name == '' or value.name is None: return
    width, height = get_image_dimensions(value)
    size=value.size
    if size > 40960:
        raise ValidationError("The maximum image size that can be uploaded is 40KB")
    elif height > 128:
        raise ValidationError("The maximum image height is 128px")
    elif width > 128:
        raise ValidationError("The maximum image width is 128px")
    else:
        return value

def dropBoxDocValidator(aURL):
    dropBoxValidator(aURL, True)

def dropBoxExeValidator(aURL):
    dropBoxValidator(aURL, False)

def dropBoxValidator(aURL,doc):
    value=unquote(aURL)
    if value:  # there is a string and it's not empty
        lv=value.lower()
        # check for valid document type
        if doc:
            extensions=('.txt', '.rtf', '.pdf', '.doc', '.docx', '.odt', '.pages','')
        else:
            extensions = ('.exe',)
        if not any(extn in lv for extn in extensions):
            raise ValidationError(_('%(value)s does not reference a valid document type. The file reference part of the URL requires a:  %(extensions)s extension'),
                                  params={'value': value, 'extensions': extensions},
                                  code='invalid', )
        # check for DROPBOX
        if not 'dropbox' in lv:
            raise ValidationError(_('%(value)s does not reference a dropbox file'), params={'value': value,}, code='invalid', )

        # =check for valid URL
        if not isValidURL(aURL):
            raise ValidationError(_('%(value)s is not a valid URL'), params={'value': value,}, code='invalid', )


def isValidURL(url):
    validate = URLValidator()
    try:
        validate(url)
        return True
    except ValidationError:
        return False




