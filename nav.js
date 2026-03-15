// ========== SHARED NAVIGATION & UI COMPONENTS ==========
(function() {
    'use strict';

    // Determine current page for active nav state
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    function isActive(page) {
        if (page === 'index.html' && (currentPage === '' || currentPage === 'index.html' || currentPage === '/')) return true;
        return currentPage === page;
    }

    function navLinkClass(page) {
        const base = 'nav-link transition-colors';
        return isActive(page) ? base + ' active text-[#C87533]' : base + ' text-gray-400 hover:text-white';
    }

    // ========== INSERT SHARED HTML ==========
    const sharedHTML = `
    <!-- Mobile Menu Overlay -->
    <div class="mobile-menu" id="mobile-menu">
        <a href="index.html">Home</a>
        <a href="products.html">Products</a>
        <a href="investor.html">Investors</a>
        <a href="contact.html">Contact</a>
    </div>

    <!-- Loading Screen -->
    <div id="loading-screen">
        <div class="loader"></div>
        <p style="color: var(--copper); margin-top: 20px; font-size: 14px; letter-spacing: 2px;">KURA MATERIALS</p>
    </div>

    <!-- Back to Top Button -->
    <div id="back-to-top">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
    </div>

    <!-- Scroll Progress Bar -->
    <div id="scroll-progress"></div>
    `;

    // Insert shared HTML at start of body
    document.body.insertAdjacentHTML('afterbegin', sharedHTML);

    // ========== INSERT NAVIGATION ==========
    const nav = document.createElement('nav');
    nav.id = 'main-nav';
    nav.innerHTML = `
        <div class="container mx-auto px-6 py-4 flex justify-between items-center">
            <a href="index.html" class="text-2xl font-bold gradient-text" style="text-decoration:none;">Kura Materials</a>
            <div class="hamburger md:hidden" id="hamburger">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div class="desktop-nav hidden md:flex gap-8 items-center">
                <a href="index.html" class="${navLinkClass('index.html')}">Home</a>
                <a href="products.html" class="${navLinkClass('products.html')}">Products</a>
                <a href="investor.html" class="${navLinkClass('investor.html')}">Investors</a>
                <a href="contact.html" class="btn-primary px-6 py-2 rounded-full text-sm font-semibold text-white inline-block" style="text-decoration:none;">Talk to Sales</a>
            </div>
        </div>
    `;
    // Insert nav after shared HTML (after scroll-progress)
    const scrollProgress = document.getElementById('scroll-progress');
    if (scrollProgress) {
        scrollProgress.after(nav);
    } else {
        document.body.prepend(nav);
    }

    // ========== PARTICLE BACKGROUND ==========
    const particlesDiv = document.createElement('div');
    particlesDiv.id = 'particles';
    particlesDiv.className = 'fixed inset-0 pointer-events-none overflow-hidden';
    particlesDiv.style.zIndex = '0';
    nav.after(particlesDiv);

    function createParticles() {
        const container = document.getElementById('particles');
        if (!container) return;
        const particleCount = window.innerWidth < 768 ? 0 : 30;
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            const size = Math.random() * 4 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 4 + 's';
            particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
            container.appendChild(particle);
        }
    }

    // ========== HAMBURGER MENU TOGGLE ==========
    function initHamburger() {
        const hamburger = document.getElementById('hamburger');
        const mobileMenu = document.getElementById('mobile-menu');
        if (!hamburger || !mobileMenu) return;

        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            mobileMenu.classList.toggle('active');
        });

        // Close menu when a link is clicked
        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                mobileMenu.classList.remove('active');
            });
        });
    }

    // ========== BACK TO TOP ==========
    function initBackToTop() {
        const btn = document.getElementById('back-to-top');
        if (!btn) return;

        window.addEventListener('scroll', function() {
            if (window.scrollY > 500) {
                btn.classList.add('show');
            } else {
                btn.classList.remove('show');
            }
        });

        btn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ========== SCROLL PROGRESS BAR ==========
    function initScrollProgress() {
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const progress = (scrollTop / scrollHeight) * 100;
            const bar = document.getElementById('scroll-progress');
            if (bar) bar.style.width = progress + '%';
        });
    }

    // ========== STICKY NAV ==========
    function initStickyNav() {
        window.addEventListener('scroll', function() {
            const navEl = document.getElementById('main-nav');
            if (!navEl) return;
            if (window.scrollY > 100) {
                navEl.classList.add('scrolled');
            } else {
                navEl.classList.remove('scrolled');
            }
        });
    }

    // ========== SMOOTH SCROLL FOR ANCHOR LINKS ==========
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    // ========== INTERSECTION OBSERVER FOR SCROLL ANIMATIONS ==========
    function initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');

                    // Trigger counter animation
                    if (entry.target.querySelector('.counter')) {
                        entry.target.querySelectorAll('.counter').forEach(function(counter) {
                            if (!counter.classList.contains('animated')) {
                                counter.classList.add('animated');
                                animateCounter(counter);
                            }
                        });
                    }

                    // Trigger circular progress
                    if (entry.target.querySelector('#progress-circle')) {
                        animateCircularProgress();
                    }
                }
            });
        }, observerOptions);

        document.querySelectorAll('.scroll-animate').forEach(function(el) {
            observer.observe(el);
        });
    }

    // ========== ANIMATED COUNTER ==========
    function animateCounter(element) {
        const target = parseInt(element.dataset.target);
        const duration = 2000;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(target * easeOutQuart);
            element.textContent = current;
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = target;
            }
        }

        requestAnimationFrame(update);
    }

    // ========== CIRCULAR PROGRESS ANIMATION ==========
    function animateCircularProgress() {
        const circle = document.getElementById('progress-circle');
        if (!circle) return;
        const radius = 90;
        const circumference = 2 * Math.PI * radius;
        const targetPercent = 95;
        const offset = circumference - (targetPercent / 100) * circumference;
        setTimeout(function() {
            circle.style.strokeDashoffset = offset;
        }, 500);
    }

    // ========== LOADING SCREEN ==========
    function initLoadingScreen() {
        window.addEventListener('load', function() {
            const ls = document.getElementById('loading-screen');
            if (ls) ls.classList.add('hidden');
        });
        // Fallback
        setTimeout(function() {
            const ls = document.getElementById('loading-screen');
            if (ls) ls.classList.add('hidden');
        }, 3000);
    }

    // ========== REDUCED MOTION ==========
    function initReducedMotion() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.querySelectorAll('.scroll-animate').forEach(function(el) {
                el.style.transition = 'none';
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
            document.querySelectorAll('.particle').forEach(function(p) {
                p.style.animation = 'none';
            });
        }
    }

    // ========== INITIALIZE EVERYTHING ==========
    document.addEventListener('DOMContentLoaded', function() {
        createParticles();
        initHamburger();
        initBackToTop();
        initScrollProgress();
        initStickyNav();
        initSmoothScroll();
        initScrollAnimations();
        initReducedMotion();
    });

    initLoadingScreen();
})();
