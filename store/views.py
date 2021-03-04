from django.shortcuts import render
from store.serializers import StoreItemSerializer, AddressBookSerializer, CartSerializer, PreviousOrderSerializer
from api.models import StoreItem, Address, Cart, Order, PreviousOrder

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



class AddressBook(generics.ListCreateAPIView):

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



class CartView(generics.ListCreateAPIView):
	 queryset = Cart.objects.all()
	 serializer_class = CartSerializer
	 authentication_classes = (TokenAuthentication, )
	 permission_classes = (IsAuthenticated, )

	 def get_queryset(self):

	 	queryset = self.queryset
	 	qs = queryset.filter(user=self.request.user).distinct('ordereditem')

	 	return qs



@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def CartReduceItemOrDeleteItem(request):

	if request.method == "POST":

		item = request.data['item']
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
		qs = Order.objects.create(user=request.user, total_price=total_price['price__sum'])
		qs.ordereditem.set(get_order)
		qs2 = PreviousOrder.objects.create(user=request.user, price=total_price['price__sum'])
		qs2.ordereditem.set(get_order)

		return Response(status=201)


class PreviousOrderView(generics.ListAPIView):

	queryset = PreviousOrder.objects.all()
	serializer_class = PreviousOrderSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )


	def get_queryset(self):

		queryset = self.queryset
		qs = queryset.filter(user=self.request.user).distinct('ordereddate')

		return qs