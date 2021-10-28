from rest_framework import serializers
from junkAPIs.models import ApprovedOrders


class ApprovedOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApprovedOrders
        fields = '__all__'