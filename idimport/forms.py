from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
import magic, logging

logger = logging.getLogger(__name__)
logging.basicConfig()

@deconstructible
class FileValidator(object):
    error_messages = {
        'max_size': ("Ensure this file size is not greater than %(max_size)s."
                  " Your file size is %(size)s."),
        'min_size': ("Ensure this file size is not less than %(min_size)s. "
                  "Your file size is %(size)s."),
        'content_type': "Files of type %(content_type)s are not supported.",
    }

    def __init__(self, max_size=None, min_size=None, content_types=()):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            logger.error("file upload - file too large (" + str(data.size) + ")")
            params = {
                'max_size': filesizeformat(self.max_size),
                'size': filesizeformat(data.size),
            }
            raise ValidationError(self.error_messages['max_size'], 'max_size',
                                  params)

        if self.min_size is not None and data.size < self.min_size:
            logger.error("file upload - file too small (" + str(data.size) + ")")
            params = {
                'min_size': filesizeformat(self.mix_size),
                'size': filesizeformat(data.size)
            }
            raise ValidationError(self.error_messages['min_size'], 'min_size',
                                  params)

        if self.content_types:
            content_type = magic.from_buffer(data.read(), mime=True)
            if content_type not in self.content_types:
                logger.error("file upload - content type not allowed (" + content_type + ")")
                params = {'content_type': content_type}
                raise ValidationError(self.error_messages['content_type'],
                                  'content_type', params)

    def __eq__(self, other):
        return isinstance(other, FileValidator)


class CustomerForm(forms.Form):
    name = forms.CharField(label='Customer Name',
                           max_length=100,
                           required=True)


class UploadForm(forms.Form):
    validate_file = FileValidator(max_size=5000000, 
                            content_types=('application/jpg','application/jpeg','application/png',
                                'image/jpg','image/jpeg','image/png'))
    file = forms.FileField(label='Select an image', validators=[validate_file])
