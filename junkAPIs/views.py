from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from .JunkSerializers.item_serializers import ItemsSerializer
from .JunkSerializers.order_serializers import OrderSerializer
from .JunkSerializers.cart_serializers import CartSerializer
from .JunkSerializers.menu_serializers import MenuSerializer
from .JunkSerializers.approved_order_serializers import ApprovedOrderSerializer
from .JunkSerializers.junkuser_serializers import JunkUserSearializer,\
    JunkUserBasicSerializer, JunkuserCustomerRegistrationSerializer
from .CustomPermissions.junkuser_custom_permissions import JunkuserCustomPermission, JunkuserDetailCustomPermission
from .CustomPermissions.pendingorders_custom_permissions import PendingOrdersCustomPermission
from .CustomPermissions.approvedorders_custom_permissions import ApprovedOrdersCustomPermission
from .CustomPermissions.items_custom_permissions import ItemsCustomPermission
from .CustomPermissions.menu_custom_permissions import MenuCustomPermission
from .CustomPermissions.cartorders_custom_permission import CartOrderCustomPermission
from .models import Items, PendingOrders, Menu, Junkuser, ApprovedOrders, CartOrders
from django.core.exceptions import ObjectDoesNotExist
from junkAPIs.signals import delete_item_image, delete_menu_image
from datetime import datetime
from django.db.models import Q
import json


