from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('login/', obtain_auth_token),
    path('register/', JunkuserCustomerRegistration.as_view(), name='junkuser_registration'),
    path('menu/', MenuList.as_view(), name='menu_list'),
    path('menu/<int:menu_id>/', MenuDetail.as_view(), name='menu_detail'),
    path('items/', ItemsList.as_view(), name='items_list'),
    path('items/<str:item_id>/', ItemDetail.as_view(), name='item_detail'),
    path('pendingorders/', PendingOrdersList.as_view(), name='orders_list'),
    path('pendingorders/<int:order_id>/', PendingOrderDetail.as_view(), name='order_detail'),
    path('approvedorders/', ApprovedOrdersList.as_view(), name='approved_orders_list'),
    path('approvedorders/<int:order_id>/', ApprovedOrdersDetail.as_view(), name='approved_ordes_detail'),
    path('cartorders/', CartOrdersList.as_view(), name='cart_list'),
    path('cartorders/<int:junkuser_id>/', CartOrdersDetail.as_view(), name='cart_user_detail'),
    path('junkusers/', JunkUsersList.as_view(), name='junkusers_list'),
    path('junkusers/<int:junkuser_id>/', JunkUserDetail.as_view(), name='junkusers_detail'),
    path('userloggedin/', ValidateUserLoggedIn.as_view(), name='validate_user_logged_in')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)