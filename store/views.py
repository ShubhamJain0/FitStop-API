from django.shortcuts import render
from store.serializers import (StoreItemSerializer, AddressBookSerializer, CartSerializer, PreviousOrderSerializer, 
	DeliveryAddressIdSerializer, RatingSerializer, RecipeSerializer, HomeBannerSerializer, DetailsImageSerializer, 
	PushNotificationsTokenSerializer, HomeProductsSerializer, CouponSerializer, ActiveOrderSerializer, OrderSerializer,
	PreviousOrderItemsSerializer, RecipeIngredientsSerializer, FavRecipeSerializer, NutritionalValueSerializer)
from api.models import (StoreItem, Address, Cart, Order, PreviousOrder, Rating, Recipe, HomeBanner, CustomUserModel, 
	DetailsImage, PushNotificationsToken, HomeProducts, Coupon, ActiveOrder, VariableItem, PreviousOrderItems, 
	RecipeIngredients, FavRecipe, DeliveryAddressId, NutritionalValue)

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import (Sum, Count)
from django.core.serializers import serialize

from rest_framework import viewsets, status, generics, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
) 
from requests.exceptions import ConnectionError, HTTPError

import re

# Create your views here.

User = get_user_model()




def send_push_message(token, message, title, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        title=title,
                        data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': extra})
        raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        PushNotificationsToken.objects.get(token=token).delete()
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            })
        raise self.retry(exc=exc)



def send_bulk_push_message(message, title, extra=None):

	qs = PushNotificationsToken.objects.all()
	for i in qs:
	    try:
	        response = PushClient().publish(
	            PushMessage(to=i.token,
	                        body=message,
	                        title=title,
	                        data=extra))
	    except PushServerError as exc:
	        # Encountered some likely formatting/validation error.
	        rollbar.report_exc_info(
	            extra_data={
	                'token': i.token,
	                'message': message,
	                'extra': extra,
	                'errors': exc.errors,
	                'response_data': exc.response_data,
	            })
	        raise
	    except (ConnectionError, HTTPError) as exc:
	        # Encountered some Connection or HTTP error - retry a few times in
	        # case it is transient.
	        rollbar.report_exc_info(
	            extra_data={'token': i.token, 'message': message, 'extra': extra})
	        raise self.retry(exc=exc)

	    try:
	        # We got a response back, but we don't know whether it's an error yet.
	        # This call raises errors so we can handle them with normal exception
	        # flows.
	        response.validate_response()
	    except DeviceNotRegisteredError:
	        # Mark the push token as inactive
	        PushNotificationsToken.objects.get(token=i.token).delete()
	    except PushTicketError as exc:
	        # Encountered some other per-notification error.
	        rollbar.report_exc_info(
	            extra_data={
	                'token': i.token,
	                'message': message,
	                'extra': extra,
	                'push_response': exc.push_response._asdict(),
	            })
	        raise self.retry(exc=exc)










class StoreItems(generics.ListAPIView):
	queryset = StoreItem.objects.all()
	serializer_class = StoreItemSerializer


class StoreItemsFruitsList(generics.ListAPIView):

	queryset = StoreItem.objects.filter(category='Fruits').order_by('name')
	serializer_class = StoreItemSerializer


class StoreItemsDriedFruitsList(generics.ListAPIView):

	queryset = StoreItem.objects.filter(category='Dried-Fruits').order_by('name')
	serializer_class = StoreItemSerializer


class StoreItemsExoticsList(generics.ListAPIView):

	queryset = StoreItem.objects.filter(category='Exotics').order_by('name')
	serializer_class = StoreItemSerializer




class AddressBook(viewsets.ModelViewSet):

	queryset = Address.objects.all()
	serializer_class = AddressBookSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get_queryset(self):

		queryset = self.queryset
		qs = queryset.filter(user=self.request.user)

		if qs:
			return qs
		raise NotFound({"message": "You don't have any saved address."})



	def create(self, request):

		address = request.data['address']
		locality = request.data['locality']
		city = request.data['city']
		type_of_address = request.data['type_of_address']
		new = Address.objects.create(address=address, locality=locality, city=city, type_of_address=type_of_address, user=request.user)
		new.save()
		DeliveryAddressId.objects.filter(user=request.user).delete()
		qs = Address.objects.filter(user=request.user)
		serializer = AddressBookSerializer(qs, many=True)
		DeliveryAddressId.objects.create(user=request.user, address_id=new.id)
		qs2 = Address.objects.filter(id=new.id, user=request.user)
		get_delivery_address = AddressBookSerializer(qs2, many=True)

		return Response({'data': serializer.data, 'delivery_address': get_delivery_address.data}, status=200)


	def delete(self, request):

		get_id = request.data['address_id']
		Address.objects.filter(user=request.user, id=get_id).delete()
		delivery_address_present = 200
		if DeliveryAddressId.objects.filter(user=request.user):
			try:
				DeliveryAddressId.objects.get(user=request.user, address_id=get_id).delete()
				delivery_address_present = 404
			except:
				pass
		else:
			delivery_address_present = 404
		qs = Address.objects.filter(user=request.user)
		if qs:
			serializer = AddressBookSerializer(qs, many=True)
			return Response({'data': serializer.data, 'deliveryaddstatus': delivery_address_present}, status=200)
		else:
			serializer = AddressBookSerializer(qs, many=True)
			return Response({'data': serializer.data, 'deliveryaddstatus': delivery_address_present}, status=404)




