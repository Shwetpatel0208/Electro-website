from django.contrib import admin
from myapp.models import contact_detail,Product,Cart,BillingDetail,Order,OrderItem
admin.site.register(contact_detail)

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(BillingDetail)
admin.site.register(Order)
admin.site.register(OrderItem)




# Register your models here.
