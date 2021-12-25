from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import (Sum, Count)

from api.models import (StoreItem, Address, Cart, PreviousOrder, DeliveryAddressId, Rating, Recipe, HomeBanner, 
	PushNotificationsToken, Coupon, ActiveOrder, Order, VariableItem, PreviousOrderItems, 
	RecipeIngredients, NutritionalValue, FavRecipe, Subscription, SubscriptionItems, SubscriptionCart, RecipeSubscriptionCart,
	SubscriptionRecipeItems)

User = get_user_model()





class StoreItemSerializer(serializers.ModelSerializer):
	detail = serializers.SerializerMethodField(read_only=True)
	nutritional_values = serializers.SerializerMethodField(read_only=True)
	class Meta:

		model = StoreItem
		fields = ['id', 'name', 'description', 'availability', 'detail', 'nutritional_values', 'image', 'no_of_ratings', 'avg_ratings', 'category']

	def get_detail(self, name):
		return VariableItem.objects.filter(item=name).values('price', 'previous_price', 'quantity', 'item', 'id')

	def get_nutritional_values(self, name):
		return NutritionalValue.objects.filter(item=name).values('id', 'name', 'value')





class VariableItemSerializer(serializers.ModelSerializer):
	class Meta:

		model = VariableItem
		fields = '__all__'




class NutritionalValueSerializer(serializers.ModelSerializer):
	class Meta:

		model = NutritionalValue
		fields = '__all__'



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
		fields = ['id', 'ordereditem', 'price', 'item_count', 'weight']


	def get_item_count(self, ordereditem):
		return Cart.objects.filter(ordereditem=ordereditem, user=self.context['request'].user).count()





class OrderSerializer(serializers.ModelSerializer):
	class Meta:

		model = Order
		fields = ['id', 'ordereditems', 'ordereddate', 'cart_total', 'coupon', 'delivery_charges', 'taxes', 'total_price', 
					'payment_mode', 'ordered_address', 'ordered_locality', 'ordered_city']




class PreviousOrderSerializer(serializers.ModelSerializer):
	class Meta:

		model = PreviousOrder
		fields = ['id', 'ordereddate', 'cart_total', 'coupon', 'delivery_charges', 'taxes', 'total_price', 'payment_mode',
					'ordered_address', 'ordered_locality', 'ordered_city', 'delivery_and_package_rating', 'delivery_and_package_review']


class PreviousOrderItemsSerializer(serializers.ModelSerializer):
	class Meta:

		model = PreviousOrderItems
		fields = ['id', 'id_of_order', 'item_name', 'item_weight', 'item_price', 'item_count']




class RatingSerializer(serializers.ModelSerializer):
	user = serializers.StringRelatedField()
	item = serializers.StringRelatedField(many=False)
	class Meta:

		model = Rating
		fields = ['id', 'item', 'stars', 'review', 'user']



class RecipeSerializer(serializers.ModelSerializer):
	user = serializers.StringRelatedField()
	count = serializers.SerializerMethodField()
	ingredient_count = serializers.SerializerMethodField()
	class Meta:

		model = Recipe
		fields = ['id', 'name', 'price', 'category', 'description', 'steps', 'image', 'user', 'name1', 'value1', 'name2', 'value2'
					, 'name3', 'value3', 'name4', 'value4', 'name5', 'value5', 'count', 'servings', 'ingredient_count']

	def create(self, validated_data):

		return Recipe.objects.create(**validated_data)


	def get_count(self, obj):
		return FavRecipe.objects.filter(id_of_recipe=obj.id).count()

	def get_ingredient_count(self, obj):
		return RecipeIngredients.objects.filter(id_of_recipe=obj.id).count()

class RecipeIngredientsSerializer(serializers.ModelSerializer):
	class Meta:

		model = RecipeIngredients
		fields = '__all__'



class FavRecipeSerializer(serializers.ModelSerializer):
	class Meta:

		model = FavRecipe
		fields = '__all__'



class HomeBannerSerializer(serializers.ModelSerializer):
	class Meta:

		model = HomeBanner
		fields = ['id', 'image']



class PushNotificationsTokenSerializer(serializers.ModelSerializer):
	class Meta: 

		model = PushNotificationsToken
		fields = '__all__'


class CouponSerializer(serializers.ModelSerializer):
	class Meta:

		model = Coupon
		fields = ['id', 'name', 'description', 'discount', 'min_items_price']



class ActiveOrderSerializer(serializers.ModelSerializer):
	class Meta:

		model = ActiveOrder
		fields = ['id', 'order_number', 'order_status', 'push_token', 'user']



class SubscriptionCartSerializer(serializers.ModelSerializer):

	item_count = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = SubscriptionCart
		fields = ['id', 'ordereditem', 'price', 'item_count', 'weight']

	def get_item_count(self, ordereditem):
		return SubscriptionCart.objects.filter(ordereditem=ordereditem, user=self.context['request'].user).count()




class RecipeSubscriptionCartSerializer(serializers.ModelSerializer):

	item_count = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = RecipeSubscriptionCart
		fields = ['id', 'recipe_name', 'price', 'category', 'item_count']

	def get_item_count(self, recipe_name):
		return RecipeSubscriptionCart.objects.filter(recipe_name=recipe_name, user=self.context['request'].user).count()



class SubscriptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subscription
		fields = '__all__'


class SubscriptionItemsSerializer(serializers.ModelSerializer):
	class Meta:
		model = SubscriptionItems
		fields = '__all__'



class SubscriptionRecipeItemsSerializer(serializers.ModelSerializer):
	class Meta:
		model = SubscriptionRecipeItems
		fields = '__all__'