class DeliveryAddressIdView(generics.CreateAPIView):

	serializer_class = DeliveryAddressIdSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getDeliveryAddress(request):

	if DeliveryAddressId.objects.filter(user=request.user):
		get_delivery_address_id = DeliveryAddressId.objects.filter(user=request.user).values('address_id')
		get_address = Address.objects.filter(user=request.user, id__in=get_delivery_address_id)
		serializer = AddressBookSerializer(get_address, many=True, context={'request': request})
		return Response({'address': serializer.data}, status=200)
	else:
		return Response({'message':'No address found'}, status=404)



class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
	 queryset = Cart.objects.all()
	 serializer_class = CartSerializer
	 authentication_classes = (TokenAuthentication, )
	 permission_classes = (IsAuthenticated, )


	 def get_queryset(self):
	 	queryset = self.queryset
	 	qs = queryset.filter(user=self.request.user).distinct('ordereditem')

	 	if qs:
	 		return qs
	 	else:
	 		raise NotFound({'message':'cart is empty!'})


	 def delete(self, request):
	 	Cart.objects.filter(user=self.request.user).delete()
	 	return Response({'message': 'Deleted'}, status=200)


	 def create(self, request, *args, **kwargs):

	 	item = request.data['ordereditem']
	 	quantity = request.data['quantity']
	 	get_price = VariableItem.objects.filter(item=item['name'], quantity=quantity).values('price')
	 	Cart.objects.create(ordereditem=item['name'], price=get_price[0]['price'], weight=quantity, user=request.user)
	 	qs = Cart.objects.filter(user=request.user).distinct('ordereditem')
	 	serializer = CartSerializer(qs, many=True, context={'request': request})
	 	return Response({'cart': serializer.data}, status=201)




@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def CartReduceItemOrDeleteItem(request):

	if request.method == "POST":

		item = request.data['reduceitem']
		Cart.objects.filter(pk__in=Cart.objects.filter(user=request.user, ordereditem=item['name']).\
			values_list('id', flat=True)[0:1]).delete()
		qs = Cart.objects.filter(user=request.user).distinct('ordereditem')
		serializer = CartSerializer(qs, many=True, context={'request': request})

		return Response({'message': 'done', 'cart': serializer.data}, status=200)

	if request.method == 'DELETE':

		delete_item = request.data['item']
		Cart.objects.filter(user=request.user, ordereditem=delete_item['ordereditem']).delete()
		qs = Cart.objects.filter(user=request.user).distinct('ordereditem')
		qs2 = StoreItem.objects.all().distinct('name')
		serializer = StoreItemSerializer(qs2, many=True, context={'request': request})
		total_price = Cart.objects.filter(user=request.user).aggregate(Sum('price'))

		data = [{'id': i.id, 'ordereditem': i.ordereditem, 'count': Cart.objects.filter(ordereditem=i.ordereditem, user=request.user).count(), 
				'items_price': Cart.objects.filter(ordereditem=i.ordereditem, user=request.user).aggregate(Sum('price'))} for i in qs]
				
		return Response({'items': data, 'total': total_price['price__sum'], 'photos': serializer.data}, status=200)





