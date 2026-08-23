// Syro Flow - global site behavior loaded on every page (base.html)

document.addEventListener('DOMContentLoaded', function () {
    // Smooth-scroll for same-page anchor links
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(function (link) {
        link.addEventListener('click', function (e) {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Open external links in a new tab safely
    document.querySelectorAll('a[href^="http"]').forEach(function (link) {
        if (link.hostname !== window.location.hostname) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });
});
