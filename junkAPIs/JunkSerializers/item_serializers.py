from rest_framework import serializers
from junkAPIs.models import Items, Menu
from .menu_serializers import MenuSerializer


class ItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Items
        fields = '__all__'

    def create(self, validated_data):
        validated_data['item_name_key'] = ''.join(validated_data['item_name_key'].strip().upper().split(' '))
        item_obj = Items.objects.create(**validated_data)
        return item_obj

    # def update(self, instance, validated_data):
    #     instance.item_type = validated_data.get('item_type', instance.item_type)
    #     instance.item_name = validated_data.get('item_name', instance.item_name)
    #     instance.item_name_key = validated_data.get('item_name_key', instance.item_name_key).upper()
    #     instance.item_description = validated_data.get('item_description', instance.item_description)
    #     instance.item_ingredients = validated_data.get('item_ingredients', instance.item_ingredients)
    #     instance.item_image = validated_data.get('item_image', instance.item_image)
    #     instance.item_diet_type = validated_data.get('item_diet_type', instance.item_diet_type)
    #     instance.item_calories = validated_data.get('item_calories', instance.item_calories)
    #     instance.menu = validated_data.get('menu', instance.menu)
    #     instance.save()
    #     return instance
