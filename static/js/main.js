document.addEventListener('DOMContentLoaded', function() {
    // ===== БУРГЕР-МЕНЮ =====
    const burger = document.getElementById('burger-btn');
    const nav = document.getElementById('main-nav');
    
    if (burger && nav) {
        burger.addEventListener('click', function() {
            nav.classList.toggle('open');
        });
    }

    // ===== КНОПКИ ВМЕСТИМОСТИ В КАТАЛОГЕ =====
    const capBtns = document.querySelectorAll('.cap-btn');
    const capacityInput = document.getElementById('capacity-input');
    
    capBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            capBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            if (capacityInput) {
                capacityInput.value = this.dataset.value;
            }
        });
    });

    // ===== КЛИЕНТСКАЯ ВАЛИДАЦИЯ ФОРМЫ РЕГИСТРАЦИИ =====
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = this.querySelector('[name="password1"]');
            const password2 = this.querySelector('[name="password2"]');
            const email = this.querySelector('[name="email"]');
            
            if (email && !validateEmail(email.value)) {
                e.preventDefault();
                alert('Введите корректный email');
                return;
            }
            if (password && password2 && password.value !== password2.value) {
                e.preventDefault();
                alert('Пароли не совпадают');
                return;
            }
            if (password && password.value.length < 8) {
                e.preventDefault();
                alert('Пароль должен содержать минимум 8 символов');
                return;
            }
        });
    }

    // ===== КЛИЕНТСКАЯ ВАЛИДАЦИЯ ФОРМЫ ВХОДА =====
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = this.querySelector('[name="username"]');
            const password = this.querySelector('[name="password"]');
            if (username && !username.value.trim()) {
                e.preventDefault();
                alert('Введите логин');
            }
            if (password && !password.value) {
                e.preventDefault();
                alert('Введите пароль');
            }
        });
    }

    // ===== КЛИЕНТСКАЯ ВАЛИДАЦИЯ ФОРМЫ КОНТАКТОВ =====
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const email = this.querySelector('[name="email"]');
            const phone = this.querySelector('[name="phone"]');
            const message = this.querySelector('[name="message"]');
            
            if (email && !validateEmail(email.value)) {
                e.preventDefault();
                alert('Введите корректный email');
                return;
            }
            if (phone && phone.value && !validatePhone(phone.value)) {
                e.preventDefault();
                alert('Введите телефон в формате +7 900 000-00-00');
                return;
            }
            if (message && message.value.length < 10) {
                e.preventDefault();
                alert('Сообщение должно содержать минимум 10 символов');
                return;
            }
        });
    }

    // ===== AJAX-ПОДПИСКА В ФУТЕРЕ =====
    const subscribeForm = document.getElementById('subscribe-form');
    if (subscribeForm) {
        subscribeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = document.getElementById('subscribe-email');
            const messageDiv = document.getElementById('subscribe-message');
            
            if (!validateEmail(emailInput.value)) {
                messageDiv.textContent = 'Введите корректный email';
                messageDiv.className = 'subscribe-message error';
                return;
            }
            
            const formData = new FormData(this);
            
            fetch('/api/subscribe/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                },
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.textContent = data.message;
                    messageDiv.className = 'subscribe-message success';
                    emailInput.value = '';
                } else {
                    messageDiv.textContent = 'Ошибка подписки';
                    messageDiv.className = 'subscribe-message error';
                }
            })
            .catch(err => {
                messageDiv.textContent = 'Ошибка соединения';
                messageDiv.className = 'subscribe-message error';
            });
        });
    }

    // ===== AJAX-РАСЧЁТ СТОИМОСТИ БРОНИРОВАНИЯ =====
    const bookingForm = document.getElementById('booking-calc');
    if (bookingForm) {
        const objectId = bookingForm.dataset.objectId || window.location.pathname.split('/').filter(Boolean).pop();
        const checkIn = document.getElementById('check_in');
        const checkOut = document.getElementById('check_out');
        const guests = document.getElementById('id_base_guests_count');
        const extraGuests = document.getElementById('id_extra_guests_count');
        const totalPriceEl = document.getElementById('total-price');
        const totalPriceInput = document.getElementById('total-price-input');
        const minStayWarning = document.getElementById('min-stay-warning');

        function calculate() {
            if (checkIn.value && checkOut.value) {
                const d1 = new Date(checkIn.value);
                const d2 = new Date(checkOut.value);
                const nights = Math.ceil((d2 - d1) / (1000 * 60 * 60 * 24));
                
                if (nights <= 0) {
                    totalPriceEl.textContent = '0 ₽';
                    return;
                }

                // Проверка минимального срока в выходные
                const dayOfWeek = d1.getDay();
                if (nights < 2 && (dayOfWeek === 5 || dayOfWeek === 6)) {
                    minStayWarning.style.display = 'block';
                } else {
                    minStayWarning.style.display = 'none';
                }

                const guestCount = guests ? parseInt(guests.value) : 2;

                fetch(`/api/calculate/?object_id=${objectId}&check_in=${checkIn.value}&check_out=${checkOut.value}&guests=${guestCount}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.total) {
                            const formatted = data.total.toLocaleString('ru-RU');
                            totalPriceEl.textContent = formatted + ' ₽';
                            if (totalPriceInput) totalPriceInput.value = data.total;
                        }
                    })
                    .catch(err => console.error('Ошибка расчёта:', err));
            }
        }

        if (checkIn) checkIn.addEventListener('change', calculate);
        if (checkOut) checkOut.addEventListener('change', calculate);
        if (guests) guests.addEventListener('change', calculate);
        if (extraGuests) extraGuests.addEventListener('change', calculate);
    }

    // ===== МОДАЛЬНОЕ ОКНО ПОДТВЕРЖДЕНИЯ БРОНИРОВАНИЯ =====
    const confirmBtn = document.getElementById('confirm-booking-btn');
    const modal = document.getElementById('booking-modal');
    const modalCancel = document.getElementById('modal-cancel');
    const modalConfirm = document.getElementById('modal-confirm');

    if (confirmBtn && modal) {
        confirmBtn.addEventListener('click', function() {
            const checkIn = document.getElementById('check_in');
            const checkOut = document.getElementById('check_out');
            
            if (!checkIn.value || !checkOut.value) {
                alert('Выберите даты заезда и выезда');
                return;
            }
            
            const totalPrice = document.getElementById('total-price').textContent;
            document.getElementById('modal-text').textContent = 
                `Заезд: ${checkIn.value}, Выезд: ${checkOut.value}. Итого: ${totalPrice}. Подтвердить бронирование?`;
            modal.style.display = 'flex';
        });

        if (modalCancel) {
            modalCancel.addEventListener('click', function() {
                modal.style.display = 'none';
            });
        }

        if (modalConfirm) {
            modalConfirm.addEventListener('click', function() {
                bookingForm.submit();
            });
        }

        // Закрытие по клику вне модального окна
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function validatePhone(phone) {
        const cleaned = phone.replace(/[\s\-\+\(\)]/g, '');
        return /^\d{10,11}$/.test(cleaned);
    }
});