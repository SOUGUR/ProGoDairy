// notifications.js - Self-contained notification system for GoProDairy Milk Logistics App
(function () {
    // Inject CSS once
    if (!document.getElementById('go-pro-dairy-notifications-styles')) {
        const style = document.createElement('style');
        style.id = 'go-pro-dairy-notifications-styles';
        style.textContent = `
            #notification-container .notification {
                margin-bottom: 12px;
                padding: 16px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                display: flex;
                align-items: flex-start;
                gap: 12px;
                max-width: 400px;
                opacity: 0;
                transform: translateX(-20px);
                transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                color: #2d3748;
                pointer-events: auto;
                border: 1px solid;
                border-left-width: 5px;
                position: relative;
                overflow: hidden;
                background: white;
            }

            #notification-container .notification::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
            }

            .notification-icon {
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                margin-top: 1px;
                border-radius: 50%;
                background: rgba(255,255,255,0.9);
            }

            .notification-message {
                flex: 1;
                word-wrap: break-word;
                font-weight: 500;
                color: #2d3748;
            }

            .notification-close {
                background: rgba(255,255,255,0.8);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                color: #718096;
                padding: 4px 6px;
                margin-left: 8px;
                opacity: 0.7;
                transition: all 0.2s ease;
                flex-shrink: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            }

            .notification-close:hover {
                opacity: 1;
                background: rgba(255,255,255,0.9);
                transform: scale(1.1);
                color: #2d3748;
            }

            /* Success - Milk Collection Theme */
            .notification-success {
                background: linear-gradient(135deg, #f0fff4, #ffffff);
                border-color: #38a169;
                border-left-color: #38a169;
                box-shadow: 0 4px 20px rgba(56, 161, 105, 0.2);
            }

            .notification-success .notification-icon {
                background: rgba(56, 161, 105, 0.1);
                color: #38a169;
            }

            /* Error - Quality Alert Theme */
            .notification-error {
                background: linear-gradient(135deg, #fff5f5, #ffffff);
                border-color: #e53e3e;
                border-left-color: #e53e3e;
                box-shadow: 0 4px 20px rgba(229, 62, 62, 0.2);
            }

            .notification-error .notification-icon {
                background: rgba(229, 62, 62, 0.1);
                color: #e53e3e;
            }

            /* Warning - Temperature Alert Theme */
            .notification-warning {
                background: linear-gradient(135deg, #fffaf0, #ffffff);
                border-color: #dd6b20;
                border-left-color: #dd6b20;
                box-shadow: 0 4px 20px rgba(221, 107, 32, 0.2);
            }

            .notification-warning .notification-icon {
                background: rgba(221, 107, 32, 0.1);
                color: #dd6b20;
            }

            /* Info - Logistics Theme (Matches your app's primary color) */
            .notification-info {
                background: linear-gradient(135deg, #ebf8ff, #ffffff);
                border-color: #2c5aa0;
                border-left-color: #2c5aa0;
                box-shadow: 0 4px 20px rgba(44, 90, 160, 0.2);
            }

            .notification-info .notification-icon {
                background: rgba(44, 90, 160, 0.1);
                color: #2c5aa0;
            }

            /* Dairy-specific status types */
            .notification-collection {
                background: linear-gradient(135deg, #f0fff4, #ffffff);
                border-color: #2c5aa0;
                border-left-color: #2c5aa0;
                box-shadow: 0 4px 20px rgba(44, 90, 160, 0.2);
            }

            .notification-collection .notification-icon {
                background: rgba(44, 90, 160, 0.1);
                color: #2c5aa0;
            }

            .notification-quality {
                background: linear-gradient(135deg, #fffaf0, #ffffff);
                border-color: #d69e2e;
                border-left-color: #d69e2e;
                box-shadow: 0 4px 20px rgba(214, 158, 46, 0.2);
            }

            .notification-quality .notification-icon {
                background: rgba(214, 158, 46, 0.1);
                color: #d69e2e;
            }

            .notification-transfer {
                background: linear-gradient(135deg, #e6fffa, #ffffff);
                border-color: #319795;
                border-left-color: #319795;
                box-shadow: 0 4px 20px rgba(49, 151, 149, 0.2);
            }

            .notification-transfer .notification-icon {
                background: rgba(49, 151, 149, 0.1);
                color: #319795;
            }

            /* Animation for new notifications */
            @keyframes slideInNotification {
                0% {
                    opacity: 0;
                    transform: translateX(-20px);
                }
                100% {
                    opacity: 1;
                    transform: translateX(0);
                }
            }

            @keyframes slideOutNotification {
                0% {
                    opacity: 1;
                    transform: translateX(0);
                }
                100% {
                    opacity: 0;
                    transform: translateX(-20px);
                }
            }

            /* Responsive design */
            @media (max-width: 768px) {
                #notification-container {
                    bottom: 10px;
                    left: 10px;
                    right: 10px;
                }

                #notification-container .notification {
                    max-width: none;
                    margin-bottom: 8px;
                    padding: 14px 16px;
                }
            }

            /* Hover effects */
            #notification-container .notification:hover {
                transform: translateX(0) scale(1.02);
                box-shadow: 0 6px 25px rgba(0,0,0,0.2);
            }

            /* Progress bar for auto-dismiss */
            .notification-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: linear-gradient(90deg, currentColor, rgba(255,255,255,0.8));
                width: 100%;
                transform: scaleX(1);
                transform-origin: left;
                transition: transform linear;
                border-radius: 0 0 8px 8px;
            }
        `;
        document.head.appendChild(style);
    }

    class NotificationManager {
        constructor() {
            this.container = null;
            this.initContainer();
        }

        initContainer() {
            if (!document.getElementById('notification-container')) {
                const container = document.createElement('div');
                container.id = 'notification-container';
                container.style.position = 'fixed';
                container.style.bottom = '20px';
                container.style.left = '20px';
                container.style.zIndex = '9999';
                container.style.pointerEvents = 'none';
                document.body.appendChild(container);
                this.container = container;
            } else {
                this.container = document.getElementById('notification-container');
            }
        }

        show(message, type = 'info', duration = 5000) {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <div class="notification-icon">${this.getIcon(type)}</div>
                <div class="notification-message">${message}</div>
                <button class="notification-close">&times;</button>
                <div class="notification-progress"></div>
            `;
            notification.style.pointerEvents = 'auto';

            this.container.appendChild(notification);

            // Add progress bar animation
            const progressBar = notification.querySelector('.notification-progress');
            if (progressBar && duration > 0) {
                progressBar.style.transition = `transform ${duration}ms linear`;
                progressBar.style.transform = 'scaleX(0)';
            }

            // Auto-dismiss
            const autoDismissTimer = duration > 0 ? setTimeout(() => {
                this.fadeOutAndRemove(notification);
            }, duration) : null;

            // Close on click
            const closeButton = notification.querySelector('.notification-close');
            closeButton.addEventListener('click', () => {
                if (autoDismissTimer) clearTimeout(autoDismissTimer);
                this.fadeOutAndRemove(notification);
            });

            // Fade in with animation
            requestAnimationFrame(() => {
                notification.style.animation = 'slideInNotification 0.4s ease-out forwards';
            });
        }

        getIcon(type) {
            switch (type) {
                case 'success':
                    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';
                case 'error':
                    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>';
                case 'warning':
                    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>';
                case 'collection':
                    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>'; // Play icon for collection
                case 'quality':
                    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>'; // Star icon for quality
                case 'transfer':
                    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>'; // Copy icon for transfer
                default:
                    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>';
            }
        }

        fadeOutAndRemove(notification) {
            notification.style.animation = 'slideOutNotification 0.3s ease-in forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }

    // Initialize singleton
    const notificationManager = new NotificationManager();

    // Expose globally
    window.showNotification = function (message, type = 'info', duration = 5000) {
        notificationManager.show(message, type, duration);
    };

    // Optional: support module exports (e.g., for bundlers)
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = notificationManager;
    }
})();



// reference
// Different colors for other types:

// Red for 'error'

// Orange for 'warning'

// Blue for 'info'

// Blue for 'collection'

// Yellow for 'quality'

// Teal for 'transfer'