class MenuList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = MenuSerializer
    permission_classes = [MenuCustomPermission]

    def get_queryset(self):
        menu = Menu.objects.all()
        return menu

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MenuDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin, generics.GenericAPIView):
    lookup_field = 'menu_id'
    permission_classes = [MenuCustomPermission]

    def get_serializer_class(self):
        return MenuSerializer

    def get_queryset(self):
        menu = Menu.objects.all()
        return menu

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            menu_data = request.data
            serializer_class = self.get_serializer_class()
            menu_obj = self.get_object()
            if menu_data.get('menu_image', None):
                serialized_data = serializer_class(menu_obj, data=menu_data)
            else:
                serialized_data = serializer_class(menu_obj, data=menu_data, partial=True)
            if serialized_data.is_valid():
                if menu_data.get('menu_image', None):
                    reduntant_image_path = menu_obj.menu_image.path
                    serialized_data.save()
                    delete_menu_image.send(sender="Menu", image_path=reduntant_image_path)
                else:
                    serialized_data.save()
                return Response(serialized_data.data)
            else:
                return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, ObjectDoesNotExist) as e:
            return Response(f'Invalid Request - {e}', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ItemsPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_size'


class ItemsList(generics.GenericAPIView, mixins.ListModelMixin):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [ItemsCustomPermission]
    pagination_class = ItemsPagination

    def get_queryset(self):
        queryset = Items.objects.all()
        if self.request.query_params.get('item_type', None):
            queryset = queryset.filter(item_type=self.request.query_params.get('item_type'))
        if self.request.query_params.get('item_name', None):
            queryset = queryset.filter(item_name=self.request.query_params.get('item_name'))
        if self.request.query_params.get('items', None):
            items_list = self.request.query_params.get('items').split(',')
            queryset = queryset.filter(item_name__in=items_list)
        return queryset

    def get_serializer_class(self):
        return ItemsSerializer

    def get(self, request, *args, **kwargs):

        return self.list(request, *args, **kwargs)

    def post(self, request, format=None):
        try:
            item_data = request.data
            # Since menu field value is not recieved from FE, we have to query the menu object and set.
            item_data['menu'] = Menu.objects.get(menu_name_key=request.data['item_type'].upper()).menu_id
            items_serializer = self.get_serializer_class()
            items_serialized = items_serializer(data=item_data)
            if items_serialized.is_valid():
                items_serialized.save()
                return Response(items_serialized.data, status=status.HTTP_201_CREATED)
            else:
                return Response(items_serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, ObjectDoesNotExist):
            return Response('Invalid request.', status=status.HTTP_400_BAD_REQUEST)


class ItemDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [ItemsCustomPermission]
    lookup_field = 'item_id'

    def get_queryset(self):
        items = Items.objects.all()
        return items

    def get_serializer_class(self):
        return ItemsSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            item_obj = self.get_object()
            item_data = request.data.copy()
            item_data['menu'] = Menu.objects.get(menu_name_key=request.data['item_type'].upper()).menu_id
            item_serializer = self.get_serializer_class()
            if not item_data.get('item_image', None):
                item_serialized = item_serializer(item_obj, data=item_data, partial=True)
            else:
                item_serialized = item_serializer(item_obj, data=item_data)
            if item_serialized.is_valid():
                if request.data.get('item_image', None):
                    reduntant_image_path = item_obj.item_image.path
                    item_serialized.save()
                    delete_item_image.send(sender='Items', image_path=reduntant_image_path)
                else:
                    item_serialized.save()
                return Response(item_serialized.data)
            else:
                return Response(item_serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, ObjectDoesNotExist):
            return Response('Invalid request.', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



class OrdersListPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_size'


class JunkusersListPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_size'


class PendingOrdersList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    serializer_class = OrderSerializer
    pagination_class = OrdersListPagination
    permission_classes = [PendingOrdersCustomPermission]

    ORDERS_QUERY_PARAMETERS = {
        'ORDER_ID': 'order_id',
        'ITEM_TYPE': 'item_type',
        'USER_MOBILE': 'user_mobile_number',
        'USER_EMAIL_ID': 'user_email_id',
        'START_DATE': 'start_date',
        'END_DATE': 'end_date',
        'ORDER_STATUS': 'order_status'
    }

    def get_queryset(self):
        queryset = PendingOrders.objects.all()
        query_keys = self.request.query_params.keys()
        try:
            if self.ORDERS_QUERY_PARAMETERS['ORDER_ID'] in query_keys:
                queryset = queryset.get(
                    order_id=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['ORDER_ID']))
            else:

                if self.ORDERS_QUERY_PARAMETERS['USER_EMAIL_ID'] in query_keys and self.ORDERS_QUERY_PARAMETERS['USER_MOBILE'] in query_keys:
                    junkuser_obj = Junkuser.objects.get(
                        junkuser_mobile_number=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['USER_MOBILE']),
                        email=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['USER_EMAIL_ID']))
                    if junkuser_obj:
                        queryset = junkuser_obj.pending_orders.all()
                elif self.ORDERS_QUERY_PARAMETERS['USER_EMAIL_ID'] in query_keys:
                    junkuser_obj = Junkuser.objects.get(
                        email=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['USER_EMAIL_ID']))
                    if junkuser_obj:
                        queryset = junkuser_obj.pending_orders.all()
                elif self.ORDERS_QUERY_PARAMETERS['USER_MOBILE'] in query_keys:
                    junkuser_obj = Junkuser.objects.get(
                        junkuser_mobile_number=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['USER_MOBILE']))
                    if junkuser_obj:
                        queryset = junkuser_obj.pending_orders.all()

                if self.ORDERS_QUERY_PARAMETERS['START_DATE'] in query_keys and self.ORDERS_QUERY_PARAMETERS['END_DATE'] in query_keys:
                    start_date = datetime.strptime(
                        self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['START_DATE']), '%Y-%m-%d').date()
                    end_date = datetime.strptime(
                        self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['END_DATE']), '%Y-%m-%d').date()
                    queryset = queryset.filter(Q(ordered_date__lte=end_date) & Q(ordered_date__gte=start_date))

                if self.ORDERS_QUERY_PARAMETERS['ITEM_TYPE'] in query_keys:
                    item_type = self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['ITEM_TYPE'])
                    queryset = [order for order in queryset if item_type in json.loads(order.order_items).keys()]

            return queryset
        except ObjectDoesNotExist:
            return Response('Invalid user details, order details.', status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PendingOrderDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin, generics.GenericAPIView):

    queryset = PendingOrders.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'
    permission_classes = [PendingOrdersCustomPermission]

    def get(self, request, *args,  **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args,  **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ApprovedOrdersList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    ORDERS_QUERY_PARAMETERS = {
        'ORDER_ID': 'order_id',
        'ITEM_TYPE': 'item_type',
        'USER_MOBILE': 'user_mobile_number',
        'USER_EMAIL_ID': 'user_email_id',
        'START_DATE': 'start_date',
        'END_DATE': 'end_date',
        'ORDER_STATUS': 'order_status',
        'ORDER_APPROVED_EMPLOYEE': 'order_approved_employee_id',
        'ORDER_DELIVERY_EMPLOYEE': 'order_delivery_employee_id',
    }

    serializer_class = ApprovedOrderSerializer
    pagination_class = OrdersListPagination
    permission_classes = [ApprovedOrdersCustomPermission]

    def get_queryset(self):
        queryset = ApprovedOrders.objects.all()
        query_keys = self.request.query_params.keys()

        try:
            if self.ORDERS_QUERY_PARAMETERS['ORDER_ID'] in query_keys:
                queryset = queryset.filter(
                    order_id=self.request.query_params.get([self.ORDERS_QUERY_PARAMETERS['ORDER_ID']]))
            else:

                if self.ORDERS_QUERY_PARAMETERS['USER_MOBILE'] in query_keys and self.ORDERS_QUERY_PARAMETERS['USER_EMAIL_ID'] in query_keys:
                    junk_user = Junkuser.objects.get(
                        junkuser_mobile_number=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['USER_MOBILE']),
                        email=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['USER_EMAIL_ID']))
                    if junk_user:
                        queryset = junk_user.approved_orders.all()
                elif self.ORDERS_QUERY_PARAMETERS['USER_MOBILE'] in query_keys:
                    junk_user = Junkuser.objects.get(
                        junkuser_mobile_number=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['USER_MOBILE']))
                    if junk_user:
                        queryset = junk_user.approved_orders.all()
                elif self.ORDERS_QUERY_PARAMETERS['USER_EMAIL_ID'] in query_keys:
                    junk_user = Junkuser.objects.get(
                        email=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['USER_EMAIL_ID']))
                    if junk_user:
                        queryset = junk_user.approved_orders.all()

                if self.ORDERS_QUERY_PARAMETERS['ORDER_STATUS'] in query_keys:
                    queryset = queryset.filter(
                        order_status=self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['ORDER_STATUS']))

                if self.ORDERS_QUERY_PARAMETERS['ORDER_APPROVED_EMPLOYEE'] in query_keys:
                    employee_obj = Junkuser.objects.get(junkuser_id=self.request.query_params.get(
                        self.ORDERS_QUERY_PARAMETERS['ORDER_APPROVED_EMPLOYEE']))
                    if employee_obj:
                        queryset = queryset.filter(order_approved_employee=employee_obj.junkuser_id)

                if self.ORDERS_QUERY_PARAMETERS['ORDER_DELIVERY_EMPLOYEE'] in query_keys:
                    employee_obj = Junkuser.objects.get(junkuser_id=self.request.query_params.get(
                        self.ORDERS_QUERY_PARAMETERS['ORDER_DELIVERY_EMPLOYEE']))
                    if employee_obj:
                        queryset = queryset.filter(order_approved_employee=employee_obj.junkuser_id)

                if self.ORDERS_QUERY_PARAMETERS['START_DATE'] in query_keys and self.ORDERS_QUERY_PARAMETERS['END_DATE'] in query_keys:
                    start_date = datetime.strptime(
                        self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['START_DATE']), '%Y-%m-%d').date()
                    end_date = datetime.strptime(
                        self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['END_DATE']), '%Y-%m-%d').date()
                    queryset = queryset.filter(Q(ordered_date__lte=end_date) & Q(ordered_date__gte=start_date))

                if self.ORDERS_QUERY_PARAMETERS['ITEM_TYPE'] in query_keys:
                    item_type = self.request.query_params.get(self.ORDERS_QUERY_PARAMETERS['ITEM_TYPE'])
                    queryset = [order for order in queryset if item_type in json.loads(order.order_items).keys()]
            return queryset
        except ObjectDoesNotExist:
            return Response('Invalid order details, search criteria', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ApprovedOrdersDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin, generics.GenericAPIView):

    queryset = ApprovedOrders.objects.all()
    serializer_class = ApprovedOrderSerializer
    lookup_field = 'order_id'
    permission_classes = [ApprovedOrdersCustomPermission]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class JunkUsersList(mixins.ListModelMixin, generics.GenericAPIView):

    JUNKUSER_QUERY_PARAMS = {
        'JUNKUSER_ID': 'junkuser_id',
        'JUNKUSER_LAST_NAME': 'junkuser_last_name',
        'JUNKUSER_FIRST_NAME': 'junkuser_first_name',
        'JUNKUSER_EMAIL_ID': 'junkuser_email_id',
        'JUNKUSER_MOBILE_NUMBER': 'junkuser_mobile_number',
        'JUNKUSER_JOINED': 'junkuser_joined',
        'JUNKUSER_AGE': 'junkuser__age',
        'JUNKUSER_GENDER': 'junkuser_gender',
        'JUNKUSER_IS_CUSTOMER': 'junkuser_is_customer',
        'JUNKUSER_IS_EMPLOYEE': 'junkuser_is_employee'
    }

    permission_classes = [JunkuserCustomPermission]
    pagination_class = JunkusersListPagination

    def get_serializer_class(self):
        try:
            if self.request.user.is_superuser:
                return JunkUserSearializer
            elif self.request.user.junkuser_is_customer or self.request.user.junkuser_is_employee:
                return JunkUserBasicSerializer
        except Exception:
            raise PermissionDenied

    def get_queryset(self):
        queryset = Junkuser.objects.all()
        query_keys = self.request.query_params.keys()
        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_IS_CUSTOMER'] in query_keys:
            queryset = queryset.filter(
                junkuser_is_customer=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_IS_CUSTOMER']))
        elif self.JUNKUSER_QUERY_PARAMS['JUNKUSER_IS_EMPLOYEE'] in query_keys:
            queryset = queryset.filter(
                junkuser_is_employee=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_IS_EMPLOYEE']))

        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_ID'] in query_keys:
            queryset = queryset.filter(
                junkuser_id=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_ID']))

        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_LAST_NAME'] in query_keys:
            queryset = queryset.filter(
                junkuser_last_name=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_LAST_NAME']))

        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_FIRST_NAME'] in query_keys:
            queryset = queryset.filter(
                junkuser_first_name=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_FIRST_NAME']))

        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_EMAIL_ID'] in query_keys:
            queryset = queryset.filter(
                email=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_EMAIL_ID']))

        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_MOBILE_NUMBER'] in query_keys:
            queryset = queryset.filter(junkuser_mobile_number=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_MOBILE_NUMBER']))

        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_JOINED'] in query_keys:
            employee_joined_date = datetime.strptime(
                self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_JOINED']), '%Y-%m-%d').date()
            queryset = queryset.filter(junkuser_joined=employee_joined_date)

        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_AGE'] in query_keys:
            queryset = queryset.filter(
                junkuser__age=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_AGE']))

        if self.JUNKUSER_QUERY_PARAMS['JUNKUSER_GENDER'] in query_keys:
            queryset = queryset.filter(
                junkuser_gender=self.request.query_params.get(self.JUNKUSER_QUERY_PARAMS['JUNKUSER_GENDER']))
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        junkuser_data_serialized = serializer_class(data=request.data)
        if junkuser_data_serialized.is_valid():
            junkuser_data_serialized.save()
            return Response(junkuser_data_serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(junkuser_data_serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class JunkUserDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, generics.GenericAPIView):

    queryset = Junkuser.objects.all()
    lookup_field = 'junkuser_id'
    permission_classes = [JunkuserDetailCustomPermission]

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return JunkUserSearializer
        elif self.request.user.junkuser_is_employee:
            return JunkUserBasicSerializer
        elif self.request.user.junkuser_is_customer:
            return JunkUserBasicSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class JunkuserCustomerRegistration(generics.GenericAPIView):
    serializer_class = JunkuserCustomerRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        junkuser_serialized = JunkuserCustomerRegistrationSerializer(data=request.data)
        if junkuser_serialized.is_valid():
            junkuser_serialized.save()
            return Response(junkuser_serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(junkuser_serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateUserLoggedIn(APIView):

    def get(self, request):
        print(f'request - {request.user}')
        return Response({'loggedIn': 'success'})


class CartOrdersList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView, ):
    lookup_field = 'cart_user'
    permission_classes = [CartOrderCustomPermission]
    pagination_class = OrdersListPagination

    cart_data_items_format = {
        'items_details': list(),
        'items': list(),
        'total_price': float()
    }

    cart_post_request_data_requirement = "Input data should be a dictionary with keys and values - " \
                                         "{'cart_user': 00, 'item_name': 'Hamburger', 'quantity':'5'}"

    def get_serializer_class(self):
        return CartSerializer

    def get_queryset(self):
        query_set = CartOrders.objects.all()
        if self.request.query_params.get('cart_user', None):
            junkuser = Junkuser.objects.get(junkuser_id=self.request.query_params.get('cart_user'))
            query_set = junkuser.user_cart_items.all()
        return query_set

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Retrieve junkuser object and pass junkuser_id to the cart_user field of CartOrders model.
        try:
            cart_data = dict()
            if self.request.data.get('cart_user', None):
                # validating id received is valid.
                junkuser = Junkuser.objects.get(junkuser_id=request.data['cart_user']).junkuser_id
                cart_data['cart_user'] = junkuser
            else:
                raise KeyError

            if self.request.data.get('item_name', None) and self.request.data.get('quantity', None) and self.request.data.get('price', None):
                self.cart_data_items_format['items_details'].append(
                    {'item_name': self.request.data.get('item_name'), 'quantity': self.request.data.get('quantity')}
                )
                self.cart_data_items_format['items'].append(self.request.data.get('item_name'))
                self.cart_data_items_format['total_price'] = \
                    float(self.request.data.get('price')) * int(self.request.data.get('price'))

                cart_data['cart_items'] = json.dumps(self.cart_data_items_format)
            else:
                raise KeyError

            print(cart_data)

            serializer_class = self.get_serializer_class()
            cart_serialized = serializer_class(data=cart_data)
            if cart_serialized.is_valid():
                cart_serialized.save()
                return Response(cart_serialized.data, status=status.HTTP_201_CREATED)
            else:
                return Response(cart_serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except (ObjectDoesNotExist, KeyError):
            return Response(json.dumps(self.cart_post_request_data_requirement), status=status.HTTP_400_BAD_REQUEST)


class CartOrdersDetail(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [CartOrderCustomPermission]

    def get_serializer_class(self):
        return CartSerializer

    def get_object(self, id):
        try:
            junkuser = Junkuser.objects.get(junkuser_id=id)
            cart_items = junkuser.user_cart_items.all()
            if cart_items:
                cart_items = list(junkuser.user_cart_items.all())[0]
            else:
                cart_items = list()
            return cart_items
        except ObjectDoesNotExist:
            return Response('Invalid user', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, junkuser_id, **kwargs):
        serializer_class = self.get_serializer_class()
        cart_data = self.get_object(junkuser_id)
        if cart_data:
            cart_serialized = serializer_class(cart_data)
            return Response(cart_serialized.data)
        else:
            return Response({'results': [], 'message': 'No results'}, status=status.HTTP_200_OK)

    def put(self, request, junkuser_id, **kwargs):
        serializer_class = self.get_serializer_class()
        cart_instance = self.get_object(junkuser_id)
        cart_data = request.data.copy()
        print(cart_data)
        cart_data['cart_items'] = str(cart_data['cart_items'])
        print(cart_data)
        cart_data['cart_user'] = Junkuser.objects.get(junkuser_id=request.data['cart_user']).junkuser_id
        cart_serialized = serializer_class(cart_instance, data=cart_data, partial=True)
        if cart_serialized.is_valid():
            cart_serialized.save()
            return Response(cart_serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(cart_serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, junkuser_id, **kwargs):
        cart_obj = self.get_object(junkuser_id)
        cart_obj.delete()
        return Response("cart object deleted successfully", status=status.HTTP_200_OK)