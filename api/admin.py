from django.contrib import admin
from .models import (CustomUserModel, InactiveUserId, ResetPassUserId, StoreItem, Address, Cart, Order, PreviousOrder, 
	DeliveryAddressId, Rating, Recipe, ItemsData, HomeBanner, DetailsImage, PushNotificationsToken, HomeProducts, Coupon)


admin.site.register(CustomUserModel)
admin.site.register(InactiveUserId)
admin.site.register(ResetPassUserId)
admin.site.register(StoreItem)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(PreviousOrder)
admin.site.register(DeliveryAddressId)
admin.site.register(Rating)
admin.site.register(Recipe)
admin.site.register(ItemsData)
admin.site.register(HomeBanner)
admin.site.register(DetailsImage)
admin.site.register(PushNotificationsToken)
admin.site.register(HomeProducts)
admin.site.register(Coupon)