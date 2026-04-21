from rest_framework import serializers
from .models.customer_request import CustomerRequest

class CustomerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerRequest
        fields = '__all__'