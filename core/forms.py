from django import forms
from .models import Client,WaterMeter,WaterConsumption,ManagerClientCommunication
from django_summernote.widgets import SummernoteWidget
class addClientForm(forms.ModelForm):
    class Meta:
        model =Client
        fields = ['full_name','metre_number','first_reading','existing_balance','active_phone_number','secondary_phone_number']
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

        

class NewClientSmsForm(forms.ModelForm):
    class Meta:
        model = ManagerClientCommunication
        fields = ['send_to_all','sent_to','message']
        widgets = {
            'sent_to': forms.CheckboxSelectMultiple,
            'message': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '300px'}}),
        }
    def __init__(self, *args, **kwargs):
        super(NewClientSmsForm, self).__init__(*args, **kwargs)
        self.fields['sent_to'].label = 'Receivers'
        self.fields['sent_to'].queryset = Client.objects.all()
