from django import forms
from .models import Client,WaterMeter,WaterConsumption
class addClientForm(forms.ModelForm):
    class Meta:
        model =Client
        fields = ['full_name','metre_number','first_reading','existing_balance','active_phone_number']
class addWaterMetreForm(forms.ModelForm):
    class Meta:
        model =WaterMeter
        fields = '__all__'
class WaterReadingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WaterReadingForm, self).__init__(*args, **kwargs)
     
    class Meta:
        model = WaterConsumption
        fields = ['previous_reading','current_reading','month']