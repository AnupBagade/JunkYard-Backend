from rest_framework.views import APIView
from rest_framework import generics, mixins, serializers
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
from .models import DeliveryEmployees, Items, PendingOrders, Menu, Junkuser, ApprovedOrders, CartOrders
from django.core.exceptions import ObjectDoesNotExist
from junkAPIs.signals import delete_item_image, delete_menu_image
from datetime import datetime
from django.db.models import Q
import json
import ast
import time


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
        if self.request.query_params.get('item_name_key', None):
            queryset = queryset.filter(item_name_key=self.request.query_params.get('item_name_key'))
            print(queryset)
        if self.request.query_params.get('items', None):
            print(self.request.query_params.get('items'))
            items_list = self.request.query_params.get('items').split(',')
            queryset = queryset.filter(item_name_key__in=items_list)
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

    pagination_class = OrdersListPagination
    permission_classes = [PendingOrdersCustomPermission]
    message = list()

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

    def get_serializer_class(self):
        return OrderSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            # creating copy of data recieved.
            order_data = self.request.data.copy()
            # Creating instance of serializer class
            serializer_class = self.get_serializer_class()
            # validating junkuser id
            junkuser = Junkuser.objects.filter(junkuser_id=self.request.data.get('user'))
            if junkuser.exists(): 
                order_data['junkuser_customer'] = junkuser.first().junkuser_id
                order_data['order_delivery_address'] = self.request.data.get('order_delivery_address')
                order_data['order_user_mobile_number'] = self.request.data.get('order_user_mobile_number')
                orders_data_serialized = serializer_class(data=order_data)
                if orders_data_serialized.is_valid():
                    orders_data_serialized.save()
                    # CartOrders.objects.delete(cart_user=junkuser.junkuser_id)
                    return Response(orders_data_serialized.data, status=status.HTTP_200_OK)
                else:
                    return Response(orders_data_serialized.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                self.message.append('Provided user doesnot exist. Please register.')
        except (ObjectDoesNotExist, KeyError):
            return Response(self.message, status=status.HTTP_400_BAD_REQUEST)


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
    errorMessage = []

    def get_serializer_class(self):
        return ApprovedOrderSerializer

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
        order_data = request.data.copy()
        print(order_data)
        try:
            # Retrieve pending order details.
            pending_order_details = PendingOrders.objects.filter(order_id=request.data.get('order_id'))
            if pending_order_details.exists():
                pending_order_details = pending_order_details.first()
                order_data['order_items'] = pending_order_details.order_items
                order_data['order_user_mobile_number'] = pending_order_details.order_user_mobile_number
                order_data['order_delivery_address'] = pending_order_details.order_delivery_address
                order_data['ordered_date'] = pending_order_details.ordered_date
                order_data['ordered_timestamp'] = pending_order_details.ordered_timestamp
                order_data['ordered_status'] = 'in_progress'
                order_data['junkuser_customer'] = pending_order_details.junkuser_customer.junkuser_id
            else:
                self.errorMessage.append('Invalid pending order_id. Please provide valid pending order_id.')
                raise ObjectDoesNotExist
            
            # Retrieve employee instance using user_id.
            employee_details = Junkuser.objects.filter(junkuser_id=request.data.get('employee_id'), junkuser_is_employee=True)
            if employee_details.exists():
                order_data['order_approved_employee'] = employee_details.first().junkuser_id
            else:
                self.errorMessage.append('Invlaid employee ID. Please provide valid employee details.')

            # Serialize data
            serializer_class = self.get_serializer_class()
            serialized_orders = serializer_class(data=order_data)
            if serialized_orders.is_valid():
                # serialized_orders.save()
                # Removing pending order instance from PendingOrders model.
                # PendingOrders.objects.delete(order_id=request.data.get('order_id'))
                return Response(serialized_orders.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serialized_orders.data, status=status.HTTP_201_CREATED)
        except (ObjectDoesNotExist, KeyError):
            return Response(self.errorMessage, status=status.HTTP_400_BAD_REQUEST)
        


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
        print(self.request)
        print(dir(self.request))
        print(self.request.user)
        print(dir(self.request.user))
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
            print(junkuser_data_serialized.errors)
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
        return Response({'loggedIn': 'success'})


class GetUserRoles(APIView):
    def get(self, request):
        userRoles = {
            'email': request.user.email,
            'is_employee': request.user.junkuser_is_employee,
            'is_customer': request.user.junkuser_is_customer,
            'is_superuser': request.user.is_superuser
        }
        return Response(userRoles)

class CartOrdersList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView, ):
    permission_classes = [CartOrderCustomPermission]
    pagination_class = OrdersListPagination
    message = list()
    cart_post_request_data_requirement = "Input data should be below format. {'cart_user': userid, 'cart_items': {'items_details':[{'item_name': 'hamburger', 'quantity':2, 'price':12}], 'items':['hamburger'], 'total_price':price of all items/}/}. Valid user id should be used. Cartobject with required userid should not be present."

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
        try:
            cart_data = dict()
            cart_data['cart_items_details'] = dict()
            cart_data['cart_items_keys'] = list()
            cart_data['cart_items'] = list()
            cart_data['cart_items_total_price'] = float()

            # Validating user id.
            if self.request.data.get('cart_user', None):
                junkuser = Junkuser.objects.get(junkuser_id=self.request.data['cart_user']).junkuser_id
                cart_data['cart_user'] = junkuser
            else:
                self.message.append('Invalid user.')
                raise KeyError
            
            # Validating is there any existing cartorder instance for the user, item description and creating list of cart_items_keys, cart_items_total_price and cart_items.
            if not CartOrders.objects.filter(cart_user=self.request.data.get('cart_user')).exists():
                items_details = self.request.data.get('cart_items_details')
                for item in items_details:
                    item_name_key = Items.objects.get(item_name=item['item_name']).item_name_key
                    cart_data['cart_items_details'][item_name_key] = item
                    cart_data['cart_items'].append(item['item_name'])
                    cart_data['cart_items_keys'].append(item_name_key)
                    cart_data['cart_items_total_price'] += float(item['price']) * float(item['quantity'])
            else:
                self.message.append('Cart Instance is already present for this user or invalid keyword arguments. Please refer doc to use this endpoint.')
                raise KeyError

            serializer_class = self.get_serializer_class()
            cart_serialized = serializer_class(data=cart_data)
            if cart_serialized.is_valid():
                cart_serialized.save()
                return Response(cart_serialized.data, status=status.HTTP_201_CREATED)
            else:
                return Response(cart_serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except (ObjectDoesNotExist, KeyError):
            return Response(self.message, status=status.HTTP_400_BAD_REQUEST)


class CartOrdersDetail(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [CartOrderCustomPermission]
    message = list()

    def get_serializer_class(self):
        return CartSerializer

    def get_object(self, id):
        try:
            junkuser = Junkuser.objects.filter(junkuser_id=id)
            cart_items = list()
            if junkuser.exists():
                cart_items = junkuser.first().user_cart_items.all()
                if cart_items:
                    cart_items = cart_items.first()
                return {'status': True, 'cart_items': cart_items}
            else:
                return {'status': False}
        except (ObjectDoesNotExist, AttributeError, Exception):
            self.message.append('Invalid user. Please provide valid user id.')
            return Response({'information': self.message}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, junkuser_id, **kwargs):
        serializer_class = self.get_serializer_class()
        cart_obj = self.get_object(junkuser_id)

        if cart_obj.get('status') and cart_obj.get('cart_items'):
            cart_serialized = serializer_class(cart_obj['cart_items'])
            return Response(cart_serialized.data)

        elif cart_obj.get('status') and not cart_obj.get('cart_items'):
            return Response({'results': [], 'information': self.message}, status=status.HTTP_200_OK)

        elif not cart_obj.get('status'):
            return Response({'information': 'User with provided id, is not available.'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, junkuser_id, **kwargs):
        try:
            action_type = self.request.data.get('action_type')
            serializer_class = self.get_serializer_class()
            cart_instance = self.get_object(junkuser_id)

            if not cart_instance.get('status'):
                self.message.append('User with provided id, is not available.')
                return Response({'information': self.message}, status=status.HTTP_400_BAD_REQUEST)

            elif cart_instance.get('status') and not cart_instance.get('cart_items'):
                self.message.append('Cart Instance is not present for this user or invalid keyword arguments. Please try with post method or refer doc to use this endpoint.')
                return Response({'information': self.message}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                cart_data = dict()
                cart_data['cart_items_details'] = dict()
                cart_data['cart_items_keys'] = list()
                cart_data['cart_items'] = list()
                cart_data['cart_items_total_price'] = float()

                # Retrieving user id.
                if self.request.data.get('cart_user', None):
                    junkuser = Junkuser.objects.get(junkuser_id=self.request.data['cart_user']).junkuser_id
                    cart_data['cart_user'] = junkuser
                else:
                    self.message.append('User should be provided  as a value to cart_user key.')
                    raise KeyError

                # Validating is there any existing cartorder instance for the user, item description and creating list of cart_items_keys, cart_items_total_price and cart_items.
                if CartOrders.objects.filter(cart_user=self.request.data.get('cart_user')).exists():
                    if action_type == 'add' or action_type == 'update':
                        items_details = self.request.data.get('cart_items_details')
                        for item in items_details:
                            item_name_key = Items.objects.get(item_name=item['item_name']).item_name_key
                            cart_data['cart_items_details'][item_name_key] = item
                            cart_data['cart_items'].append(item['item_name'])
                            cart_data['cart_items_keys'].append(item_name_key)
                            cart_data['cart_items_total_price'] += float(item['price']) * float(item['quantity'])

                    elif action_type == 'remove':
                        for item in self.request.data.get('cart_items'):
                            cart_data['cart_items_keys'].append(Items.objects.get(item_name=item).item_name_key)
                            cart_data['cart_items'].append(item)
                
                cart_serialized = serializer_class(cart_instance['cart_items'], data=cart_data, partial=True, context={'action_type': action_type})
                if cart_serialized.is_valid():
                    cart_serialized.save()
                    return Response(cart_serialized.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(cart_serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except (ObjectDoesNotExist, KeyError):
            return Response({'information':self.message}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, junkuser_id, **kwargs):
        cart_obj = self.get_object(junkuser_id)
        cart_obj.delete()
        return Response("cart object deleted successfully", status=status.HTTP_200_OK)