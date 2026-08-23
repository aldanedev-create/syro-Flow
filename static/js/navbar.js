    (function() {
        'use strict';

        // Mobile Toggle
        const toggle = document.querySelector('.navbar-toggle');
        const menu = document.querySelector('.navbar-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function() {
                this.classList.toggle('active');
                menu.classList.toggle('active');
                this.setAttribute('aria-expanded', menu.classList.contains('active'));
            });
        }

        // Dropdown Toggles
        document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                const dropdownId = this.dataset.dropdown;
                const dropdown = document.getElementById(dropdownId);
                if (dropdown) {
                    const isOpen = dropdown.classList.toggle('show');
                    this.setAttribute('aria-expanded', isOpen);
                }
            });
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function(e) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                if (!menu.closest('.nav-item').contains(e.target)) {
                    menu.classList.remove('show');
                    const toggle = menu.closest('.nav-item').querySelector('.dropdown-toggle');
                    if (toggle) toggle.setAttribute('aria-expanded', 'false');
                }
            });
        });

        // Search Overlay
        const searchToggle = document.querySelector('.search-toggle');
        const searchOverlay = document.querySelector('.search-overlay');
        const searchClose = document.querySelector('.search-close');
        const searchInput = document.querySelector('.search-input-overlay');

        if (searchToggle && searchOverlay) {
            searchToggle.addEventListener('click', function() {
                searchOverlay.classList.add('active');
                if (searchInput) {
                    setTimeout(() => searchInput.focus(), 300);
                }
                document.body.style.overflow = 'hidden';
            });

            const closeSearch = function() {
                searchOverlay.classList.remove('active');
                document.body.style.overflow = '';
                if (searchInput) searchInput.value = '';
            };

            if (searchClose) {
                searchClose.addEventListener('click', closeSearch);
            }

            searchOverlay.addEventListener('click', function(e) {
                if (e.target === this) closeSearch();
            });

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
                    closeSearch();
                }
            });
        }

        // Close mobile menu on link click
        document.querySelectorAll('.navbar-nav a').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 992) {
                    menu?.classList.remove('active');
                    toggle?.classList.remove('active');
                    toggle?.setAttribute('aria-expanded', 'false');
                }
            });
        });

    })();
