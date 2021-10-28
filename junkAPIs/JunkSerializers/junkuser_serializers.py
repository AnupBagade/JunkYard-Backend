from junkAPIs.models import Junkuser
from rest_framework import serializers
from junkAPIs.models import PendingOrders, Junkuser
from django.contrib.contenttypes.models import ContentType


class JunkUserSearializer(serializers.ModelSerializer):

    class Meta:
        model = Junkuser
        fields = '__all__'

    def create(self, validated_data):
        user_email = validated_data.pop('email')
        user_mobile = validated_data.pop('junkuser_mobile_number')
        user_password = validated_data.pop('password')
        user_groups = validated_data.pop('groups')
        user_perms = validated_data.pop('user_permissions')
        junkuser_obj = Junkuser.objects.create_user(user_email, user_mobile, user_password, **validated_data)
        return junkuser_obj


class JunkUserBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Junkuser
        fields = ['email', 'junkuser_first_name', 'junkuser_last_name', 'junkuser_gender',
                  'junkuser_age', 'junkuser_mobile_number', 'junkuser_address']


class JunkuserCustomerRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Junkuser
        fields = ['junkuser_last_name', 'junkuser_first_name', 'email','junkuser_mobile_number', 'junkuser_address', 'password']

    def create(self, validated_data):

        user_email = validated_data.pop('email')
        user_password = validated_data.pop('password')
        user_mobile = validated_data.pop('junkuser_mobile_number')
        # user_groups = validated_data.pop('groups')
        # user_perms = validated_data.pop('user_permissions')
        validated_data['junkuser_is_customer'] = True
        customer_obj = Junkuser.objects.create_user(user_email, user_mobile, user_password, **validated_data)
        return customer_obj
