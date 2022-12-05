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
import requests
from djqscsv import render_to_csv_response
from .forms import addClientForm,addWaterMetreForm,WaterReadingForm,NewClientSmsForm
from django.contrib import messages #import messages
# Create your views here.
from datetime import datetime
from django.contrib import messages
from .send_sms import send_sms
#send sms
import os
import africastalking 
from dotenv import load_dotenv
currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year
prevMonth=currentMonth-1

billing_date=datetime(currentYear,currentMonth,8)

if currentMonth == 12:
    nextMonth=currentMonth-11
else:
    nextMonth=currentMonth+1


today_date=datetime(currentYear,currentMonth,currentDay)

#billing_cycles=WaterBillingCycle.objects.filter(month=currentMonth)
watermeters=WaterMeter.objects.all()
all_clients=Client.objects.all()

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
        consumptions=WaterConsumption.objects.filter(month=currentMonth)

        billing_cycles=WaterBillingCycle.objects.filter(month=currentMonth)
        context = super().get_context_data(**kwargs)
        context['billing_cycles']=billing_cycles
        context['form']=client_form
        context['consumptions']=consumptions
        
       
        return context
@login_required
def home(request):
    billing_cycles=WaterBillingCycle.objects.filter(month=currentMonth)
    billing_cycles_this_month=billing_cycles.count()
    water_meters=watermeters.count()
    # for i in all_clients:
    #         try:   
    #             bill=WaterBillingCycle.objects.create(client_id=i.id,meter_number_id=i.metre_number_id,
                  

    #                 month=str(currentMonth),balance_carried_forward = i.existing_balance)

    #             WaterConsumption.objects.create(parent=bill,previous_reading=i.first_reading,current_reading=0,
    #                                         month=str(currentMonth))
    #         except:
    #             print(i)
    #             pass

            
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
    template_name='client_form.html'
    
    success_url=reverse_lazy('core:home')
       

def client_dashboard(request,pk):
    billing_cycle_current_month=WaterBillingCycle.objects.get(id=pk)
    client=Client.objects.get(id=billing_cycle_current_month.client_id)
    all_billing_cycles=WaterBillingCycle.objects.filter(client_id=billing_cycle_current_month.client_id)
    readings = WaterConsumption.objects.filter(parent=billing_cycle_current_month).order_by('-month')
    all_customer_payments=MpesaPayment.objects.filter(reference='414170#{}'.format(str(client.metre_number)))
    #this months reading
    reading= WaterConsumption.objects.get(parent=billing_cycle_current_month)
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
        'reading':reading,
         'readings':readings,
        'bill_cycle':billing_cycle_current_month,
        'reading_form':reading_form,
        'billing_history':all_billing_cycles,
         "customer_readings":customer_readings,
         "all_customer_payments":all_customer_payments
        }
    return render(request,'client_billing_dashboard.html',context)
def take_readings(request):
    billing_cycles=WaterBillingCycle.objects.filter(month=currentMonth)
    consumptions=WaterConsumption.objects.filter(month=currentMonth)

    context={}
    context['billing_cycles']=billing_cycles
 
    context['consumptions']=consumptions
    return render(request,'form2a.html',context)

def download_form2A(request):
     consumptions=WaterConsumption.objects.filter(month=currentMonth).values('parent__meter_number','parent__client__full_name',
     'previous_reading','current_reading','consumption')
     return render_to_csv_response(consumptions,filename=f"Form 2A month-{currentMonth}")
def bill_records(request):
    billing_cycles=WaterBillingCycle.objects.filter(month=currentMonth)
    consumptions=WaterConsumption.objects.filter(month=currentMonth)

    context={}
    context['billing_cycles']=billing_cycles
 
    context['consumptions']=consumptions
    return render(request,'form2b.html',context)
def download_form2B(request):
     consumptions=WaterConsumption.objects.filter(month=currentMonth).values('parent__meter_number','parent__client__full_name',
     'previous_reading','current_reading','consumption','parent__balance_carried_forward','parent__total','parent__amount_paid')
     return render_to_csv_response(consumptions,filename=f"Form 2A month-{currentMonth}")
def updateBulkMeterReadings(request):
    consumptions=WaterConsumption.objects.filter(month=currentMonth)

    for i in consumptions:
        if str(i.parent.id) in request.POST:
            new_reading = request.POST[str(i.parent.id)]
            i.current_reading = int(new_reading)
            i.save()
            billing_cycle_current_month=WaterBillingCycle.objects.get(id=i.parent.id,month=currentMonth)
            bill_update=billing_cycle_current_month
            bill_update.units = 0
          
            
            if bill_update.units == 0:
                bill_update.total = 0
                
            bill_update.units =  bill_update.units + i.consumption
           
           
            bill_update.save(update_fields=['units','total'])
           
             
    
    
    
    return HttpResponse('All Readings have been updated successfully')
