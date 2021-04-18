from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import (Sum, Count)

from api.models import (StoreItem, Address, Cart, PreviousOrder, DeliveryAddressId, Rating, Recipe, HomeBanner, 
	ItemsData, DetailsImage, PushNotificationsToken)

User = get_user_model()





class StoreItemSerializer(serializers.ModelSerializer):

	class Meta:

		model = StoreItem
		fields = ['id', 'name', 'description','price', 'image', 'no_of_ratings', 'avg_ratings']



class DetailsImageSerializer(serializers.ModelSerializer):
	class Meta:

		model = DetailsImage
		fields = ['id', 'image', 'item']


class AddressBookSerializer(serializers.ModelSerializer):

	class Meta:

		model = Address
		fields = ['id', 'address', 'locality', 'city', 'type_of_address']




class DeliveryAddressIdSerializer(serializers.ModelSerializer):
	class Meta:

		model = DeliveryAddressId
		fields = ['address_id']


	def create(self, validated_data):
		
		DeliveryAddressId.objects.filter(user=self.context['request'].user).delete()
		new = DeliveryAddressId.objects.create(**validated_data, user=self.context['request'].user)
		new.save()

		return new




class CartSerializer(serializers.ModelSerializer):

	item_count = serializers.SerializerMethodField(read_only=True)

	class Meta:

		model = Cart
		fields = ['id', 'ordereditem', 'price', 'item_count']


	def get_item_count(self, ordereditem):
		return Cart.objects.filter(ordereditem=ordereditem, user=self.context['request'].user).count()




class ItemsDataSerializer(serializers.ModelSerializer):
	class Meta:

		model = ItemsData
		fields = '__all__'




class PreviousOrderSerializer(serializers.ModelSerializer):
	ordereditem = serializers.StringRelatedField(many=True)
	class Meta:

		model = PreviousOrder
		fields = ['id', 'ordereditem', 'ordereddate', 'price']




class RatingSerializer(serializers.ModelSerializer):
	user = serializers.StringRelatedField()
	item = serializers.StringRelatedField(many=False)
	class Meta:

		model = Rating
		fields = ['id', 'item', 'stars', 'review', 'user']



class RecipeSerializer(serializers.ModelSerializer):
	store_item = serializers.StringRelatedField()
	user = serializers.StringRelatedField()
	class Meta:

		model = Recipe
		fields = ['name', 'ingredients', 'description', 'image', 'store_item', 'user']

	def create(self, validated_data):

		return Recipe.objects.create(**validated_data)



class HomeBannerSerializer(serializers.ModelSerializer):
	class Meta:

		model = HomeBanner
		fields = ['id', 'image']


class PushNotificationsTokenSerializer(serializers.ModelSerializer):
	class Meta: 

		model = PushNotificationsToken
		fields = '__all__'