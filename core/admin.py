from django.contrib import admin
from .models import MpesaPayment,MpesaCallBacks,MpesaCalls
# Register your models here.
admin.site.register(MpesaPayment)
admin.site.register(MpesaCalls)
admin.site.register(MpesaCallBacks)