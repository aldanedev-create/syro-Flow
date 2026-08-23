// Image detail page controls (gallery/image_detail.html)
// Reads its config from data-* attributes on .image-display so this file
// can stay a plain, cacheable static asset with no server-rendered values.

(function () {
    const display = document.querySelector('.image-display');
    if (!display) return;

    const { title, fileUrl, siteName, deleteUrl, galleryUrl, csrfToken } = display.dataset;

    window.downloadImage = function () {
        const link = document.createElement('a');
        link.download = title;
        link.href = fileUrl;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    window.openFullscreen = function () {
        const img = document.querySelector('.main-image');
        if (!img) return;
        if (img.requestFullscreen) {
            img.requestFullscreen();
        } else if (img.webkitRequestFullscreen) {
            img.webkitRequestFullscreen();
        }
    };

    window.shareImage = function () {
        if (navigator.share) {
            navigator.share({
                title: title,
                text: 'Check out this image from ' + siteName,
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(window.location.href);
            alert('Link copied to clipboard!');
        }
    };

    window.deleteImage = function () {
        if (!confirm('Are you sure you want to delete this image? This action cannot be undone.')) {
            return;
        }
        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            }
        }).then(response => {
            if (response.ok) {
                window.location.href = galleryUrl;
            } else {
                alert('Failed to delete image. It may be in use.');
            }
        });
    };

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && document.fullscreenElement) {
            document.exitFullscreen();
        }
    });
})();
