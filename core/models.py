import random
import string

from django.conf import settings
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Role(models.Model):
    """Модель для ролей"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название роли')
    description = models.TextField(blank=True, verbose_name='Описание роли')
    created_date = models.DateTimeField("Дата создания", auto_now_add=True)
    edit_date = models.DateTimeField(
        "Дата редактирования",
        auto_now=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

# Модель для хранения городов
class City(models.Model):
    # Поле для наименования города с максимальной длиной в 100 символов
    name = models.CharField(max_length=100, verbose_name='Наименование города')
    slug = models.SlugField(unique=True)
    created_date = models.DateTimeField("Дата создания", auto_now_add=True)
    edit_date = models.DateTimeField(
        "Дата редактирования",
        auto_now=True
    )
    published = models.BooleanField(default=True, verbose_name='Отобразить?')

    def __str__(self):
        # Возвращает строковое представление города для отображения в Django admin и других местах
        return self.name

    class Meta:
        verbose_name='Город'
        verbose_name_plural= 'Города'


class Configuration(models.Model):
    """Модель для хранения глобальных конфигураций системы"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Администратор')
    # Поле, определяющее, включена ли система оплаты
    enable_payment_system = models.BooleanField(default=True, verbose_name='Включить систему оплаты?')
    # Поле, определяющее, включен ли тестовый режим
    enable_test_mode = models.BooleanField(default=False, verbose_name='Включить тестовый режим?')
    city = models.ForeignKey(City, verbose_name='Город', on_delete=models.CASCADE)
    created_date = models.DateTimeField("Дата создания", auto_now_add=True)
    edit_date = models.DateTimeField(
        "Дата редактирования",
        auto_now=True
    )

    def __str__(self):
        # Возвращает строковое представление модели для отображения в Django admin
        return "Настроики системы"
    class Meta:
        verbose_name='Настроика системы'
        verbose_name_plural= 'Настроики системы'





# Наследуемая от стандартной модели пользователя Django для добавления дополнительных полей
class CustomUser(AbstractUser):
    # Связь с моделью City, позволяет пользователю выбирать город. Удаление города каскадно удаляет пользователя.
    city = models.ManyToManyField(City, related_name='cities', null=True, blank=True, verbose_name='Город')
    # Поле, определяющее роль
    roles = models.ManyToManyField(Role, related_name='users', verbose_name='Роли')
    created_date = models.DateTimeField("Дата создания", auto_now_add=True)
    edit_date = models.DateTimeField(
        "Дата редактирования",
        auto_now=True
    )

    def list_cities(self):
        return f"{', '.join([city.name for city in self.city.all()])}"

    list_cities.short_description = 'Привязанные города'



# Генерация случайного кода билета, состоящего из 10 символов
def generate_ticket_code():
    # Генерация строки из случайных букв и цифр длиной 10 символов
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class TicketPrice(models.Model):
    """Модель для хранения сумм билетов"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ticket_price', verbose_name='Кто установил цену')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма билета')
    city = models.ForeignKey(City, verbose_name='Город', on_delete=models.CASCADE)
    created_date = models.DateTimeField("Дата создания", auto_now_add=True)
    edit_date = models.DateTimeField(
        "Дата редактирования",
        auto_now=True
    )


    def __str__(self):
        return f"{self.amount} в городе {self.city}"

    class Meta:
        verbose_name='Стоимость билета'
        verbose_name_plural='Стоимость билета'



# Модель для хранения информации о билетах
class Ticket(models.Model):
    # Связывает билет с кассиром, который его продал. Если кассир удален, это поле будет null.
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tickets_cashier', verbose_name='Кассир')
    # Поле для хранения города, где был произведен платеж
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    # Поле для хранения времени покупки билета, по умолчанию текущее время
    purchase_time = models.DateTimeField(default=timezone.now, verbose_name='Начала действия билета')
    # Поле для хранения времени истечения действия билета
    expiration_time = models.DateTimeField(verbose_name='Срок действия билета')
    # Поле для хранения статуса активности билета, по умолчанию активен
    is_active = models.BooleanField(default=True, verbose_name='Действует?')
    # Флаг, указывающий, был ли платеж выполнен в тестовом режиме
    is_test_mode = models.BooleanField(default=False, verbose_name='Тестовый режим?')
    # Поле для хранения кода билета, может быть пустым или null
    ticket_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='Код билета')
    # Поле для хранения суммы платежа, с поддержкой 10 цифр до запятой и 2 после запятой
    amount = models.ForeignKey(TicketPrice, on_delete=models.PROTECT, verbose_name='Стоимость')


    def save(self, *args, **kwargs):
        # Обновляем статус активности перед сохранением
        self.is_active = timezone.now() < self.expiration_time
        # Если время истечения действия билета не установлено, устанавливаем его на 40 минут вперед от времени покупки
        if not self.expiration_time:
            self.expiration_time = self.purchase_time + timezone.timedelta(minutes=40)
        # Если код билета не установлен, генерируем новый код
        if not self.ticket_code:
            self.ticket_code = generate_ticket_code()
        # Если время действия билета не установлено, устанавливаем его на 40 минут вперед от времени платежа
        if not self.valid_until:
            self.valid_until = self.timestamp + timedelta(minutes=40)
        # Вызываем метод сохранения родительского класса для завершения процесса сохранения
        super().save(*args, **kwargs)

    def __str__(self):
        # Возвращаем строковое представление билета для отображения в Django admin и других местах
        return f"Билет продал(а) {self.cashier.username if self.cashier else 'Unknown'} - {'Действует' if self.is_active else 'Истек'}"

    class Meta:
        verbose_name='Билет'
        verbose_name_plural='Билеты'


# Модель для хранения информации о платежах
class Payment(models.Model):
    # Связывает платеж с билетом
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, related_name='processed_payments', verbose_name='Кассир')
    # Поле для автоматического сохранения времени, когда был выполнен платеж
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время платежа')

    class Meta:
        verbose_name='Платеж'
        verbose_name_plural='Платежи'


