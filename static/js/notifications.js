class NotificationSystem {
    constructor() {
        this.socket = io('http://localhost:8000');
        this.notifications = [];
        this.count = 0;
        this.setup();
    }

    setup() {
        this.socket.on('new_booking', (data) => {
            this.addNotification({
                type: 'booking',
                message: `New booking from ${data.user_name}`,
                time: new Date()
            });
        });

        this.socket.on('ride_completed', (data) => {
            this.addNotification({
                type: 'ride',
                message: `Ride #${data.ride_id} completed`,
                time: new Date()
            });
        });

        document.getElementById('notification-btn').addEventListener('click', () => {
            this.toggleNotificationPanel();
        });
    }

    addNotification(notification) {
        this.notifications.unshift(notification);
        this.count++;
        this.updateUI();
        this.showToast(notification);
    }

    updateUI() {
        const countElement = document.getElementById('notification-count');
        countElement.textContent = this.count;

        const listElement = document.getElementById('notification-list');
        listElement.innerHTML = this.notifications
            .map(n => this.renderNotification(n))
            .join('');
    }

    renderNotification(notification) {
        return `
            <div class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="flex items-center">
                    <i class="fas ${this.getIcon(notification.type)} mr-2"></i>
                    <p class="text-sm">${notification.message}</p>
                </div>
                <p class="text-xs text-gray-500 mt-1">
                    ${this.formatTime(notification.time)}
                </p>
            </div>
        `;
    }

    getIcon(type) {
        const icons = {
            booking: 'fa-calendar-check',
            ride: 'fa-car',
            payment: 'fa-credit-card'
        };
        return icons[type] || 'fa-bell';
    }

    formatTime(time) {
        return new Intl.RelativeTimeFormat('en', {
            numeric: 'auto'
        }).format(
            Math.floor((time - new Date()) / 60000),
            'minute'
        );
    }

    showToast(notification) {
        // Implementation for toast notifications
    }
} 