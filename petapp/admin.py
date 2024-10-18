from django.contrib import admin
from petapp.models import Pet, Cart, Order

# Register your models here.
class PetAdmin(admin.ModelAdmin):
    list_display=['name','type','breed','gender','age','price','details','imagepath']
    list_filter=['type','breed','age','price']

class CartAdmin(admin.ModelAdmin):
    list_display=['id', 'petid', 'uid','quantity']

class OrderAdmin(admin.ModelAdmin):
    list_display=['id', 'orderid', 'petid','userid','quantity']
    list_filter=['petid', 'userid']

admin.site.register(Pet, PetAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)