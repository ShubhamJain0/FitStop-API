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

	('Fruits', 'Fruits'),
	('Dried-Fruits', 'Dried-Fruits'),
	('Exotics', 'Exotics'),
	('Banner1', 'Banner1'),
	('Banner2', 'Banner2'),
	('Immuntiy-Booster', 'Immuntiy-Booster'),
	('Other', 'Other'),

	)


SUBSCRIPTION_STATUS = (

	('Active', 'Active'),
	('Expired', 'Expired'),

	)


USER_OPTION = (

	('one', 'one'),
	('two', 'two'),
	('three', 'three'),
	('four', 'four')

	)

ACTIVE_ORDER = (

	('Order Placed', 'Order Placed'),
	('Order Confirmed', 'Order Confirmed'),
	('Out for delivery', 'Out for delivery'),
	('Order Delivered', 'Order Delivered'),
	('Order Cancelled', 'Order Cancelled'),

	)


RECIPE_CATEGORY = (

	('Breakfast', 'Breakfast'),
	('Lunch', 'Lunch'),
	('Dinner', 'Dinner')

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
	phone = models.CharField(unique=True, max_length=10, validators=[RegexValidator(r'^\d{10}$')])
	selected_option = models.CharField(max_length=50, choices=USER_OPTION, null=True)
	image = models.ImageField(upload_to='images/user_profile/', null=True)
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
			provided_otp = otp
		except:
			return False

		t = pyotp.TOTP(self.key, interval=200)
		return t.verify(provided_otp)





class StoreItem(models.Model):

	name = models.CharField(max_length=50)
	description = models.CharField(max_length=255, null=True)
	category = models.CharField(max_length=50, choices=FOOD_CATEGORY, null=True)
	image = models.ImageField(null=True, upload_to='images/store/')
	availability = models.CharField(max_length=255, default='In stock', choices=(('In stock', 'In stock'), ('Out of stock', 'Out of stock')))

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


class VariableItem(models.Model):

	item = models.CharField(max_length=255, null=True)
	quantity = models.CharField(max_length=255, null=True)
	price = models.IntegerField()
	previous_price = models.IntegerField(default=0)



class NutritionalValue(models.Model):

	item = models.CharField(max_length=255, null=True)
	name = models.CharField(max_length=255, null=True)
	value = models.CharField(max_length=255, null=True)



class Address(models.Model):

	address = models.CharField(max_length=255, null=True)
	locality = models.CharField(max_length=255, null=True)
	city = models.CharField(max_length=255, null=True)
	type_of_address = models.CharField(max_length=20)
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
	item_type = models.CharField(max_length=255, null=True)
	price = models.IntegerField()
	weight = models.CharField(max_length=255, null=True)
	ordereddate = models.DateField(default=now)
	orderedtime = models.TimeField(default=now)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)


	def __str__(self):

		return self.ordereditem



class SubscriptionCart(models.Model):

	ordereditem = models.CharField(max_length=200)
	price = models.IntegerField()
	weight = models.CharField(max_length=255, null=True)
	ordereddate = models.DateField(default=now)
	orderedtime = models.TimeField(default=now)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)

	def __str__(self):

		return self.ordereditem



class RecipeSubscriptionCart(models.Model):

	recipe_name = models.CharField(max_length=255, null=True)
	price = models.IntegerField()
	category = models.CharField(max_length=255, null=True, choices=RECIPE_CATEGORY)
	ordereddate = models.DateField(default=now)
	orderedtime = models.TimeField(default=now)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)

	def __str__(self):

		return self.recipe_name



class Order(models.Model):

	ordereditems = models.TextField(null=True)
	ordereddate = models.DateField(default=now)
	orderedtime = models.TimeField(default=now)
	ordered_address = models.CharField(null=True, max_length=255)
	ordered_locality = models.CharField(null=True,max_length=255)
	ordered_city = models.CharField(max_length=255)
	cart_total = models.IntegerField(null=True)
	coupon = models.IntegerField(default=0)
	delivery_charges = models.IntegerField(default=25)
	taxes = models.IntegerField(default=30)
	total_price = models.IntegerField(null=True)
	payment_mode = models.CharField(max_length=255, null=True)
	payment_order_id = models.CharField(max_length=1000, null=True, blank=True)
	transaction_id = models.CharField(max_length=1000, null=True, blank=True)
	payment_authenticity = models.CharField(max_length=100, null=True, blank=True)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)





class PreviousOrder(models.Model):

	ordereddate = models.DateField(default=now)
	orderedtime = models.TimeField(default=now)
	ordered_address = models.CharField(null=True, max_length=255)
	ordered_locality = models.CharField(null=True,max_length=255)
	ordered_city = models.CharField(max_length=255)
	cart_total = models.IntegerField(null=True)
	coupon = models.IntegerField(default=0)
	delivery_charges = models.IntegerField(default=25)
	taxes = models.IntegerField(default=30)
	total_price = models.IntegerField(null=True)
	payment_mode = models.CharField(max_length=255, null=True)
	payment_order_id = models.CharField(max_length=1000, null=True, blank=True)
	transaction_id = models.CharField(max_length=1000, null=True, blank=True)
	payment_authenticity = models.CharField(max_length=100, null=True, blank=True)
	delivery_and_package_rating = models.IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
	delivery_and_package_review = models.CharField(max_length=1000, null=True)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)


