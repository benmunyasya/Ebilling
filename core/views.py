from django.shortcuts import render,HttpResponse
from .models import WaterBillingCycle,Client,WaterMeter,WaterConsumption,MpesaCallBacks,MpesaPayment,MpesaCalls
from .mpesa_credentials import LipanaMpesaPassword,MpesaAccessToken,MpesaC2bCredential
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from  django.urls import reverse_lazy
from django.http import JsonResponse
from django.core import serializers
import requests
from requests.auth import HTTPBasicAuth
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import addClientForm,addWaterMetreForm,WaterReadingForm
# Create your views here.
from datetime import datetime
from django.contrib import messages
currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year
prevMonth=currentMonth-1
nextMonth=currentMonth+1
billing_date=datetime(currentYear,currentMonth,8)
due_date=datetime(currentYear,nextMonth,8)
today_date=datetime(currentYear,currentMonth,currentDay)


class WaterMetreCreate(CreateView):
    
    model=WaterMeter
    template_name='water_metre_form.html'
    success_url=reverse_lazy('core:water-meter-list')
    form_class=addWaterMetreForm
   
    
    def form_valid(self,form):

        
        return super(WaterMetreCreate,self).form_valid(form)
class ClientCreate(CreateView):
    
    model=Client
    template_name='client_form.html'
    success_url=reverse_lazy('core:client-list')
    form_class=addClientForm
   
    
    def form_valid(self,form):

        
        return super(ClientCreate,self).form_valid(form)
billing_cycles=WaterBillingCycle.objects.filter(month=currentMonth)
watermeters=WaterMeter.objects.all()
all_clients=Client.objects.all()
class MeterList(ListView):
    model=WaterMeter
    context_object_name='water_meters'
    template_name='watermeter_list.html'
    def get_context_data(self, **kwargs):
        

        add_new_meter=addWaterMetreForm()
        context=super().get_context_data(**kwargs)
        
        context['form']=add_new_meter
        context['clients']=all_clients
           
       
        return context

class  ClientList(ListView):
    model=Client
    context_object_name='clients'
    template_name='client_list.html'
   
    

    def get_context_data(self, **kwargs):
       
           
        client_form=addClientForm()

        context = super().get_context_data(**kwargs)
        context['billing_cycles']=billing_cycles
        context['form']=client_form
       
        return context
@login_required
def home(request):
   
    billing_cycles_this_month=billing_cycles.count()
    water_meters=watermeters.count()
    context={
      'billing_cycles_this_month':billing_cycles_this_month,
      'water_meters':water_meters
    }
    
    return render(request,'home.html',context)

class ClientDelete(DeleteView):
    model= Client
    context_object_name='Client'
    template_name='confirm_delete.html'
    success_url=reverse_lazy('home')    
class ClientUpdate(UpdateView):
    model=Client
    form_class=addClientForm
    template_name='Client_form.html'
    
    success_url=reverse_lazy('core:home')
       

def client_dashboard(request,pk):
    billing_cycle_current_month=WaterBillingCycle.objects.get(id=pk)
    client=Client.objects.get(id=billing_cycle_current_month.client_id)
    all_billing_cycles=WaterBillingCycle.objects.filter(client_id=billing_cycle_current_month.client_id)
    readings = WaterConsumption.objects.filter(parent=billing_cycle_current_month).order_by('-month')
    all_customer_payments=MpesaPayment.objects.filter(reference='414170#{}'.format(str(client.metre_number)))
    print(all_customer_payments)
     #readings associated with this customer
    customer_readings=WaterConsumption.objects.all()
    customers_consumption=WaterConsumption.objects.filter(parent=billing_cycle_current_month).first()
    if  request.method=="POST":
         reading_form = WaterReadingForm(request.POST)
         if reading_form.is_valid():
            
            readings.delete()
            
            reading_form.instance.parent =billing_cycle_current_month
            
            instance=reading_form.save()
            reading_instance = serializers.serialize('json', [ instance, ])
            # send to client side.
            
            
            
            bill_update = billing_cycle_current_month
            bill_update.units = 0
          
            
            if bill_update.units == 0:
                bill_update.total = 0
                
            bill_update.units += reading_form.instance.consumption
           
          
            bill_update.save(update_fields=['units','total'])
            month_bill=bill_update.amount_remaining()
          
            return JsonResponse({"instance": reading_instance,
                             'units': bill_update.units,
                             'total':bill_update.total,
                             'month_bill':month_bill,
                           
                            },
                               status = 200)
    else:
        reading_form = WaterReadingForm(initial={"previous_reading":customers_consumption.previous_reading})
        
        
    context={
        'client':client,
         'readings':readings,
        'bill_cycle':billing_cycle_current_month,
        'reading_form':reading_form,
        'billing_history':all_billing_cycles,
         "customer_readings":customer_readings,
         "all_customer_payments":all_customer_payments
        }
    return render(request,'client_billing_dashboard.html',context)
def getAccessToken(request):
    consumer_key = 'qDHrMFeYU2Zp0sdGkda4q6mmhnHIBjZb'
    consumer_secret = 'wwMDwDgQA3L8bxwD'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    try:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    except:
        pass    
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    
    return HttpResponse(validated_mpesa_access_token)
@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               
               "ValidationURL":   "https://billin.herokuapp.com/c2b/validation",
               "ConfirmationURL": "https://billin.herokuapp.com/c2b/confirmation"}
    try:

        response = requests.post(api_url, json=options, headers=headers)
    except:
        pass
    return HttpResponse(response.text)
@csrf_exempt
def call_back(request):
    pass
@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    payment = MpesaPayment(
        type=mpesa_payment['TransactionType'],
        time=mpesa_payment['TransTime'],
        first_name=mpesa_payment['FirstName'],
        reference=mpesa_payment['BillRefNumber'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
      
       
      )
        
       
       
   
   
    payment.save()
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
