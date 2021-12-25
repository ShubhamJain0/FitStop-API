"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers
from store.views import (StoreItems, StoreItemsFruitsList, StoreItemsDriedFruitsList,StoreItemsExoticsList, AddressBook, CartView, PlaceOrder, 
    CartReduceItemOrDeleteItem, PreviousOrderView, DeliveryAddressIdView, ConfirmOrder, RepeatOrder, RatingCreateView, GetRatingItems,
    createDelPackRating, RecipeView, RecipeDetailView, HomeBannerView, getDeliveryAddress, CreatePushNotificationsToken, CouponView, 
    ActiveOrderView, buildCartForRecipeIngredients, FavRecipeView, NutritionalValuesView, CreatePaymentOrder, PlaceOrderCOD, SubscriptionCartView,
    SubscriptionCartReduceItemOrDeleteItem, ConfirmSubscription, StartSubscription, RecipeSubscriptionCartView, RecipeSubscriptionCartReduceOrDelete,
    ConfirmRecipeSubscription, StartRecipeSubscription, MySubscriptionsView, RepeatSubscription, StoreItemsImmuntiyBoosterList,
    StoreItemsOtherList)

router = routers.DefaultRouter()
router.register('myaddress', AddressBook)
router.register('recipedetail', RecipeDetailView)


urlpatterns = [
	path('', include(router.urls)),
    path('storelist/', StoreItems.as_view()),
    path('fruitslist/', StoreItemsFruitsList.as_view()),
    path('dried-fruitslist/', StoreItemsDriedFruitsList.as_view()),
    path('exoticslist/', StoreItemsExoticsList.as_view()),
    path('imblist/', StoreItemsImmuntiyBoosterList.as_view()),
    path('otherlist/', StoreItemsOtherList.as_view()),
    path('cart/', CartView.as_view()),
    path('order/', PlaceOrder),
    path('orderCOD/', PlaceOrderCOD),
    path('activeorders/',  ActiveOrderView),
    path('reduceordelete/', CartReduceItemOrDeleteItem),
    path('previousorders/', PreviousOrderView),
    path('deliveryaddress/', DeliveryAddressIdView.as_view()),
    path('getdeliveryaddress/', getDeliveryAddress),
    path('confirm/', ConfirmOrder),
    path('repeatorder/', RepeatOrder),
    path('createrating/', RatingCreateView),
    path('getratingitems/', GetRatingItems),
    path('delpackrate/', createDelPackRating),
    path('homebanner/', HomeBannerView.as_view()),
    path('pushnotificationtoken/', CreatePushNotificationsToken),
    path('coupons/', CouponView),
    path('recipes/', RecipeView),
    path('recipecartingredients/', buildCartForRecipeIngredients),
    path('favrecipes/', FavRecipeView),
    path('nutritionalvalues/', NutritionalValuesView),
    path('createpaymentorder/', CreatePaymentOrder),
    path('subscart/', SubscriptionCartView.as_view()),
    path('subsreduceordelete/', SubscriptionCartReduceItemOrDeleteItem),
    path('subsconfirm/', ConfirmSubscription),
    path('subscribe/', StartSubscription),
    path('recipesubscart/', RecipeSubscriptionCartView.as_view()),
    path('recipesubsreduceordelete/', RecipeSubscriptionCartReduceOrDelete),
    path('recipesubsconfirm/', ConfirmRecipeSubscription),
    path('recipesubscribe/', StartRecipeSubscription),
    path('mysubscriptions/', MySubscriptionsView),
    path('repeatsubscription/', RepeatSubscription),
]