from ast import iter_fields

from django.db.models import F
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, ValidationError

from app.funcsion import check_order_status, quantity_all_order, user_quantity, check_order_difference, distance
from app.models import Menu, Basket, Order, User


# ------------------------------------- USER serializers --------------------------------------------------- #
class LatitudeLongitudeUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['latitude', 'longitude']


class PhoneUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']


class UpdateFullnameSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


# --------------------------------------------- Menu Serializers ---------------------------------------------- #

class MenuSerializer(ModelSerializer):
    class Meta:
        model = Menu
        fields = ['name', 'created_at', 'price']


class MenuDetailSerializer(MenuSerializer):
    class Meta(MenuSerializer.Meta):
        fields = MenuSerializer.Meta.fields + ['description']


# ---------------------------------------- Basket Serializers ------------------------------------------------- #

class BasketSerializer(ModelSerializer):
    class Meta:
        model = Basket
        fields = ['food', 'quantity', 'price']


class BasketCreateSerializer(ModelSerializer):
    class Meta:
        model = Basket
        fields = ['food']
        read_only_fields = ['user']

    def create(self, validated_data):
        food_id = validated_data.get('food')
        user = validated_data.get('user')
        existing_food_basket = Basket.objects.filter(user=user, food=food_id).first()

        if existing_food_basket:
            existing_food_basket.quantity += 1
            existing_food_basket.save()
            return existing_food_basket
        else:
            validated_data['user'] = user
            validated_data['quantity'] = 1
            return Basket.objects.create(**validated_data)


# --------------------------------------------- Plus and Minus -------------------------------------------` #.

class BasketPlusSerializer(ModelSerializer):
    class Meta:
        model = Basket
        fields = ['id', 'food']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # Basketda userga tegishli bo'lgan foodni olish
        basket = Basket.objects.filter(user=user, food=validated_data['food']).first()

        if basket:
            # Mavjud quantity ni oshirish
            basket.quantity = F('quantity') + 1
            basket.save()
            basket.refresh_from_db()  # Yangilangan qiymatni olish uchun
            return basket
        else:
            raise ValidationError("Ushbu food userning savatida mavjud emas.")


class BasketMinusSerializer(ModelSerializer):
    class Meta:
        model = Basket
        fields = ['food']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        basket = Basket.objects.filter(user=user, food=validated_data['food']).first()

        if basket:
            if basket.quantity > 1:
                basket.quantity = F('quantity') - 1
                basket.save()
                basket.refresh_from_db()
                return basket
            else:
                basket.delete()
                basket.deleted = True
                return basket
        else:
            raise ValidationError("Ushbu food userning savatida mavjud emas.")


# ------------------------------------------- Order Serializers -------------------------------------------------- #
class OrderListSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'quantity', 'price']


class OrderAcceptSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        if instance.status != 'yangi':
            raise ValidationError("Faqat statusi 'yangi' larni qabul qilishingiz mumkin.")
        instance.status = "jarayonda"
        instance.save()
        return instance


class OrderPrepareSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        if instance.status != 'jarayonda':
            raise ValidationError("Faqat statusi 'yangi' larni qabul qilishingiz mumkin.")
        instance.status = 'tayyorlanmoqda'
        instance.save()
        return instance


class OrderDeliverySerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        if instance.status != 'tayyorlanmoqda':
            raise ValidationError("Faqat statusi 'tayyorlanmoqda' larni qabul qilishingiz mumkin.")
        instance.status = 'yo\'lda'
        instance.save()
        return instance


class OrderCompletionSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        if instance.status != "yo'lda":
            raise ValidationError("Faqat statusi 'Yo'lda' larni qabul qilishingiz mumkin.")
        instance.status = 'tugallandi'
        instance.save()
        return instance


class OrderCancelSerializer(ModelSerializer):
    def update(self, instance, validated_data):
        if not instance.status in ['yangi', 'jarayonda']:
            raise ValidationError(
                "Faqat statusi 'yangi yoki qabul qilingandan keyin bekor qilishingiz mumkin' larni qabul qilishingiz mumkin.")
        instance.status = 'bekor qilindi'
        instance.save()
        return instance


class OrderSerializer(ModelSerializer):
    response_message = SerializerMethodField()

    class Meta:
        model = Order
        fields = ['status', 'price', 'quantity', 'response_message']

    def get_response_message(self, obj):
        if obj.status == "yangi":
            return {"message": "Buyurtma hali qabul qilinmadi."}
        elif obj.status == 'jarayonda':
            return {
                'estimated preparation time': check_order_status(obj.updated_at, quantity_all_order(obj))
            }
        elif obj.status == 'tayyorlanmoqda':
            return {
                'estimated preparation time': check_order_status(obj.updated_at, user_quantity(obj.user))
            }
        elif obj.status == 'yo\'lda':
            return {"difference": f"{distance(obj.user.latitude, obj.user.longitude)} km",
                    'estimated delivery time': check_order_difference(obj.updated_at, obj.user.latitude,
                                                                      obj.user.longitude)
                    }
        elif obj.status == 'tugallandi':
            return {
                'message': 'Buyurtma muvofaqiyatli amalga oshirildi!😊'
            }
        elif obj.status == 'bekor qilindi':
            return {
                'message': 'Buyurma bekor qilindi!'
            }
