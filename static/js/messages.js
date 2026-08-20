    (function() {
        'use strict';

        // Auto-dismiss after 5 seconds
        const messages = document.querySelectorAll('.message[data-dismissible="true"]');

        messages.forEach(message => {
            // Close button
            const closeBtn = message.querySelector('.message-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    dismissMessage(message);
                });
            }

            // Auto dismiss after 5 seconds (or 8 for errors/warnings)
            let delay = 5000;
            if (message.classList.contains('message-error') || 
                message.classList.contains('message-danger') ||
                message.classList.contains('message-warning')) {
                delay = 8000;
            }

            setTimeout(() => {
                dismissMessage(message);
            }, delay);

            // Dismiss on click anywhere (optional)
            message.addEventListener('click', function(e) {
                if (e.target === this || e.target.closest('.message-content')) {
                    dismissMessage(message);
                }
            });
        });

        function dismissMessage(message) {
            if (message.classList.contains('hiding')) return;
            
            message.classList.add('hiding');
            
            setTimeout(() => {
                message.remove();
                // If no messages left, remove container if empty
                const container = document.querySelector('.messages-container');
                if (container && !container.children.length) {
                    container.remove();
                }
            }, 300);
        }

        // Stack messages with proper spacing
        function updateMessagePositions() {
            const container = document.querySelector('.messages-container');
            if (!container) return;
            
            const messages = container.querySelectorAll('.message');
            messages.forEach((msg, index) => {
                msg.style.marginBottom = index < messages.length - 1 ? '0' : '';
            });
        }

        updateMessagePositions();

        // Observer to handle dynamic messages
        const observer = new MutationObserver(() => {
            updateMessagePositions();
        });

        const container = document.querySelector('.messages-container');
        if (container) {
            observer.observe(container, { childList: true });
        }

    })();
