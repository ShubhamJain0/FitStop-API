from django.db import models
from django.conf import settings
from django.utils.timezone import now

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
import pyotp
import os
import uuid
# Create your models here.


FOOD_CATEGORY = (

	('Category1', 'Category1'),
	('Category2', 'Category2'),

	)


ADDRESS_TYPE = (

	('Home', 'Home'),
	('Work', 'Work'),
	('Other', 'Other')

	)







class CustomUserModelManager(BaseUserManager):

	def create_user(self, phone, password=None, **extra_fields):

		if not phone:
			raise ValueError('Phone number is needed!')

		user = self.model(phone=phone, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)

		return user


	def create_superuser(self, phone, password, **extra_fields):

		user = self.create_user(phone, password)
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)

		return user








class CustomUserModel(AbstractBaseUser, PermissionsMixin):

	email = models.EmailField(unique=True, max_length=255, null=True)
	name = models.CharField(null=True, max_length=255)
	phone = models.CharField(unique=True, null=True, max_length=15)
	key = models.CharField(max_length=100, blank=True)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)

	objects = CustomUserModelManager()

	USERNAME_FIELD = 'phone'

	def __str__(self):

		return self.phone


	def authenticate(self, otp):
		"""This method authenticates the otp"""
		provided_otp = 0
		try:
			provided_otp = int(otp)
		except:
			return False

		t = pyotp.TOTP(self.key, interval=300)
		return t.verify(provided_otp)



class InactiveUserId(models.Model):

	id_of_user = models.IntegerField()
	otp_code = models.IntegerField(null=True)




class ResetPassUserId(models.Model):

	reset_user_id = models.IntegerField()
	reset_code = models.IntegerField()





class StoreItem(models.Model):

	name = models.CharField(max_length=50)
	description = models.CharField(max_length=50, null=True)
	category = models.CharField(max_length=50, choices=FOOD_CATEGORY)
	price = models.IntegerField()
	image = models.ImageField(null=True, upload_to='images/')

	def __str__(self):

		return self.name

	def no_of_ratings(self):
		ratings = Rating.objects.filter(item=self)
		return len(ratings)


	def avg_ratings(self):
		ratings = Rating.objects.filter(item=self)
		sum_of_stars = 0

		for rating in ratings:
			sum_of_stars += rating.stars

		if len(ratings) > 0:
			return sum_of_stars / len(ratings)
		else:
			return 0



class Address(models.Model):

	address = models.CharField(max_length=50, null=True)
	locality = models.CharField(max_length=20, null=True)
	city = models.CharField(max_length=30, null=True)
	type_of_address = models.CharField(max_length=20, choices=ADDRESS_TYPE)
	user = models.ForeignKey(
			settings.AUTH_USER_MODEL,
			on_delete=models.CASCADE
		)


	REQUIRED_FIELDS = ['address', 'city', 'locality', 'type_of_address']




class DeliveryAddressId(models.Model):

	address_id = models.IntegerField()
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)








class Cart(models.Model):

	ordereditem = models.CharField(max_length=200)
	price = models.IntegerField()
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)


	def __str__(self):

		return self.ordereditem





class Order(models.Model):

	ordereditem = models.ManyToManyField(Cart)
	ordereddate = models.DateField(default=now)
	orderedtime = models.TimeField(default=now)
	ordered_address = models.CharField(null=True, max_length=15)
	ordered_locality = models.CharField(null=True,max_length=255)
	ordered_city = models.CharField(max_length=255)
	total_price = models.IntegerField(null=True)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)





class PreviousOrder(models.Model):

	ordereditem = models.ManyToManyField(Cart)
	ordereddate = models.DateField(default=now)
	orderedtime = models.TimeField(default=now)
	ordered_address = models.CharField(null=True, max_length=15)
	ordered_locality = models.CharField(null=True,max_length=255)
	ordered_city = models.CharField(max_length=255)
	price = models.IntegerField(null=True)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)


class Rating(models.Model):

	stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
	review = models.CharField(max_length=255, blank=True)
	item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	class Meta:

		unique_together = (('user', 'item'),)
		index_together = (('user', 'item'),)



class Recipe(models.Model):

	name = models.CharField(max_length=50, blank=True)
	ingredients = models.CharField(max_length=100)
	description = models.CharField(max_length=5000, blank=True)
	store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='images/recipe/')