from django.db.models.signals import (pre_save, post_save)
from django.dispatch import receiver
from .models import CustomUserModel, ActiveOrder
from store.views import send_push_message
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



@receiver(post_save, sender=ActiveOrder)
def sendNotification(sender, instance, **kwargs):

	try:
		ActiveOrder.objects.get(id=instance.id)

		if instance.order_status == 'Order Placed' and instance.push_token:
			send_push_message(instance.push_token, 'Order has been placed successfully!', 'Order Status', {'screen': 'ActiveOrders', 'item_id': instance.order_number})
		elif instance.order_status == 'Order Confirmed' and instance.push_token:
			send_push_message(instance.push_token, 'Your order has been confirmed and will be delivered soon!', 'Order Status', {'screen': 'ActiveOrders', 'item_id': instance.order_number})
		elif instance.order_status == 'Out for delivery' and instance.push_token:
			send_push_message(instance.push_token, 'Order is out for delivery', 'Order Status', {'screen': 'ActiveOrders', 'item_id': instance.order_number})
		elif instance.order_status == 'Order Delivered' and instance.push_token:
			send_push_message(instance.push_token, 'Order has been delivered successfully!', 'Order Status', {'screen': 'Home'})
			instance.delete()
		elif instance.order_status == 'Order Delivered' and not instance.push_token:
			instance.delete()
		elif instance.order_status == 'Order Cancelled' and instance.push_token:
			send_push_message(instance.push_token, 'Your order has been cancelled and amount will be refunded at earliest, if any', 'Order Status', {'screen': 'ActiveOrders'})

	except ActiveOrder.DoesNotExist:
		return