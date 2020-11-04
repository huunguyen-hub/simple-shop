from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Cart, Profile


def unique_username_generator(instance, new_username=None):
    # user_str = get_first_name(instance.name)
    # In your case
    user_str = instance.username
    if new_username is not None:
        username = new_username
    else:
        user_num = random.randint(1, 391020931223)
        username = '{user_str}_{user_num}'.format(user_num=user_num, user_str=user_str)
    cls = instance.__class__
    qs_exists = cls.objects.filter(username=username).exists()
    if qs_exists:
        user_num = random.randint(1, 391020931223)
        new_username = '{user_str}_{user_num}'.format(user_num=user_num, user_str=user_str)
        return unique_username_generator(instance, new_username=new_username)
    return username


def username_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.username:
        instance.username = unique_username_generator(instance)


pre_save.connect(username_pre_save_receiver, sender=User)


@receiver(post_save, sender=Cart)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


@receiver(post_save, sender=Cart)
def save_user_cart(sender, instance, **kwargs):
    instance.cart.save()


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        Profile.objects.get_or_create(user=kwargs.get('instance'))
