    // Optional: Smooth scroll to top when changing page
    document.querySelectorAll('.pagination-link:not(.disabled)').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.includes('page=')) {
                e.preventDefault();
                window.location.href = href;
                // Smooth scroll to top after navigation
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    });
