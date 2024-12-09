from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------- User -----------------------------------------------------#

class User(AbstractUser, Base):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('user', 'User')
    ]
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=13, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    username = None

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"Email: {self.email}\nRole: {self.role}"


# --------------------------------------------- Menu -------------------------------------------------- #

class Menu(Base):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


# -------------------------------------------- Order ----------------------------------------------------- #

class Order(Base):
    STATUS_CHOICES = [
        ('yangi', 'Yangi'),
        ('jarayonda', 'Jarayonda'),
        ('tayyorlanmoqda', 'Tayyorlanmoqda'),
        ('bekor qilindi', 'Bekor qilindi'),
            ('yo\'lda', 'Yo\'lda'),
        ('tugallandi', 'Tugallandi')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='yangi')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"Status: {self.status}\nTo\'lov summasi: {self.price}\nBarcha buyurtmalar: {self.quantity}"


# ------------------------------------------------- Basket ------------------------------------------------- #

class Basket(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    food = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.price = self.food.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food.name} * {self.quantity} = {self.price}"
