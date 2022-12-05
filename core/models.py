from django.db import models


import uuid

from phonenumber_field.modelfields import PhoneNumberField
from django.utils.text import slugify

from datetime import datetime
import string
import random





MONTHS_SELECT = [
    ('1','1'),
    ('1','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7'),
    ('8','8'),
    ('9','9'),
    ('10','10'),
    ('11','11'),
    ('12','12'),
]
# Create your models here.
class WaterMeter(models.Model):
    metre_number =  models.IntegerField(primary_key=True)
   
    def __str__(self):
        return f"{self.metre_number}"  

class Client(models.Model):
   
    full_name = models.CharField(max_length=100)
   
   
   
    metre_number=  models.OneToOneField(WaterMeter,
      unique=True,on_delete=models.CASCADE)
   
    first_reading = models.IntegerField(default=0)
    existing_balance = models.IntegerField(default=100)
    active_phone_number = PhoneNumberField(null=True, blank=True)
    secondary_phone_number= PhoneNumberField(null=True, blank=True)
    
    def __str__(self):
            return f"{self.full_name}"
   
class WaterBillingCycle(models.Model):
       
    client = models.ForeignKey('Client', on_delete=models.CASCADE,null=True,blank=True,verbose_name='Client.full_name')
   
    
    meter_number = models.ForeignKey('WaterMeter', on_delete=models.CASCADE,null=True,blank=True)
    amount_paid = models.IntegerField(
         default=0)
    
    
    units = models.IntegerField(
        default=0, null=True, blank=True)
    unit_price = models.IntegerField(
        verbose_name='Unit Price (KES)',default=120)
    
    balance_carried_forward=models.IntegerField(
       default=0)
    total = models.IntegerField( default=0)
  
    
    month = models.CharField(choices=MONTHS_SELECT, null=True, blank=True,max_length=10)
    standing_charge = models.IntegerField(
        default=200)
    
  
    
   
   
    
    
    def amount_remaining(self):
        r_amount = self.total-self.amount_paid
        return r_amount
    def save(self, *args, **kwargs):
            
           

            if self.units :
                
                self.total = (self.units*self.unit_price)+ self.standing_charge+ self.balance_carried_forward
            if self.units == 0:
                 self.total=self.standing_charge+ self.balance_carried_forward
                
            
           
        
            super(WaterBillingCycle, self).save(*args, **kwargs)
    def month_bill(self):
        monthly_bill=self.total-self.balance_carried_forward
        return monthly_bill
  

    def __str__(self):
        return f'{self.id} - {self.client}'

    class Meta:
        verbose_name_plural = 'Water Billing Cycles'
class WaterConsumption(models.Model):
    parent = models.ForeignKey('WaterBillingCycle', on_delete=models.CASCADE,verbose_name='WaterBillingCycle.client')
    
    previous_reading = models.IntegerField()
    current_reading = models.IntegerField()
   
    consumption = models.IntegerField(
        default=0)
    month = models.CharField(choices=MONTHS_SELECT,max_length=10,null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.current_reading:
            self.consumption = self.current_reading-self.previous_reading
            
            super(WaterConsumption, self).save(*args, **kwargs)
            
        super(WaterConsumption, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.month}"


class WaterPayments(models.Model):
    parent = models.ForeignKey(WaterBillingCycle, on_delete=models.CASCADE)
    tracking_code = models.CharField(
        max_length=15, unique=True, blank=True, null=True)
    payment_code = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    
    date_paid = models.DateField()

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = ''.join(random.choices(
                string.ascii_letters+string.digits, k=10))
       
            super(WaterPayments, self).save(*args, **kwargs)
        super(WaterPayments, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_code}"

    class Meta:
        verbose_name = 'Water Billing Payments'
        verbose_name_plural = verbose_name

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True        
class MpesaCalls(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call'
        verbose_name_plural = 'Mpesa Calls'


class MpesaCallBacks(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'






class   MpesaPayment(models.Model):
    """This model records all the mpesa payment transactions"""
    amount = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)
    type=models.TextField(null=True, blank=True)
    reference=models.TextField(null=True, blank=True)
    first_name=models.CharField(max_length=100,null=True, blank=True)
    middle_name=models.CharField(max_length=100,null=True, blank=True)
    last_name=models.CharField(max_length=100,null=True, blank=True)
    transaction_no = models.CharField(default=uuid.uuid4, max_length=50, unique=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    organization_balance = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    time=models.DateTimeField(blank=True, null=True,auto_now_add=True)
    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'
    def __str__(self):
        return self.first_name
    
   
    
   
   
    
  
    
   
 

    def __unicode__(self):
        return f"{self.transaction_no}"

        #############communications######
class ManagerClientCommunication(models.Model):
    ref_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    sent_to = models.ManyToManyField(Client,blank=True)
   
    send_to_all = models.BooleanField(default=False)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    
    
    def receiver_names(self):
        return ','.join([str(t.Client) for t in self.sent_to.all()])
    
    def save(self, *args, **kwargs):
        if not self.ref_number:
            self.ref_number = ''.join(random.choices(string.digits, k=10))
            super(ManagerClientCommunication, self).save(*args, **kwargs)
        super(ManagerClientCommunication, self).save(*args, **kwargs)
    class Meta:
        verbose_name_plural = 'Archives | Manager SMS'
    def __Str__(self):
        return f"{self.sent_to}"