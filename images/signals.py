from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Image


@receiver(m2m_changed, sender=Image.users_like.through)
def users_likes(sender, instance, **kwargs):
    """
    Signal user likes
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    instance.total_likes = instance.users_like.count()
    instance.save()
