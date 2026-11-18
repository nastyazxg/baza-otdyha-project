from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint, CheckConstraint, Q


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Accommodation(models.Model):
    TYPE_CHOICES = [
        ("cabin", "Домик"),
        ("gazebo", "Беседка"),
        ("glamping", "Глэмпинг"),
    ]

    name = models.CharField(max_length=150, verbose_name="Название")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Тип объекта")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="accommodations", verbose_name="Категория"
    )
    base_capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Основная вместимость"
    )
    max_capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Максимальная вместимость"
    )
    description = models.TextField(verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Объект размещения"
        verbose_name_plural = "Объекты размещения"
        ordering = ["name"]
        constraints = [
            CheckConstraint(
                condition=Q(max_capacity__gte=models.F("base_capacity")),
                name="max_capacity_gte_base_capacity"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class SeasonalTariff(models.Model):
    SEASON_CHOICES = [
        ("low", "Низкий сезон"),
        ("high", "Высокий сезон"),
        ("weekend", "Выходные"),
        ("holiday", "Праздники"),
    ]

    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, related_name="tariffs", verbose_name="Объект"
    )
    season_name = models.CharField(max_length=50, choices=SEASON_CHOICES, verbose_name="Сезон")
    price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Цена за сутки"
    )
    min_booking_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(14)],
        verbose_name="Минимальный срок бронирования"
    )
    start_date = models.DateField(verbose_name="Начало сезона")
    end_date = models.DateField(verbose_name="Конец сезона")

    class Meta:
        verbose_name = "Сезонный тариф"
        verbose_name_plural = "Сезонные тарифы"
        ordering = ["accommodation", "start_date"]
        constraints = [
            CheckConstraint(
                condition=Q(end_date__gte=models.F("start_date")),
                name="end_date_gte_start_date"
            )
        ]

    def __str__(self):
        return f"{self.accommodation.name} — {self.get_season_name_display()}"


class AdditionalService(models.Model):
    TYPE_CHOICES = [
        ("bath", "Баня"),
        ("boat", "Лодка"),
        ("grill", "Мангал"),
        ("rental", "Прокат"),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Название услуги")
    service_type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Тип услуги")
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Цена"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Дополнительная услуга"
        verbose_name_plural = "Дополнительные услуги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает подтверждения"),
        ("confirmed", "Подтверждено"),
        ("checked_in", "Заселён"),
        ("checked_out", "Выехал"),
        ("cancelled", "Отменено"),
    ]

    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.PROTECT, related_name="bookings", verbose_name="Объект"
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="bookings", verbose_name="Пользователь"
    )
    check_in_date = models.DateField(verbose_name="Дата заезда")
    check_out_date = models.DateField(verbose_name="Дата выезда")
    base_guests_count = models.PositiveIntegerField(verbose_name="Количество основных гостей")
    extra_guests_count = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(2)],
        verbose_name="Дополнительные спальные места"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая стоимость")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-check_in_date"]
        constraints = [
            CheckConstraint(
                condition=Q(check_out_date__gt=models.F("check_in_date")),
                name="check_out_after_check_in"
            ),
            CheckConstraint(
                condition=Q(extra_guests_count__lte=2),
                name="extra_guests_max_2"
            )
        ]

    def __str__(self):
        return f"Бронь #{self.id}: {self.accommodation.name} ({self.check_in_date} — {self.check_out_date})"


class BookingService(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking_services", verbose_name="Бронирование"
    )
    service = models.ForeignKey(
        AdditionalService, on_delete=models.PROTECT, related_name="booking_services", verbose_name="Услуга"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")

    class Meta:
        verbose_name = "Дополнительная услуга в бронировании"
        verbose_name_plural = "Дополнительные услуги в бронированиях"
        constraints = [
            UniqueConstraint(fields=["booking", "service"], name="unique_booking_service")
        ]

    def __str__(self):
        return f"{self.booking} — {self.service.name}"


class Guest(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="guests", verbose_name="Бронирование"
    )
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    passport_number = models.CharField(max_length=20, blank=True, verbose_name="Паспорт")
    is_primary = models.BooleanField(default=False, verbose_name="Основной гость")

    class Meta:
        verbose_name = "Гость"
        verbose_name_plural = "Гости"
        ordering = ["-is_primary", "full_name"]

    def __str__(self):
        return f"{self.full_name} ({'основной' if self.is_primary else 'дополнительный'})"


class Deposit(models.Model):
    RETURN_STATUS_CHOICES = [
        ("not_paid", "Не оплачен"),
        ("paid", "Оплачен"),
        ("returned", "Возвращён"),
        ("partially_returned", "Возвращён частично"),
    ]

    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="deposit", verbose_name="Бронирование"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма залога")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата оплаты")
    return_status = models.CharField(
        max_length=20, choices=RETURN_STATUS_CHOICES, default="not_paid", verbose_name="Статус возврата"
    )
    return_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Сумма возврата"
    )
    return_reason = models.TextField(blank=True, verbose_name="Причина удержания")

    class Meta:
        verbose_name = "Залог"
        verbose_name_plural = "Залоги"

    def __str__(self):
        return f"Залог по брони #{self.booking.id}: {self.amount} руб."


class Cleaning(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("in_progress", "В процессе"),
        ("completed", "Выполнена"),
    ]

    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, related_name="cleanings", verbose_name="Объект"
    )
    booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="cleanings", verbose_name="Бронирование"
    )
    scheduled_date = models.DateField(verbose_name="Запланированная дата")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")

    class Meta:
        verbose_name = "Уборка"
        verbose_name_plural = "Уборки"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"Уборка {self.accommodation.name} на {self.scheduled_date}"


class Review(models.Model):
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="review", verbose_name="Бронирование"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Оценка"
    )
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв на бронь #{self.booking.id}: {self.rating}/5"