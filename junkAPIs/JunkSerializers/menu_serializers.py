from rest_framework import serializers
from junkAPIs.models import Menu


class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = '__all__'

    def create(self, validated_data):
        validated_data['menu_name_key'] = validated_data['menu_name_key'].upper()
        menu_obj = Menu.objects.create(**validated_data)
        return menu_obj

    def update(self, instance, validated_data):
        instance.menu_name = validated_data.get('menu_name', instance.menu_name)
        instance.menu_name_key = validated_data.get('menu_name_key', instance.menu_name_key).upper()
        instance.menu_image = validated_data.get('menu_image', instance.menu_image)
        instance.save()
        return instance