def updateBillRecords(request):
    cycles=WaterBillingCycle.objects.filter(month=currentMonth)

    for i in cycles:
        if str(i.id) in request.POST:
            new_bill_update = request.POST[str(i.id)]
           
            i.amount_paid = int(new_bill_update)
            
            i.save(update_fields=['amount_paid','total'])
            print(i.amount_paid)
           
          
            
           
            
           
           
          
           
           
             
    
    
    
    return HttpResponse('Entered Payments  have been updated successfully')
def comms_dashboard(request):
    form=NewClientSmsForm()
    context={
        'form':form
    }
    return render (request,'comms.html',context)
    
def sending_bill_sms(request):
        import calendar
        import time
        current_GMT = time.gmtime()

        time_stamp = calendar.timegm(current_GMT)
        all_recipients=WaterConsumption.objects.filter(month=currentMonth)
        URL='https://sms.movesms.co.ke/api/compose?'
        access_token='IWMJ34pknP5FTg3JQgMUUE0aja8uPt67aBM1PWu97vowc3Ao9c'
        headers = {'api_key':'IWMJ34pknP5FTg3JQgMUUE0aja8uPt67aBM1PWu97vowc3Ao9c','User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
        leo=datetime.now()
        secondary_recipients=Client.objects.filter(secondary_phone_number__isnull=False)
        print(secondary_recipients.count())
        #sending to undelivered
        undelivered=[73,37,111,135,128,150,183,13,205,148,222,70,102,91,36,99,223,230,77,59,167,226,234,180,67,39,2,76,213,192,158,500]
        for i in undelivered:
            cycle=WaterBillingCycle.objects.get(meter_number=i,month=currentMonth)
            consumption = WaterConsumption.objects.get(parent_id=cycle.id,month=currentMonth)
            balance = cycle.amount_remaining()
            if cycle.client.secondary_phone_number is not None:
                phone=[str(cycle.client.active_phone_number),str(cycle.client.secondary_phone_number)]
            else:
                phone=str(cycle.client.active_phone_number)
            message=f"WANGETHA WATER\nDate:{str(leo)}\nName:{cycle.client.full_name}\nMtr:{str(cycle.client.metre_number).zfill(3)}\nPrev. Reading:{consumption.previous_reading}\nCurr.Reading:{consumption.current_reading}\nUnits:{consumption.consumption}\nUnit Price:{cycle.unit_price}\nService Charge:{cycle.standing_charge}\nBalance:{cycle.balance_carried_forward}\nTotal:{balance}\nPAYMENT:\nLipa Na Mpesa Paybill\nBusiness No:247247\nAccount No:414170#{str(cycle.meter_number).zfill(3)}\nAccount Name:Nicholas Wangetha Kabubi"
            data={'username':'Munyasya',
                       'api_key':'IWMJ34pknP5FTg3JQgMUUE0aja8uPt67aBM1PWu97vowc3Ao9c',
                       'sender':'SMARTLINK',
                       'to':phone,
                       'message':message,
                       'msgtype':'5',
                       'dlr':'0'}
            response2=requests.get(url=URL,params=data,headers=headers)
                
            
        #sending to secondary numbers
        #for i in secondary_recipients:
            #cycle=WaterBillingCycle.objects.get(client_id=i.id,month=currentMonth)
            #consumption = WaterConsumption.objects.get(parent_id=cycle.id,month=currentMonth)
            #balance = cycle.amount_remaining()
            #phone=str(i.secondary_phone_number)
           # message=f"WANGETHA WATER\nDate:{str(leo)}\nName:{i.full_name}\nMtr:{str(i.metre_number).zfill(3)}\nPrev. Reading:{consumption.previous_reading}\nCurr.Reading:{consumption.current_reading}\nUnits:{consumption.consumption}\nUnit Price:{cycle.unit_price}\nService Charge:{cycle.standing_charge}\nBalance:{cycle.balance_carried_forward}\nTotal:{balance}\nPAYMENT:\nLipa Na Mpesa Paybill\nBusiness No:247247\nAccount No:414170#{str(cycle.meter_number).zfill(3)}\nAccount Name:Nicholas Wangetha Kabubi"
            #data={'username':'Munyasya',
               #        'api_key':'IWMJ34pknP5FTg3JQgMUUE0aja8uPt67aBM1PWu97vowc3Ao9c',
                #       'sender':'SMARTLINK',
                  #     'to':phone,
                     #  'message':message,
                     #  'msgtype':'5',
                      # 'dlr':'0'}
            #response2=requests.get(url=URL,params=data,headers=headers)
        # for i in all_recipients:
       #         balance=i.parent.amount_remaining()
               

       #         phone=str(i.parent.client.active_phone_number)
       #         message=f"WANGETHA WATER\nDate:{str(leo)}\nName:{i.parent.client.full_name}\nMtr:{str(i.parent.meter_number).zfill(3)}\nPrev. Reading:{i.previous_reading}\nCurr.Reading:{i.current_reading}\nUnits:{i.consumption}\nUnit Price:{i.parent.unit_price}\nService Charge:{i.parent.standing_charge}\nBalance:{i.parent.balance_carried_forward}\nTotal:{balance}\nPAYMENT:\nLipa Na Mpesa Paybill\nBusiness No:247247\nAccount No:414170#{str(i.parent.meter_number).zfill(3)}\nAccount Name:Nicholas Wangetha Kabubi"
        #        data={'username':'Munyasya',
        #               'api_key':'IWMJ34pknP5FTg3JQgMUUE0aja8uPt67aBM1PWu97vowc3Ao9c',
         #              'sender':'SMARTLINK',
         #              'to':phone,
         #              'message':message,
         #              'msgtype':'5',
         #              'dlr':'0'}
          #      response2=requests.get(url=URL,params=data,headers=headers)
          #      print(data['message'])
           #     print(response2)
        return render (request,'comms.html')        
                    
                #response=requests.get(f"https://sms.movesms.co.ke/api/compose?username=Munyasya&api_key=z8a0Qxeo2NYDXkxizPfQiUVa6sgk79Nloaf3e2EFZgTH8LNNrU&sender=SMARTLINK&to=[{i.parent.client.active_phone_number}]&message={payment_message}&msgtype=5&dlr=1",headers=headers)
                #print(i,response.text)
           # all_recipients=WaterConsumption.objects.filter(month=currentMonth)
            #for i in all_recipients:
                   #balance=i.parent.amount_remaining()
                   #response=requests.get(f"https://sms.movesms.co.ke/api/compose?username=Munyasya&api_key=9MwIOCOLy6Uzuxoffiqa8T0yt1CZBNfAyiNcNet2RdcddFWJjY&sender=SMARTLINK&to=[254741433144]&message=[Hello]&msgtype=[5]&dlr=[0]")
                     #response=requests.get(f"https://api2.uwaziimobile.com/send?token=W9AVmznocBsoGVkHqBOf_mChmfYZyr&phone={i.parent.client.active_phone_number}&text=WANGETHA WATER\nDate:{str(today_date).split()[0]}\nName:{i.parent.client.full_name.split()[0]}\nMtr:{str(i.parent.meter_number).zfill(3)}\nCurr.Reading:{i.current_reading}\nPrev. Reading:{i.previous_reading}\nUnits:{i.consumption}\nUnit Price:{i.parent.unit_price}\nService Charge:{i.parent.standing_charge}\nBalance:{i.parent.balance_carried_forward}\nTotal:{balance}\n&senderID=Uwazii-OTP")
                   # if response:
                            #   response2=requests.get(f"https://api2.uwaziimobile.com/send?token=W9AVmznocBsoGVkHqBOf_mChmfYZyr&phone={i.parent.client.active_phone_number}&text=PAYMENT DETAILS:\nLipa Na Mpesa Paybill\nBusiness Number:247247\nAccount Number:414170#+{str(i.parent.meter_number).zfill(3)}\nAccount Name:Nicholas Wangetha Kabubi\n&senderID=Uwazii-OTP")
                              # print(i,response2.text)
        
        #from urllib.parse import urlencode
        
       
       
      
       
        #username='Munyasya'
        #api_key='mDTNhvqsfaF1qjrkyUWFtKG8PynpGMRqqQF7xlDTZdTUiYCc76'
        #sender='SMARTLINK'
        #to='[254741433144]'
        #message='[hello]',
        
        #data = {'username':username,
        #'api_key':api_key,
        #'sender':sender,
        #'to':to,
        #'message':message,
          
       # }
       
        #print(response2)
        #URL='https://sms.movesms.co.ke/api/compose?'
        #response=requests.post(url=URL,data=data,headers=headers)
        #print(response.text)
                  
           
        
def getAccessToken(request):
    consumer_key = 'qDHrMF1eYU2Zp0sdGkda4q6mmhnHIBjZb'
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