class PreviousOrderItems(models.Model):

	id_of_order = models.ForeignKey(PreviousOrder, on_delete=models.CASCADE)
	item_name = models.CharField(max_length=255, null=True)
	item_weight = models.CharField(max_length=255, null=True)
	item_price = models.IntegerField()
	item_count = models.IntegerField()
	user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)




class ActiveOrder(models.Model):

	order_number = models.IntegerField(null=True)
	order_status = models.CharField(default='Order Placed', max_length=255, choices=ACTIVE_ORDER)
	user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
	push_token = models.CharField(null=True, max_length=255, blank=True)




class Subscription(models.Model):

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		)
	subscription_plan = models.CharField(null=True, max_length=255)
	subscription_type = models.CharField(null=True, max_length=255)
	startdate = models.DateField(default=now)
	starttime = models.TimeField(default=now)
	enddate = models.DateField(null=True)
	subscription_status = models.CharField(default='Active', max_length=255, choices=SUBSCRIPTION_STATUS)
	push_token = models.CharField(null=True, max_length=255, blank=True)
	ordereditems = models.TextField(null=True)
	cart_total = models.IntegerField(null=True)
	coupon = models.IntegerField(default=0)
	delivery_charges = models.IntegerField(default=25)
	taxes = models.IntegerField(default=30)
	total_subscription_price = models.IntegerField(null=True)
	delivery_address = models.CharField(null=True, max_length=255)
	delivery_locality = models.CharField(null=True,max_length=255)
	delivery_city = models.CharField(max_length=255)
	payment_mode = models.CharField(max_length=255, null=True)
	payment_order_id = models.CharField(max_length=1000, null=True, blank=True)
	transaction_id = models.CharField(max_length=1000, null=True, blank=True)
	payment_authenticity = models.CharField(max_length=100, null=True, blank=True)



class SubscriptionItems(models.Model):

	id_of_subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
	item_name = models.CharField(max_length=255, null=True)
	item_weight = models.CharField(max_length=255, null=True)
	item_price = models.IntegerField()
	item_count = models.IntegerField()
	user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)



class SubscriptionRecipeItems(models.Model):

	 id_of_subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
	 recipe_name = models.CharField(max_length=255, null=True)
	 recipe_price = models.IntegerField()
	 category = models.CharField(max_length=255, null=True)
	 user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)




class Rating(models.Model):

	stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
	review = models.CharField(max_length=1000, blank=True)
	item = models.CharField(max_length=255, null=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	class Meta:

		unique_together = (('user', 'item'),)
		index_together = (('user', 'item'),)



class Recipe(models.Model):

	name = models.CharField(max_length=50, blank=True)
	price = models.IntegerField(default=0)
	category = models.CharField(max_length=255, null=True, choices=RECIPE_CATEGORY)
	description = models.CharField(max_length=5000, blank=True)
	steps = models.TextField(null=True)
	servings = models.IntegerField(default=0)
	name1 = models.CharField(max_length=255, null=True)
	value1 = models.CharField(max_length=255, null=True)
	name2 = models.CharField(max_length=255, null=True)
	value2 = models.CharField(max_length=255, null=True)
	name3 = models.CharField(max_length=255, null=True)
	value3 = models.CharField(max_length=255, null=True)
	name4 = models.CharField(max_length=255, null=True)
	value4 = models.CharField(max_length=255, null=True)
	name5 = models.CharField(max_length=255, null=True)
	value5 = models.CharField(max_length=255, null=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='images/recipe/', null=True)

	def __str__(self):
		return self.name



class RecipeIngredients(models.Model):

	id_of_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	name = models.CharField(max_length=255, null=True)
	weight = models.CharField(max_length=255, null=True)
	price = models.IntegerField()
	count = models.IntegerField(default=1)
	show_weight_in_recipe = models.CharField(max_length=255, null=True)
	image = models.ImageField(upload_to='images/RecipeIngredients/', blank=True, null=True)



class FavRecipe(models.Model):

	id_of_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)



class HomeBanner(models.Model):

	image = models.ImageField(upload_to='images/banner/')




class PushNotificationsToken(models.Model):

	token = models.CharField(null=True, max_length=500)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)



class Coupon(models.Model):

	name = models.CharField(max_length=255, null=True)
	description = models.CharField(max_length=255, null=True)
	discount = models.IntegerField(default=0)
	min_items_price = models.IntegerField(default=0)
	user = models.ManyToManyField(CustomUserModel)