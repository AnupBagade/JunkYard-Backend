from rest_framework.serializers import ModelSerializer
from junkAPIs.models import CartOrders


class CartSerializer(ModelSerializer):

    class Meta:
        model = CartOrders
        fields = '__all__'

    
    def create(self, validated_data):
        cart_order_obj = CartOrders.objects.create(**validated_data)
        return cart_order_obj
    
    def update(self, instance, validated_data):
        new_cart_items_details = instance.cart_items_details
        new_cart_items = instance.cart_items
        new_cart_items_keys = instance.cart_items_keys
        new_cart_items_total_price = instance.cart_items_total_price
        if self.context.get('action_type') == 'add':    
            for key, value in validated_data.get('cart_items_details').items():
                if key not in instance.cart_items_keys:
                    # Adding items that are not exists in instance
                    new_cart_items_details[key] = value
                    new_cart_items_total_price = float(new_cart_items_total_price) + (float(value['price']) * float(value['quantity']))
                    new_cart_items_keys.append(key)
                else:
                    # Updating items
                    new_cart_items_details[key]['quantity'] = int(new_cart_items_details[key]['quantity']) + int(value['quantity'])
                    new_cart_items_details[key]['price'] = float(new_cart_items_details[key]['price']) + float(value['price'])
                    new_cart_items_total_price = float(new_cart_items_total_price) + (float(value['price']) * float(value['quantity']))

            # extend method modifies list, it does not return anything. Hence breaking conversion and modification.
            new_cart_items.extend(validated_data.get('cart_items'))
            new_cart_items = list(set(new_cart_items))
        
        elif self.context.get('action_type') == 'update':
            for key, value in validated_data.get('cart_items_details').items():
                new_cart_items_total_price = float(new_cart_items_total_price) - (float(new_cart_items_details[key]['quantity']) * float(new_cart_items_details[key]['price']))
                new_cart_items_details[key]['quantity'] = int(value['quantity'])
                new_cart_items_details[key]['price'] = float(value['price'])
                new_cart_items_total_price = float(new_cart_items_total_price) + float(new_cart_items_details[key]['quantity']) * float(new_cart_items_details[key]['price'])

        
        elif self.context.get('action_type') == 'remove':
            # Removing required elements from cart_items_details
            for item_name_key in validated_data.get('cart_items_keys'):
                #Updating new_cart_items_total_price
                item_quantity =  new_cart_items_details.get(item_name_key)['quantity']
                item_price = new_cart_items_details.get(item_name_key)['price']
                new_cart_items_total_price = float(new_cart_items_total_price) - (float(item_quantity) * float(item_price))

                # Removing item from new_cart_items_details
                new_cart_items_details.pop(item_name_key)

                # Removing item from new_cart_items_keys
                new_cart_items_keys.pop(new_cart_items_keys.index(item_name_key))
            
            new_cart_items = list(set(new_cart_items).difference(set(validated_data.get('cart_items'))))

        instance.cart_items_details = new_cart_items_details
        instance.cart_items = new_cart_items
        instance.cart_items_keys = new_cart_items_keys
        instance.cart_items_total_price = new_cart_items_total_price
        instance.save()
        return instance
