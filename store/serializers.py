from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.models import StoreItem, Address, Cart, PreviousOrder

User = get_user_model()

class StoreItemSerializer(serializers.ModelSerializer):

	class Meta:

		model = StoreItem
		fields = ['name', 'description','price', 'image']


class AddressBookSerializer(serializers.ModelSerializer):

	class Meta:

		model = Address
		fields = ['address', 'locality', 'city', 'type_of_address']


	def create(self, validated_data):

		new = Address.objects.create(**validated_data, user=self.context['request'].user)
		new.save()

		return new




class CartSerializer(serializers.ModelSerializer):

	item_count = serializers.SerializerMethodField(read_only=True)

	class Meta:

		model = Cart
		fields = ['ordereditem', 'price', 'item_count']

	def create(self, validated_data):

		new = Cart.objects.create(**validated_data, user=self.context['request'].user)
		new.save()

		return new


	def get_item_count(self, ordereditem):
		return Cart.objects.filter(ordereditem=ordereditem, user=self.context['request'].user).count()



class PreviousOrderSerializer(serializers.ModelSerializer):
	class Meta:

		model = PreviousOrder
		fields = ['ordereditem', 'ordereddate', 'price']


