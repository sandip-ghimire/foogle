from django.db import models
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class AttributeMixin:
    def save(self, *args, **kwargs):
        extra_attr = None
        if 'extra_attributes' in kwargs:
            extra_attr = kwargs.pop('extra_attributes')
        super().save(*args, **kwargs)
        if extra_attr:
            try:
                for key, val in extra_attr.items():
                    obj, created = Attribute.objects.get_or_create(
                        model_name=self.__class__.__name__, entity_id=self.pk, attr_name=key
                    )
                    obj.attr_value = val
                    obj.save()
            except Exception as e:
                logger.error(f'Failed to save extra attributes {e}')


class Setting(AttributeMixin, models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class File(models.Model):
    settings = models.ForeignKey('Setting', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000)
    file_size = models.IntegerField(default=0)

    def __str__(self):
        return self.settings.name + '_' + self.file_name


class Link(models.Model):
    settings = models.ForeignKey('Setting', on_delete=models.CASCADE)
    url = models.CharField(max_length=500)

    def __str__(self):
        return self.settings.name + '_' + self.url


class Config(models.Model):
    user = models.ForeignKey(User, related_name='config', default=None, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name + ':' + self.value


class Attribute(models.Model):
    model_name = models.CharField(max_length=100)
    entity_id = models.IntegerField()
    attr_name = models.CharField(max_length=100)
    attr_value = models.CharField(max_length=5000, null=True, blank=True)

    def __str__(self):
        return self.model_name + '_' + str(self.entity_id) + '_' + self.attr_name + ':' + self.attr_value
