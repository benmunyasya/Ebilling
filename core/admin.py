from django.contrib import admin
from .models import MpesaPayment,MpesaCallBacks,MpesaCalls,Client,WaterBillingCycle
# Register your models here.
admin.site.register(Client)
admin.site.register(WaterBillingCycle)
admin.site.register(MpesaPayment)
admin.site.register(MpesaCalls)
admin.site.register(MpesaCallBacks)