
from django import forms
from .models import Sheet
from django.forms.widgets import DateTimeInput


class NewSheetForm(forms.ModelForm):
    # email = forms.CharField(max_length=255, required=True, widget=forms.EmailInput())

    class Meta:
        model = Sheet
        fields = ['sheeturl', 'ticketname','batchNumber', 'MajentoDate', 'Majentoid']
        unique_together = ('ticketname','batchNumber')
        widgets = {
            'MajentoDate': DateTimeInput(attrs={'type': 'datetime-local'}),
        }









