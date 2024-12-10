from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.funcsion import is_within_24_hours, user_quantity
from app.permissions import IsAdminOrWaiter
from app.models import Menu, Order, Basket
from app.serializers import MenuSerializer, MenuDetailSerializer, BasketPlusSerializer, BasketMinusSerializer, \
    BasketSerializer, BasketCreateSerializer, OrderListSerializer, OrderPrepareSerializer, OrderAcceptSerializer, \
    OrderDeliverySerializer, OrderSerializer, LatitudeLongitudeUpdateSerializer, PhoneUpdateSerializer, \
    UpdateFullnameSerializer, OrderCompletionSerializer, OrderCancelSerializer


# ---------------------------------------------------- USER ------------------------------------------------
class BaseUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LatitudeLongitudeUpdateView(BaseUpdateAPIView):
    serializer_class = LatitudeLongitudeUpdateSerializer


class PhoneUpdateView(BaseUpdateAPIView):
    serializer_class = PhoneUpdateSerializer


class FullnameUpdateView(BaseUpdateAPIView):
    serializer_class = UpdateFullnameSerializer


# -------------------------------------- MENU ----------------------------------------------- #
def is_available_food():
    queryset = Menu.objects.filter(is_available=True).all()
    return queryset


class MenuListApiView(ListAPIView):
    queryset = is_available_food()
    serializer_class = MenuSerializer


class MenuDetailAPIView(RetrieveAPIView):
    queryset = is_available_food()
    serializer_class = MenuDetailSerializer
    permission_classes = [IsAuthenticated]


# ---------------------------------- ADMIN AND WAITER FOR --------------------------------------------- #

class MenuCreateAPIView(CreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrWaiter]


class MenuUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    queryset = is_available_food()
    serializer_class = MenuDetailSerializer
    permission_classes = [IsAuthenticated,IsAdminOrWaiter]


# -------------------------------------------------- Basket ----------------------------------------------------- #

class BasketListAPIView(ListAPIView):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticated]


class ProductBasketCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BasketCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasketFoodPlusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BasketPlusSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasketFoodMinusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BasketMinusSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            basket = serializer.save()
            if basket:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                Response({'message': 'Savatdan bunday ovqat yoq!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteBasketView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        delete_basket, _ = Basket.objects.filter(user=user, order__isnull=True).delete()
        if delete_basket > 0:
            return Response({"message": "Savatcha muvofaqiyatli ochirildi"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Savat bo'sh"}, status=status.HTTP_204_NO_CONTENT)


# -------------------------------------------- Order ------------------------------------------------------------- #

class OrderCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "error": "Foydalanuvchi autentifikatsiyadan o'tmagan"
            }, status=status.HTTP_201_CREATED)
        if user.latitude is None or user.longitude is None:
            return Response({'message': 'buyurtma berish uchun joylashuvingizni kiriting!'})
        user_updated = is_within_24_hours(user.updated_at)
        if not user_updated:
            return Response({'message': 'Joylashuvingizni yangilaganingizdan keyiin buyurtma bera olsiz.'})
        baskets = Basket.objects.filter(user=user, order__isnull=True)
        if not baskets.exists():
            return Response({
                "error": "Sizda hech qanday malumot topilmadi!"
            }, status=status.HTTP_400_BAD_REQUEST)

        new_order = Order.objects.create(user=user, price=0, quantity=0, status='yangi')

        total_price, total_quantity = 0, 0
        for item in baskets:
            item.order = new_order
            item.save()
            total_price += item.price
            total_quantity += item.quantity

        new_order.price = total_price
        new_order.quantity = total_quantity
        new_order.save()
        baskets.delete()
        return Response({'message': 'Buyurtma muvofaqiyatli qabul qilindi.'}, status=status.HTTP_201_CREATED)


class OrderListAPIView(ListAPIView):
    queryset = Order.objects.filter(status__in=['yangi', 'jarayonda', 'tayyorlanmoqda', 'yo\'lda']).all()
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated, IsAdminOrWaiter]


class OrderAcceptanceView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrWaiter]

    def patch(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(pk=pk)
        except:
            return Response({"error": "Bunday Buyurtma mavjud emas."})
        serializer = OrderAcceptSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Buyurtma qabul qilindi."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderPreparationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrWaiter]

    def patch(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(pk=pk)
        except:
            return Response({"error": "Bunday Buyurtma mavjud emas."})
        serializer = OrderPrepareSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Buyurtmani Tayoorlash bsohlandi"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDeliveryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrWaiter]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except:
            return Response({"error": "Bunday Buyurtma mavjud emas."})
        serializer = OrderDeliverySerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            return Response({"message": "Buyurtma yetkazib berish uchun yolga chiqdi."})

class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrWaiter]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except:
            return Response({"error": "Bunday Buyurtma mavjud emas."})
        serializer = OrderCancelSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            return Response({"message": "Buyurtma bekor qilindi."})

class OrderCompletionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrWaiter]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except:
            return Response({"error": "Bunday Buyurtma mavjud emas."})
        serializer = OrderCompletionSerializer(order, request.data, partial=True)
        if serializer.is_valid():
            return Response({"message": "Buyurtma muvofaqiyatli yakunlandi."})


class OrderTheAboutAPIView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Filter the latest order for the currently authenticated user
        user = self.request.user
        order = Order.objects.filter(user=user).order_by('created_at').first()

        # If no order is found, raise a 404 error
        if not order:
            raise NotFound(detail="No orders found for this user.")

        return order
