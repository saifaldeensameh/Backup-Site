
from django import forms
from .models import Sheet
from django.forms.widgets import DateTimeInput,SelectMultiple
from django.contrib.auth.models import User



class NewSheetForm(forms.ModelForm):
    # email = forms.CharField(max_length=255, required=True, widget=forms.EmailInput())

    class Meta:
        model = Sheet
        fields = ['sheeturl', 'ticketname','batchNumber', 'MajentoDate', 'Majentoid']
        unique_together = ('ticketname','batchNumber')
        widgets = {
            'MajentoDate': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class UserandSheet (forms.Form):
    majento_id = forms.ModelMultipleChoiceField(queryset=User.objects.all(),required=False)
    from_date = forms.DateTimeField(widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    to_date = forms.DateTimeField(widget=DateTimeInput(attrs={'type': 'datetime-local'}))