@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def PlaceOrder(request):

	if request.method == 'POST':

		if Cart.objects.filter(user=request.user):

			address = DeliveryAddressId.objects.filter(user=request.user).values('address_id')
			get_address = Address.objects.get(user=request.user, id__in=address)
			cart_total = request.data['cart_total']
			coupon = request.data['coupon']
			delivery_charges = request.data['delivery_charges']
			taxes = request.data['taxes']
			total_price = request.data['total_price']
			payment_mode = request.data['payment']
			get_pushtoken = request.data['pushToken']

			get_date = Cart.objects.filter(user=request.user).values_list('ordereddate', flat=True)
			get_time = Cart.objects.filter(user=request.user).values_list('orderedtime', flat=True)

			get_cart = Cart.objects.filter(user=request.user).distinct('ordereditem', 'weight')
			ordereditems = []

			for i in get_cart:
				get_items = Cart.objects.filter(ordereditem=i.ordereditem, user=request.user, weight=i.weight).values('ordereditem', 'weight').annotate(count=Count('ordereditem'))
				ordereditems.append((get_items[0]['ordereditem'] + ' w' + get_items[0]['weight'] + ' x' + str(get_items[0]['count']) + ', '))

			qs = Order.objects.create(user=request.user, ordereditems=ordereditems, cart_total=cart_total, coupon=coupon, 
				delivery_charges=delivery_charges, taxes=taxes, total_price=total_price, payment_mode=payment_mode, ordered_address=get_address.address, 
				ordered_locality=get_address.locality, ordered_city=get_address.city)
			qs2 = PreviousOrder.objects.create(user=request.user, cart_total=cart_total, coupon=coupon, delivery_charges=delivery_charges, 
				taxes=taxes, total_price=total_price, payment_mode=payment_mode, ordered_address=get_address.address, ordered_locality=get_address.locality, 
				ordered_city=get_address.city)

			for i in get_cart:
				data = Cart.objects.filter(ordereditem=i.ordereditem, weight=i.weight, price=i.price, user=request.user).values('ordereditem', 'weight', 'price').annotate(count=Count('ordereditem'))
				PreviousOrderItems.objects.create(id_of_order=qs2, item_name=data[0]['ordereditem'], item_weight=data[0]['weight'], item_price=data[0]['price'], item_count=data[0]['count'], user=request.user)

			ActiveOrder.objects.create(order_number=qs.id, user=request.user, push_token=get_pushtoken)
			Cart.objects.filter(user=request.user).delete()

			return Response({'message': 'Placed Succesfully'}, status=201)
		else:
			return Response({'message': 'Cart is empty'}, status=400)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ActiveOrderView(request):

	get_active_orders = ActiveOrder.objects.filter(user=request.user).values_list('order_number', flat=True)
	qs = Order.objects.filter(id__in=get_active_orders, user=request.user).order_by('-id')
	qs2 = ActiveOrder.objects.filter(user=request.user)
	serializer = OrderSerializer(qs, many=True)
	serializer1 = ActiveOrderSerializer(qs2, many=True)

	if qs:
		return Response({'data': serializer.data, 'orderstatus': serializer1.data}, status=200)
	else:
		raise NotFound('No active orders!')



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def PreviousOrderView(request):

	qs = PreviousOrder.objects.filter(user=request.user).order_by('-id')
	qs1 = [{'items': PreviousOrderItems.objects.filter(id_of_order=i.id, user=request.user).values('id', 'id_of_order', 'item_name', 'item_weight', 'item_count')} for i in qs]
	serializer = PreviousOrderSerializer(qs, many=True)
	qs2 = StoreItem.objects.all()
	serializer2 = StoreItemSerializer(qs2, many=True, context={'request': request})

	if qs:
		return Response({'qs': serializer.data, 'data': qs1, 'images': serializer2.data})
	else:
		raise NotFound('Not Found')




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ConfirmOrder(request): 
	if Cart.objects.filter(user=request.user):
		qs = Cart.objects.filter(user=request.user).distinct('ordereditem')
		qs2 = StoreItem.objects.all().distinct('name')
		qs3 = Cart.objects.filter(user=request.user).distinct('ordereditem', 'weight').values('ordereditem', 'weight', 'price')
		qs4 = Cart.objects.filter(user=request.user)
		serializer = StoreItemSerializer(qs2, many=True, context={'request': request})
		total_price = Cart.objects.filter(user=request.user).aggregate(Sum('price'))

		"""
		total_carbs = 0
		total_protein = 0
		total_calories = 0
		total_sugar = 0



		for i in qs4:
			get = NutritionalValue.objects.filter(item=i.ordereditem).values('name', 'value')
			times_to_multiply = 0
			num = 0
			weight = 0

			if 1 <= int(float(re.sub(r'[^\d.]+','',i.weight))) <= 9:
				weight = int(float(re.sub(r'[^\d.]+','',i.weight))) * 1000
			else:
				weight = int(float(re.sub(r'[^\d.]+','',i.weight)))

			while num < weight:
				times_to_multiply += 0.5
				num += 50;
			for i in get:
				if i['name'] == 'Protein':
					result = float(re.sub(r'[^\d.]+','',i['value'])) * times_to_multiply
					total_protein = float(total_protein + result)
				elif i['name'] == 'Carbs':
					result = float(re.sub(r'[^\d.]+','',i['value'])) * times_to_multiply
					total_carbs = float(total_carbs + result)
				elif i['name'] == 'Calories':
					result = float(re.sub(r'[^\d.]+','',i['value'])) * times_to_multiply
					total_calories = float(total_calories + result)
				elif i['name'] == 'Sugar':
					result = float(re.sub(r'[^\d.]+','',i['value'])) * times_to_multiply
					total_sugar = float(total_sugar + result)


		print(total_carbs, total_protein, total_calories, total_sugar)"""



		data = [{'id': i.id, 'ordereditem': i.ordereditem, 'weight': i.weight, 'count': Cart.objects.filter(ordereditem=i.ordereditem, user=request.user).count(), 
				'items_price': Cart.objects.filter(ordereditem=i.ordereditem, user=request.user).aggregate(Sum('price'))} for i in qs]
		data2 = [{'get_count': Cart.objects.filter(ordereditem=i['ordereditem'], weight=i['weight'], price=i['price'], user=request.user).values('ordereditem', 'weight').annotate(cou=Count('weight'))} for i in qs3]
		return Response({'items': data, 'total': total_price['price__sum'], 'photos': serializer.data, 'custom_count': data2}, status=200)
	else:
		return Response({'message':'Your cart is empty!'}, status=404)




