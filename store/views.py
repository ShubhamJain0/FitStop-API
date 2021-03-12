from django.shortcuts import render
from store.serializers import (StoreItemSerializer, AddressBookSerializer, CartSerializer, PreviousOrderSerializer, 
	DeliveryAddressIdSerializer, RatingSerializer, RecipeSerializer)
from api.models import StoreItem, Address, Cart, Order, PreviousOrder, DeliveryAddressId, Rating, Recipe

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import (Sum, Count)

from rest_framework import viewsets, status, generics, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound


# Create your views here.

User = get_user_model()

class StoreItemsList(generics.ListAPIView):

	queryset = StoreItem.objects.all().order_by('name')
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
		raise NotFound({"message": ["You don't have any saved address."]})




class DeliveryAddressIdView(generics.CreateAPIView):

	serializer_class = DeliveryAddressIdSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )




class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
	 queryset = Cart.objects.all()
	 serializer_class = CartSerializer
	 authentication_classes = (TokenAuthentication, )
	 permission_classes = (IsAuthenticated, )


	 def get_queryset(self):

	 	queryset = self.queryset
	 	qs = queryset.filter(user=self.request.user).distinct('ordereditem')

	 	return qs

	 def delete(self, request):
	 	Cart.objects.filter(user=self.request.user).delete()
	 	return Response(status=200)
		






@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def CartReduceItemOrDeleteItem(request):

	if request.method == "POST":

		item = request.data['reduceitem']
		Cart.objects.filter(pk__in=Cart.objects.filter(user=request.user, ordereditem=item).\
			values_list('id', flat=True)[0:1]).delete()

		return Response(status=200)

	if request.method == 'DELETE':

		delete_item = request.data['item']
		Cart.objects.filter(user=request.user, ordereditem=delete_item).delete()

		return Response(status=200)





@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def PlaceOrder(request):

	if request.method == 'GET':

		get_order = Cart.objects.filter(user=request.user)
		total_price = Cart.objects.filter(user=request.user).aggregate(Sum('price'))
		address = DeliveryAddressId.objects.filter(user=request.user).values('address_id')
		get_address = Address.objects.get(user=request.user, id__in=address)

		qs = Order.objects.create(user=request.user, total_price=total_price['price__sum'], ordered_address=get_address.address, 
			ordered_locality=get_address.locality, ordered_city=get_address.city)
		qs.ordereditem.set(get_order)
		qs2 = PreviousOrder.objects.create(user=request.user, price=total_price['price__sum'], ordered_address=get_address.address, 
			ordered_locality=get_address.locality, ordered_city=get_address.city)
		qs2.ordereditem.set(get_order)

		return Response(status=201)





class PreviousOrderView(generics.ListAPIView):

	queryset = PreviousOrder.objects.all()
	serializer_class = PreviousOrderSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )


	def get_queryset(self):

		queryset = self.queryset
		qs = queryset.filter(user=self.request.user)

		return qs




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ConfirmOrder(request):

	qs = Cart.objects.filter(user=request.user).distinct('ordereditem')
	total_price = Cart.objects.filter(user=request.user).aggregate(Sum('price'))
	total_price_with_all_charges = total_price['price__sum'] + 20

	data = [{'ordereditem': i.ordereditem, 'count': Cart.objects.filter(ordereditem=i.ordereditem, user=request.user).count(), 
			'items_price': Cart.objects.filter(ordereditem=i.ordereditem, user=request.user).aggregate(Sum('price'))} for i in qs]
	return Response({'items':data, 'total': total_price_with_all_charges})




"""Check in frontend if it works with many to many field objects coming from previous order model passed in request's ordereditem"""
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def RepeatOrder(request):

	items = request.data['ordereditem']
	"""for i in items.split(","):
		item = i
		item_price = StoreItem.objects.filter(name=item).values('price')
		Cart.objects.create(ordereditem=item, price=item_price, user=request.user)"""
	print(items)
	return Response(status=200)





@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def RatingCreateView(request):

	item = request.data['ordereditem']
	stars = request.data['stars']
	review = request.data['review']
	try:
		qs = StoreItem.objects.get(name=item)
	except:
		return Response({'message': 'Item does not exist'}, status=400)

	if Rating.objects.get(user=request.user, item=qs.id):
		return Response({'message':'You have already rated this item!'}, status=226)
	Rating.objects.create(user=request.user, item=qs, stars=stars, review=review)
	return Response({'message':'Your rating has been submitted!'}, status=201)




class RecipeView(viewsets.ModelViewSet):

	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )