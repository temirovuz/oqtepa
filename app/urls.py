from django.urls import path

from app.views import MenuListApiView, MenuDetailAPIView, MenuCreateAPIView, MenuUpdateDeleteAPIView, BasketListAPIView, \
    BasketFoodPlusAPIView, BasketFoodMinusAPIView, ProductBasketCreateAPIView, OrderCreateAPIView, OrderListAPIView, \
    OrderAcceptanceView, OrderPreparationView, OrderDeliveryAPIView, OrderTheAboutAPIView, LatitudeLongitudeUpdateView, \
    PhoneUpdateView, FullnameUpdateView, DeleteBasketView, OrderCompletionView

urlpatterns = [
    # user

    path('update-lat-lon/', LatitudeLongitudeUpdateView.as_view(), name='update_lat_lon'),
    path('update-phone/', PhoneUpdateView.as_view(), name='update_phone'),
    path('update-fullname/', FullnameUpdateView.as_view(), name='update_fullname'),
    # food

    path('foods/', MenuListApiView.as_view(), name='foods'),
    path('food-create/', MenuCreateAPIView.as_view(), name='food-create'),
    path('food/<int:pk>', MenuDetailAPIView.as_view(), name='food-detail'),
    path('food-edit/<int:pk>', MenuUpdateDeleteAPIView.as_view(), name='food-detail-edit'),
    # basket

    path('basket/', BasketListAPIView.as_view(), name='basket'),
    path('basket-create/', ProductBasketCreateAPIView.as_view(), name='basket-create'),
    path('plus/', BasketFoodPlusAPIView.as_view(), name='plus'),
    path('minus/', BasketFoodMinusAPIView.as_view(), name='minus'),
    path('basket/clear/', DeleteBasketView.as_view(), name='basket-clear'),
    # Order

    path('order-create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/', OrderListAPIView.as_view(), name='orders'),
    path('order-acceptance/', OrderAcceptanceView.as_view(), name="acceptance"),
    path('order-preparation/', OrderPreparationView.as_view(), name='preparation'),
    path('order-delivery/', OrderDeliveryAPIView.as_view(), name='delivery'),
    path('order-completion/', OrderCompletionView.as_view(), name='completion'),
    path('order/', OrderTheAboutAPIView.as_view(), name='order')

]
