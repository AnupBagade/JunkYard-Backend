from rest_framework import serializers
from junkAPIs.models import PendingOrders, ApprovedOrders


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = PendingOrders
        fields = '__all__'

