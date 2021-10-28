from rest_framework.serializers import ModelSerializer
from junkAPIs.models import CartOrders


class CartSerializer(ModelSerializer):

    class Meta:
        model = CartOrders
        fields = '__all__'