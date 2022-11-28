from django.urls import path


from core.views import ClientCreate,download_form2A,download_form2B,bill_records,WaterMetreCreate,sending_bill_sms,MeterList,ClientList,updateBulkMeterReadings,take_readings,ClientUpdate,client_dashboard,home,confirmation,register_urls,validation,call_back
app_name = 'core'
 
urlpatterns = [
    path('',home,name='home'),
    path('add-new-client',ClientCreate.as_view(),name='add-new-client'),
    path('update-client/<int:pk>',ClientUpdate.as_view(),name='update-client'),
    path('client-dashboard/<int:pk>',client_dashboard,name='client-dashboard'),
    path('update-readings',updateBulkMeterReadings,name="update-readings"),
    #take readings
    path('take-readings',take_readings,name="take-readings"),
    path('download2a',download_form2A,name="download2a"),

    #bill records
    path('bill-records',bill_records,name="bill-records"),
     path('download2b',download_form2B,name="download2b"),
    path('send-bill-sms',sending_bill_sms,name='send-bill-sms'),
     path('client-list',ClientList.as_view(),name='client-list'),
    path('add-new-water-metre',WaterMetreCreate.as_view(),name='add-new-water-metre'),
    path('water-meter-list',MeterList.as_view(),name='water-meter-list'),
      path('c2b/register', register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', confirmation, name="confirmation"),
    path('c2b/validation', validation, name="validation"),
    path('c2b/callback', call_back, name="call_back"),

]
