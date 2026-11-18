from django.contrib import admin
from .models import (
    Category, Accommodation, SeasonalTariff, AdditionalService,
    Booking, BookingService, Guest, Deposit, Cleaning, Review
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'category', 'base_capacity', 'max_capacity', 'is_active')
    list_filter = ('type', 'category', 'is_active')
    search_fields = ('name',)


@admin.register(SeasonalTariff)
class SeasonalTariffAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'season_name', 'price_per_day', 'min_booking_days', 'start_date', 'end_date')
    list_filter = ('season_name', 'accommodation')


@admin.register(AdditionalService)
class AdditionalServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'price', 'is_active')
    list_filter = ('service_type', 'is_active')


class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 0


class GuestInline(admin.TabularInline):
    model = Guest
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'accommodation', 'user', 'check_in_date', 'check_out_date', 'status', 'total_price')
    list_filter = ('status', 'accommodation', 'check_in_date')
    search_fields = ('user__username', 'accommodation__name')
    inlines = [BookingServiceInline, GuestInline]


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'return_status', 'paid_at')
    list_filter = ('return_status',)


@admin.register(Cleaning)
class CleaningAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'scheduled_date', 'status', 'cost')
    list_filter = ('status', 'scheduled_date')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'created_at')
    list_filter = ('rating',)