from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from .models import Accommodation, AdditionalService, Booking, Review
from .forms import RegisterForm


def home(request):
    """Главная страница — 3 популярных объекта из базы"""
    popular = Accommodation.objects.filter(is_active=True)[:3]
    return render(request, 'home.html', {'popular': popular})


from django.core.paginator import Paginator
from django.conf import settings

def catalog(request):
    """Каталог с фильтрацией и пагинацией"""
    objects = Accommodation.objects.filter(is_active=True)

    # Фильтры
    type_filter = request.GET.get('type')
    capacity = request.GET.get('capacity')
    search = request.GET.get('search')

    if type_filter:
        objects = objects.filter(type=type_filter)
    if capacity:
        objects = objects.filter(base_capacity__gte=int(capacity))
    if search:
        objects = objects.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # Пагинация по 20 записей
    paginator = Paginator(objects, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')
    objects_page = paginator.get_page(page)

    return render(request, 'catalog.html', {
        'objects': objects_page,
        'types': Accommodation.TYPE_CHOICES,
    })


def search(request):
    """Страница результатов поиска"""
    query = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '')
    capacity = request.GET.get('capacity', '')
    sort = request.GET.get('sort', 'name')

    objects = Accommodation.objects.filter(is_active=True)

    if query:
        objects = objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if type_filter:
        objects = objects.filter(type=type_filter)
    if capacity:
        objects = objects.filter(base_capacity__lte=int(capacity))

    if sort == 'price_asc':
        objects = objects.order_by('tariffs__price_per_day')
    elif sort == 'price_desc':
        objects = objects.order_by('-tariffs__price_per_day')
    elif sort == 'capacity':
        objects = objects.order_by('-base_capacity')
    else:
        objects = objects.order_by('name')

    paginator = Paginator(objects, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')
    objects_page = paginator.get_page(page)

    return render(request, 'search.html', {
        'objects': objects_page,
        'query': query,
        'objects_count': objects.count(),
        'types': Accommodation.TYPE_CHOICES,
    })


def object_detail(request, pk):
    """Карточка объекта"""
    obj = get_object_or_404(Accommodation, pk=pk, is_active=True)
    tariffs = obj.tariffs.all()
    services = AdditionalService.objects.filter(is_active=True)
    photos = obj.photos.all() if hasattr(obj, 'photos') else []
    main_photo = photos.filter(is_main=True).first() if photos else None

    return render(request, 'object_detail.html', {
        'object': obj,
        'tariffs': tariffs,
        'services': services,
        'photos': photos,
        'main_photo': main_photo,
    })


def about(request):
    """Статическая страница О базе"""
    return render(request, 'about.html')


def contacts(request):
    """Страница Контакты"""
    return render(request, 'contacts.html')


def register_view(request):
    """Регистрация"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Вход"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Выход"""
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('home')


@login_required
def profile_view(request):
    """Личный кабинет"""
    bookings = Booking.objects.filter(user=request.user).select_related('accommodation').order_by('-check_in_date')
    reviews = Review.objects.filter(booking__user=request.user).select_related('booking__accommodation').order_by('-created_at')

    bookings_count = bookings.count()
    active_bookings_count = bookings.filter(status__in=['pending', 'confirmed', 'checked_in']).count()
    reviews_count = reviews.count()

    return render(request, 'profile.html', {
        'bookings': bookings,
        'reviews': reviews,
        'bookings_count': bookings_count,
        'active_bookings_count': active_bookings_count,
        'reviews_count': reviews_count,
    })
from django.http import JsonResponse
from .forms import BookingForm, ContactForm, SubscriptionForm
from .models import ContactMessage
import json


def object_detail(request, pk):
    """Карточка объекта с формой бронирования"""
    obj = get_object_or_404(Accommodation, pk=pk, is_active=True)
    tariffs = obj.tariffs.all()
    services = AdditionalService.objects.filter(is_active=True)
    photos = obj.photos.all() if hasattr(obj, 'photos') else []
    main_photo = photos.filter(is_main=True).first() if photos else None

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.accommodation = obj
            booking.user = request.user
            booking.status = 'pending'
            booking.total_price = request.POST.get('total_price', 0)
            booking.save()
            messages.success(request, f'Бронирование #{booking.id} оформлено! Ожидайте подтверждения.')
            return redirect('profile')
    else:
        form = BookingForm()

    return render(request, 'object_detail.html', {
        'object': obj,
        'tariffs': tariffs,
        'services': services,
        'photos': photos,
        'main_photo': main_photo,
        'form': form,
    })


def contacts_view(request):
    """Страница контактов с формой обратной связи"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение отправлено! Мы ответим вам в ближайшее время.')
            return redirect('contacts')
    else:
        form = ContactForm()
    return render(request, 'contacts.html', {'form': form})


def subscribe_ajax(request):
    """AJAX-обработчик формы подписки"""
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # В реальном проекте здесь была бы запись в БД или отправка письма
            return JsonResponse({'success': True, 'message': f'Вы подписались на рассылку: {email}'})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Метод не разрешён'}, status=405)


def calculate_price(request):
    """AJAX-эндпоинт для расчёта стоимости бронирования"""
    if request.method == 'GET':
        object_id = request.GET.get('object_id')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = int(request.GET.get('guests', 1))

        try:
            obj = Accommodation.objects.get(pk=object_id)
            
            # Находим актуальный тариф
            from django.utils import timezone
            tariff = None
            if check_in:
                from datetime import datetime
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                tariff = obj.tariffs.filter(
                    start_date__lte=check_in_date,
                    end_date__gte=check_in_date
                ).first()
            
            if not tariff:
                tariff = obj.tariffs.first()
            
            price_per_day = float(tariff.price_per_day) if tariff else 3500.0
            
            # Считаем количество ночей
            if check_in and check_out:
                from datetime import datetime
                d1 = datetime.strptime(check_in, '%Y-%m-%d').date()
                d2 = datetime.strptime(check_out, '%Y-%m-%d').date()
                nights = (d2 - d1).days
                if nights <= 0:
                    return JsonResponse({'error': 'Некорректные даты'}, status=400)
            else:
                nights = 1
            
            total = price_per_day * nights
            
            # Доплата за доп. гостей
            if guests > obj.base_capacity:
                extra = guests - obj.base_capacity
                total += extra * 500 * nights
            
            return JsonResponse({
                'total': total,
                'price_per_day': price_per_day,
                'nights': nights,
                'min_booking_days': tariff.min_booking_days if tariff else 1,
            })
        except Accommodation.DoesNotExist:
            return JsonResponse({'error': 'Объект не найден'}, status=404)
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)