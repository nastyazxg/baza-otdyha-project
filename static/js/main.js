document.addEventListener('DOMContentLoaded', function() {
    const burger = document.getElementById('burger-btn');
    const nav = document.getElementById('main-nav');
    
    if (burger && nav) {
        burger.addEventListener('click', function() {
            nav.classList.toggle('open');
        });
    }

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

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = this.querySelector('[name="password1"]');
            const password2 = this.querySelector('[name="password2"]');
            if (password && password2 && password.value !== password2.value) {
                e.preventDefault();
                alert('Пароли не совпадают');
            }
        });
    }

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
});