"""Check in frontend if it works with many to many field objects coming from previous order model passed in request's ordereditem"""
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def RepeatOrder(request):

	get_id = request.data['id']
	ordereditems = PreviousOrderItems.objects.filter(id_of_order=get_id, user=request.user).values('item_name', 'item_weight', 'item_price', 'item_count')

	unavailable = ''
	for i in ordereditems:
		if StoreItem.objects.filter(name=i['item_name']):
			avail = StoreItem.objects.filter(name=i['item_name']).values('availability')
			if avail[0]['availability'] == 'In stock':
				j = 0
				while j < i['item_count']:
					Cart.objects.create(ordereditem=i['item_name'], price=i['item_price'], weight=i['item_weight'], user=request.user)
					j += 1
			else:
				unavailable = 'Not availabile'
		else:
			pass
	if unavailable is not '':
		raise NotFound('Some items are out of stock')
	return Response({'message': 'Added to cart'}, status=200)





@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def RatingCreateView(request):

	if request.method == "POST":
		item = request.data['ordereditem']
		stars = request.data['stars']
		review = request.data['review']
		
		qs = StoreItem.objects.filter(name=item)
		if not qs:
			return Response({'message': 'Item does not exist'}, status=400)

		if Rating.objects.filter(user=request.user, item=qs[0].name):
			return Response({'message':'You have already rated this item!'}, status=226)
		else:
			Rating.objects.create(user=request.user, item=qs[0].name, stars=stars, review=review)
			qs1 = Rating.objects.filter(user=request.user)
			serializer1 = RatingSerializer(qs1, many=True)
			return Response({'message':'Your rating has been submitted!', 'rating': serializer1.data}, status=201)
	qs = Rating.objects.filter(user=request.user)
	serializer = RatingSerializer(qs, many=True)
	qs2 = StoreItem.objects.all().distinct('name')
	serializer2 = StoreItemSerializer(qs2, many=True, context={'request': request})
	if qs:
		return Response({'rating': serializer.data, 'store_data': serializer2.data}, status=200)
	else:
		return Response({'rating': 'No ratings found!'}, status=404)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def GetRatingItems(request):
	if request.method == 'POST':
		get_id = request.data['id']
		qs = PreviousOrderItems.objects.filter(id_of_order=get_id).distinct('item_name').values('item_name')
		qs1 = PreviousOrder.objects.filter(id=get_id, user=request.user).values_list('delivery_and_package_rating', flat=True)
		qs2 = PreviousOrder.objects.filter(id=get_id, user=request.user).values_list('delivery_and_package_review', flat=True)
		return Response({'items': qs, 'get_rating': qs1, 'get_review': qs2}, status=200)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createDelPackRating(request):
	if request.method == 'POST':

		get_id = request.data['id']
		get_rating = request.data['rating']
		get_review = request.data['review']
		get_order = PreviousOrder.objects.filter(id=get_id, user=request.user).update(delivery_and_package_rating=get_rating, delivery_and_package_review=get_review)
		qs = PreviousOrder.objects.filter(id=get_id).values_list('delivery_and_package_rating', flat=True)
		qs1 = PreviousOrder.objects.filter(id=get_id).values_list('delivery_and_package_review', flat=True)

		return Response({'message': 'rating created', 'get_rating': qs, 'get_review': qs1}, status=201)



