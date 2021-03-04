from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUserModel
import pyotp


def generate_key():
	"""User otp key generator"""
	key = pyotp.random_base32()
	if is_unique(key):
		return key
	generate_key()


def is_unique(key):
	try:
		CustomUserModel.objects.get(key=key)
	except CustomUserModel.DoesNotExist:
		return True
	return False


@receiver(pre_save, sender=CustomUserModel)
def create_key(sender, instance, **kwargs):
	"""This creates the key for users that don't have keys"""
	if not instance.key:
		instance.key = generate_key()