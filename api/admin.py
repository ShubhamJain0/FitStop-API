from django.contrib import admin
from .models import CustomUserModel, InactiveUserId, ResetPassUserId, StoreItem, Address, Cart, Order, PreviousOrder


admin.site.register(CustomUserModel)
admin.site.register(InactiveUserId)
admin.site.register(ResetPassUserId)
admin.site.register(StoreItem)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(PreviousOrder)