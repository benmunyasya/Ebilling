
from django.db.models.signals import pre_save,post_save,post_delete
from django.dispatch import receiver

from  .models import Client,WaterBillingCycle,WaterConsumption,MpesaPayment
from datetime import datetime
currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year
prevMonth=currentMonth-1

billing_date=datetime(currentYear,currentMonth,8)

if currentMonth == 12:
    nextMonth=currentMonth-11
else:
    nextMonth=currentMonth+1

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

@receiver(post_save,sender=Client)
def create_billing_cycle(sender,created,instance,**kwargs):
    if created:
            billling_cycle = WaterBillingCycle.objects.create(client=instance,meter_number=instance.metre_number,
                month=currentMonth,balance_carried_forward=instance.existing_balance)
            WaterConsumption.objects.create(parent=billling_cycle,previous_reading=instance.first_reading,current_reading=0.00,month =str(currentMonth) )
           
@receiver(post_save,sender=MpesaPayment)  
def sync_Mpesa_Payment(sender,created,instance,**kwargs):   
    if created:
        associated_customer=Client.objects.get(metre_number=int(instance.reference[7:]))
        associated_bill=WaterBillingCycle.objects.get(client=associated_customer,month=currentMonth)
        
        bill_update = associated_bill
        bill_update.amount_paid=instance.amount
        bill_update.update_fields=['amount_paid','total']
        bill_update.save()
        


        
        