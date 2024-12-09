from datetime import datetime, timedelta, timezone
import pytz
from dateutil import parser

from geopy.distance import geodesic

from app.models import Order
from config.settings import env

grocery_store_lat = env('LONGITUDE')
grocery_store_lon = env('LATITUDE')


def distance(user_lat, user_lon):
    restaurant_coord = (grocery_store_lat, grocery_store_lon)
    user_coord = (user_lat, user_lon)

    distance = geodesic(restaurant_coord, user_coord).kilometers
    return float(f"{distance:.2f}")


def distance_time(nums):
    sekund = nums * (3 * 60)
    sekund += (2 * 60)
    return timedelta(seconds=sekund)


def quantity_all_order(user_order):
    orders = Order.objects.filter(created_at__lt=user_order.created_at, status__in=['jarayonda', 'tayyorlanmoqda'])
    total_previous_quantity = sum(order.quantity for order in orders)
    total_previous_quantity += user_order.quantity
    return total_previous_quantity


def user_quantity(user):
    order = Order.objects.filter(user=user).first()
    return order.quantity


def preparation_time(num):
    sekund = num * (1 * 60 + 25)
    return timedelta(seconds=sekund)


def calculate_time_difference(updated_at):
    if isinstance(updated_at, str):
        updated_at_dt = parser.parse(updated_at)
    else:
        updated_at_dt = updated_at
    now = datetime.now(updated_at_dt.tzinfo)
    return now - updated_at_dt


def check_order_status(updated_at, num):
    time_difference = calculate_time_difference(updated_at)
    required_time = preparation_time(num)
    if time_difference <= required_time:
        remaining_time = required_time - time_difference
        remaining_time_in_second = round(remaining_time.total_seconds())
        remaining_time_rounded = timedelta(seconds=remaining_time_in_second)
        return f"Vaqt qoldi: {remaining_time_rounded}"

    else:
        return "Buyurtma kechikayapti!"


def check_order_difference(updated_at, user_lat, user_lon):
    time_difference = calculate_time_difference(updated_at)
    required_time = distance_time(distance(user_lat, user_lon))
    if time_difference <= required_time:
        remaining_time = required_time - time_difference
        remaining_time_in_second = round(remaining_time.total_seconds())
        remaining_time_rounded = timedelta(seconds=remaining_time_in_second)
        return f"Vaqt qoldi: {remaining_time_rounded}"

    else:
        return "Buyurtma kechikayapti!"


def is_within_24_hours(updated_at):
    # Ensure updated_at is a datetime object
    if isinstance(updated_at, str):
        updated_at_dt = datetime.fromisoformat(updated_at)  # Convert if it's a string
    else:
        updated_at_dt = updated_at  # If it's already a datetime object, use it directly

    # Make sure both times are timezone-aware (UTC in this case)
    now = datetime.now(timezone.utc)

    # Calculate the time difference
    time_difference = now - updated_at_dt
    return time_difference.total_seconds() < 24 * 3600  # Less than 24 hours
