from rest_framework import serializers
from .models import *




class Sheet_Serializer(serializers.ModelSerializer):
    # Data_field=Data_Field_Serializer(many=True,read_only=True)
    # Data=Data_Field_Serializer(many=True,read_only=True)
    class Meta:
        model = Sheet
        fields="__all__"


class Data_Field_Serializer(serializers.ModelSerializer):
    # sheet=Sheet_Serializer(many=False,read_only=True)
    # ticketname=serializers.CharField(source="Sheet.ticketname",required=False)
    class Meta:
        model = Data_Field
        fields="__all__"