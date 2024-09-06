import requests
from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Image


class ImageCreateForm(forms.ModelForm):
    class Meta:
        """
        Meta class to define the model and fields to include in the form
        """
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput,
        }

    def clean_url(self):
        """
        Clean the url field
        :return:
        """
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL does not match valid image extensions.')
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        """
        Save Image
        :param force_insert:
        :param force_update:
        :param commit
        :return:
        """
        image = super().save(commit=False)
        image_ulr = self.cleaned_data['url']
        name = slugify(image.title)
        extension = image_ulr.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        response = requests.get(image_ulr)
        image.image.save(
            image_name,
            ContentFile(response.content),
            save=False
        )
        if commit:
            image.save()
        return image