@api_view(['POST', 'GET'])
def RecipeView(request):

	if request.method == 'GET':

		qs = Recipe.objects.all()
		serializer = RecipeSerializer(qs, many=True, context={'request': request})
		qs1 = RecipeIngredients.objects.all()
		serializer1 = RecipeIngredientsSerializer(qs1, many=True, context={'request': request})

		if qs:

			return Response({'qs': serializer.data, 'ingredients': serializer1.data}, status=200)
		else:
			raise NotFound('No recipes available')


class RecipeDetailView(viewsets.ModelViewSet):

	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def buildCartForRecipe(request):

	get_id = request.data['id']
	get_ingredients = RecipeIngredients.objects.filter(id_of_recipe=get_id).values('name', 'weight', 'price', 'count')
	unavailable = ''
	for i in get_ingredients:
		if StoreItem.objects.filter(name=i['name']):
			avail = StoreItem.objects.filter(name=i['name']).values('availability')
			if avail[0]['availability'] == 'In stock':
				j = 0
				while j < i['count']:
					Cart.objects.create(ordereditem=i['name'], price=i['price'], weight=i['weight'], user=request.user)
					j += 1
			else:
				unavailable = 'Not availabile'
		else:
			pass

	if unavailable is not '':
		raise NotFound('Some items are out of stock')

	qs = Cart.objects.filter(user=request.user).distinct('ordereditem')
	serializer = CartSerializer(qs, many=True, context={'request': request})
	return Response({'data': serializer.data}, status=200)



@api_view(['POST', 'GET', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def FavRecipeView(request):

	if request.method == 'POST':

		get_id = request.data['id']
		get_recipe = Recipe.objects.get(id=get_id)
		FavRecipe.objects.create(id_of_recipe=get_recipe, user=request.user)

		qs = FavRecipe.objects.filter(user=request.user)
		serializer = FavRecipeSerializer(qs, many=True)

		qs1 = Recipe.objects.all()
		serializer1 = RecipeSerializer(qs1, many=True, context={'request': request})
		
		return Response({'message': 'Added', 'data': serializer.data, 'data1': serializer1.data}, status=200)

	if request.method == 'DELETE':

		get_id = request.data['id']
		FavRecipe.objects.filter(id_of_recipe=get_id, user=request.user).delete()

		qs = FavRecipe.objects.filter(user=request.user)
		serializer = FavRecipeSerializer(qs, many=True)

		qs1 = Recipe.objects.all()
		serializer1 = RecipeSerializer(qs1, many=True, context={'request': request})

		return Response({'message': 'Deleted', 'data': serializer.data, 'data1': serializer1.data}, status=200)

	qs = FavRecipe.objects.filter(user=request.user)

	if qs:
		serializer = FavRecipeSerializer(qs, many=True)
		return Response({'data': serializer.data}, status=200)
	else:
		raise NotFound('No Favs found!')




class HomeBannerView(generics.ListAPIView):

	queryset = HomeBanner.objects.all()
	serializer_class = HomeBannerSerializer



class HomeProductsView(generics.ListAPIView):

	queryset = HomeProducts.objects.all()
	serializer_class = HomeProductsSerializer



@api_view(['GET'])
def NutritionalValuesView(request):

	qs = NutritionalValue.objects.all()
	serializer = NutritionalValueSerializer(qs, many=True)
	return Response({'data': serializer.data}, status=200)





@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def CouponView(request):

	queryset = Coupon.objects.filter(user=request.user)
	serializer = CouponSerializer(queryset, many=True)
	return Response({'data': serializer.data}, status=200)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def CreatePushNotificationsToken(request):

	if request.method == 'POST':

		token = request.data['pushToken']

		try:
			user = request.user
			"""Checks if current logged in user is associated with the current device token"""
			if PushNotificationsToken.objects.filter(user=user, token=token):
				return Response({'message': 'Token exists'}, status=203)
			else:
				"""If current user is not associated with the current device token it updates the current token with current user"""
				if PushNotificationsToken.objects.filter(token=token):
					PushNotificationsToken.objects.filter(token=token).update(user=user)
					return Response({'message': 'Updated'}, status=202)
				else:
					PushNotificationsToken.objects.create(user=user, token=token)
					return Response({'message': 'created'}, status=201)

		except:
			"""Returns if the device token exists"""
			if PushNotificationsToken.objects.filter(token=token):
				return Response({'message': 'Token exists'}, status=200)
			else:
				"""Creates a device token if it doesn't exists"""
				PushNotificationsToken.objects.create(token=token)
				return Response({'message': 'created'}, status=201)