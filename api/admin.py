from django.contrib import admin
from .models import (CustomUserModel, StoreItem, Address, Cart, Order, PreviousOrder, 
	DeliveryAddressId, Rating, Recipe, HomeBanner, DetailsImage, PushNotificationsToken, HomeProducts, Coupon, 
	ActiveOrder, VariableItem, PreviousOrderItems, RecipeIngredients, NutritionalValue, FavRecipe)


admin.site.register(CustomUserModel)
admin.site.register(StoreItem)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(PreviousOrder)
admin.site.register(DeliveryAddressId)
admin.site.register(Rating)
admin.site.register(Recipe)
admin.site.register(HomeBanner)
admin.site.register(DetailsImage)
admin.site.register(PushNotificationsToken)
admin.site.register(HomeProducts)
admin.site.register(Coupon)
admin.site.register(ActiveOrder)
admin.site.register(VariableItem)
admin.site.register(PreviousOrderItems)
admin.site.register(RecipeIngredients)
admin.site.register(NutritionalValue)
admin.site.register(FavRecipe)