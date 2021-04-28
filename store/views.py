from django.shortcuts import render
from store.serializers import (StoreItemSerializer, AddressBookSerializer, CartSerializer, PreviousOrderSerializer, 
	DeliveryAddressIdSerializer, RatingSerializer, RecipeSerializer, HomeBannerSerializer, DetailsImageSerializer, 
	PushNotificationsTokenSerializer, HomeProductsSerializer, CouponSerializer)
from api.models import (StoreItem, Address, Cart, Order, PreviousOrder, DeliveryAddressId, Rating, Recipe, ItemsData, 
	HomeBanner, CustomUserModel, DetailsImage, PushNotificationsToken, HomeProducts, Coupon)

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










class StoreItems(viewsets.ModelViewSet):
	queryset = StoreItem.objects.all()
	serializer_class = StoreItemSerializer

	@action(detail=True, methods=['GET'])
	def get_details(self, request, pk=None):

		get_item = StoreItem.objects.get(id=pk)
		get_detailsimages = DetailsImage.objects.filter(item=pk)

		serializer = StoreItemSerializer(get_item, many=False, context={'request': request})
		serializer1 = DetailsImageSerializer(get_detailsimages, many=True, context={'request': request})

		return Response({'details': serializer.data, 'images': serializer1.data}, status=200)


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
	 	price = StoreItem.objects.filter(name=item['name']).values('price')
	 	"""item is returning a dictionary thats the reason for item['name']"""
	 	Cart.objects.create(ordereditem=item['name'], price=price[0]['price'], user=request.user)
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
		serializer = CartSerializer(qs, many=True, context={'request': request})

		return Response({'data': serializer.data}, status=200)





@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def PlaceOrder(request):

	if request.method == 'POST':

		get_order = Cart.objects.filter(user=request.user)
		address = DeliveryAddressId.objects.filter(user=request.user).values('address_id')
		get_address = Address.objects.get(user=request.user, id__in=address)
		total_price = request.data['total_price']
		get_pushtoken = request.data['pushToken']

		for i in get_order:
			ItemsData.objects.create(ordereditem=i.ordereditem, price=i.price, ordereddate=i.ordereddate, orderedtime=i.orderedtime, 
				user=request.user)

		get_item = Cart.objects.filter(user=request.user).values_list('ordereditem', flat=True)
		get_date = Cart.objects.filter(user=request.user).values_list('ordereddate', flat=True)
		get_time = Cart.objects.filter(user=request.user).values_list('orderedtime', flat=True)
		get_data = ItemsData.objects.filter(ordereditem__in=get_item, ordereddate__in=get_date, orderedtime__in=get_time, 
			user=request.user)
		qs = Order.objects.create(user=request.user, total_price=total_price, ordered_address=get_address.address, 
			ordered_locality=get_address.locality, ordered_city=get_address.city)
		qs.ordereditem.set(get_data)
		qs2 = PreviousOrder.objects.create(user=request.user, price=total_price, ordered_address=get_address.address, 
			ordered_locality=get_address.locality, ordered_city=get_address.city)
		qs2.ordereditem.set(get_data)
		Cart.objects.filter(user=request.user).delete()
		
		send_push_message(get_pushtoken, 'Order has been placed successfully!', 'Order Status')
		return Response({'message': 'Placed Succesfully'}, status=201)





class PreviousOrderView(generics.ListAPIView):

	queryset = PreviousOrder.objects.all()
	serializer_class = PreviousOrderSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )


	def get_queryset(self):

		queryset = self.queryset
		qs = queryset.filter(user=self.request.user)

		if qs:
			return qs
		else:
			raise NotFound('Not Found')




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ConfirmOrder(request): 
	if Cart.objects.filter(user=request.user):
		qs = Cart.objects.filter(user=request.user).distinct('ordereditem')
		total_price = Cart.objects.filter(user=request.user).aggregate(Sum('price'))

		if total_price['price__sum'] is None:
			total_price_with_all_charges = total_price['price__sum']
		else:
			total_price_with_all_charges = total_price['price__sum'] + 20

		data = [{'id': i.id, 'ordereditem': i.ordereditem, 'count': Cart.objects.filter(ordereditem=i.ordereditem, user=request.user).count(), 
				'items_price': Cart.objects.filter(ordereditem=i.ordereditem, user=request.user).aggregate(Sum('price'))} for i in qs]
		return Response({'items': data, 'total': total_price_with_all_charges}, status=200)
	else:
		return Response({'message':'Your cart is empty!'}, status=404)




"""Check in frontend if it works with many to many field objects coming from previous order model passed in request's ordereditem"""
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def RepeatOrder(request):

	items = request.data['ordereditem']
	for i in items:
		item = i
		item_price = StoreItem.objects.filter(name=item).values('price')
		Cart.objects.create(ordereditem=item, price=item_price, user=request.user)
	return Response({'message': 'Added to cart'}, status=200)





@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def RatingCreateView(request):

	if request.method == "POST":
		item = request.data['ordereditem']
		stars = request.data['stars']
		review = request.data['review']
		try:
			qs = StoreItem.objects.get(name=item)
		except:
			return Response({'message': 'Item does not exist'}, status=400)

		if Rating.objects.filter(user=request.user, item=qs.id):
			return Response({'message':'You have already rated this item!'}, status=226)
		else:
			Rating.objects.create(user=request.user, item=qs, stars=stars, review=review)
			return Response({'message':'Your rating has been submitted!'}, status=201)
	qs = Rating.objects.filter(user=request.user)
	serializer = RatingSerializer(qs, many=True)
	if qs:
		return Response({'rating': serializer.data}, status=200)
	else:
		return Response({'rating': 'No ratings found!'}, status=404)




class RecipeView(viewsets.ModelViewSet):

	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )



class HomeBannerView(generics.ListAPIView):

	queryset = HomeBanner.objects.all()
	serializer_class = HomeBannerSerializer



class HomeProductsView(generics.ListAPIView):

	queryset = HomeProducts.objects.all()
	serializer_class = HomeProductsSerializer



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