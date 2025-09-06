/**
 * Mobile-optimized JavaScript for EcoCarpool
 * Handles responsive behavior, touch interactions, and mobile-specific features
 */

class MobileHandler {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.sidebarOpen = false;
        
        this.init();
        this.bindEvents();
    }
    
    init() {
        this.createMobileElements();
        this.setupSwipeGestures();
        this.setupPullToRefresh();
        this.optimizeForTouch();
    }
    
    createMobileElements() {
        if (!this.isMobile) return;
        
        // Create mobile header if it doesn't exist
        if (!document.querySelector('.mobile-header')) {
            const header = document.createElement('div');
            header.className = 'mobile-header';
            header.innerHTML = `
                <button class="mobile-menu-btn" id="mobileMenuBtn">
                    <i class="fas fa-bars"></i>
                </button>
                <div class="mobile-logo">
                    <img src="/static/images/logo.png" alt="EcoCarpool" height="30">
                </div>
                <div class="mobile-actions">
                    <button class="btn btn-sm btn-outline-primary" id="mobileSearchBtn">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            `;
            document.body.insertBefore(header, document.body.firstChild);
        }
        
        // Create sidebar overlay
        if (!document.querySelector('.sidebar-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.id = 'sidebarOverlay';
            document.body.appendChild(overlay);
        }
    }
    
    bindEvents() {
        // Mobile menu toggle
        const menuBtn = document.getElementById('mobileMenuBtn');
        if (menuBtn) {
            menuBtn.addEventListener('click', () => this.toggleSidebar());
        }
        
        // Sidebar overlay click
        const overlay = document.getElementById('sidebarOverlay');
        if (overlay) {
            overlay.addEventListener('click', () => this.closeSidebar());
        }
        
        // Window resize
        window.addEventListener('resize', () => this.handleResize());
        
        // Orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.handleResize(), 100);
        });
        
        // Touch events for swipe gestures
        document.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        document.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        document.addEventListener('touchend', (e) => this.handleTouchEnd(e));
        
        // Prevent zoom on double tap for buttons
        document.addEventListener('touchend', (e) => {
            if (e.target.matches('button, .btn, input[type="submit"]')) {
                e.preventDefault();
            }
        });
    }
    
    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && overlay) {
            this.sidebarOpen = !this.sidebarOpen;
            
            if (this.sidebarOpen) {
                sidebar.classList.add('open');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            } else {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    }
    
    closeSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && overlay) {
            this.sidebarOpen = false;
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    handleResize() {
        const newIsMobile = window.innerWidth <= 768;
        
        if (newIsMobile !== this.isMobile) {
            this.isMobile = newIsMobile;
            
            if (!this.isMobile) {
                this.closeSidebar();
            }
        }
    }
    
    setupSwipeGestures() {
        // Swipe to open/close sidebar
        let startX = 0;
        let currentX = 0;
        let isDragging = false;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            isDragging = true;
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            currentX = e.touches[0].clientX;
        });
        
        document.addEventListener('touchend', () => {
            if (!isDragging) return;
            isDragging = false;
            
            const diffX = currentX - startX;
            
            // Swipe right to open sidebar (from left edge)
            if (startX < 50 && diffX > 100 && !this.sidebarOpen) {
                this.toggleSidebar();
            }
            
            // Swipe left to close sidebar
            if (diffX < -100 && this.sidebarOpen) {
                this.closeSidebar();
            }
        });
    }
    
    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let pullDistance = 0;
        let isPulling = false;
        let refreshThreshold = 80;
        
        const createRefreshIndicator = () => {
            const indicator = document.createElement('div');
            indicator.className = 'pull-refresh-indicator';
            indicator.innerHTML = '<i class="fas fa-sync-alt"></i>';
            indicator.style.cssText = `
                position: fixed;
                top: -50px;
                left: 50%;
                transform: translateX(-50%);
                width: 40px;
                height: 40px;
                background: var(--primary-color);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                transition: all 0.3s ease;
                z-index: 1001;
            `;
            document.body.appendChild(indicator);
            return indicator;
        };
        
        const indicator = createRefreshIndicator();
        
        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!isPulling) return;
            
            currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;
            
            if (pullDistance > 0 && window.scrollY === 0) {
                e.preventDefault();
                
                const progress = Math.min(pullDistance / refreshThreshold, 1);
                indicator.style.top = `${-50 + (progress * 70)}px`;
                indicator.style.transform = `translateX(-50%) rotate(${progress * 360}deg)`;
                
                if (progress >= 1) {
                    indicator.style.background = 'var(--success-color)';
                }
            }
        });
        
        document.addEventListener('touchend', () => {
            if (!isPulling) return;
            isPulling = false;
            
            if (pullDistance >= refreshThreshold) {
                // Trigger refresh
                indicator.style.top = '20px';
                indicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i>';
                
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Reset indicator
                indicator.style.top = '-50px';
                indicator.style.transform = 'translateX(-50%) rotate(0deg)';
                indicator.style.background = 'var(--primary-color)';
            }
            
            pullDistance = 0;
        });
    }
    
    optimizeForTouch() {
        // Add touch-friendly classes to interactive elements
        const touchElements = document.querySelectorAll('button, .btn, a, input, select, textarea');
        touchElements.forEach(element => {
            element.classList.add('touch-optimized');
        });
        
        // Improve form interactions
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                // Scroll element into view on focus
                setTimeout(() => {
                    input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            });
        });
    }
    
    handleTouchStart(e) {
        this.touchStartX = e.touches[0].clientX;
        this.touchStartY = e.touches[0].clientY;
    }
    
    handleTouchMove(e) {
        // Prevent default scrolling when swiping horizontally
        const touchX = e.touches[0].clientX;
        const touchY = e.touches[0].clientY;
        const diffX = Math.abs(touchX - this.touchStartX);
        const diffY = Math.abs(touchY - this.touchStartY);
        
        if (diffX > diffY && diffX > 10) {
            e.preventDefault();
        }
    }
    
    handleTouchEnd(e) {
        // Handle swipe gestures for cards and lists
        const touchEndX = e.changedTouches[0].clientX;
        const diffX = touchEndX - this.touchStartX;
        
        if (Math.abs(diffX) > 100) {
            const target = e.target.closest('.swipeable');
            if (target) {
                if (diffX > 0) {
                    this.handleSwipeRight(target);
                } else {
                    this.handleSwipeLeft(target);
                }
            }
        }
    }
    
    handleSwipeRight(element) {
        // Handle right swipe (e.g., mark as favorite)
        element.classList.add('swiped-right');
        setTimeout(() => element.classList.remove('swiped-right'), 300);
    }
    
    handleSwipeLeft(element) {
        // Handle left swipe (e.g., delete or archive)
        element.classList.add('swiped-left');
        setTimeout(() => element.classList.remove('swiped-left'), 300);
    }
}

// Utility functions for mobile optimization
const MobileUtils = {
    // Check if device is mobile
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },
    
    // Get device orientation
    getOrientation() {
        return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
    },
    
    // Vibrate device (if supported)
    vibrate(pattern = [100]) {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    },
    
    // Show mobile-friendly notification
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `mobile-notification mobile-notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'}-color);
            color: white;
            padding: 15px 20px;
            border-radius: var(--border-radius);
            z-index: 1002;
            box-shadow: var(--shadow-lg);
            animation: slideDown 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    },
    
    // Handle offline/online status
    setupOfflineHandler() {
        const showOfflineMessage = () => {
            this.showNotification('You are currently offline', 'warning', 5000);
        };
        
        const showOnlineMessage = () => {
            this.showNotification('Connection restored', 'success');
        };
        
        window.addEventListener('offline', showOfflineMessage);
        window.addEventListener('online', showOnlineMessage);
    },
    
    // Optimize images for mobile
    optimizeImages() {
        const images = document.querySelectorAll('img[data-mobile-src]');
        images.forEach(img => {
            if (this.isMobile()) {
                img.src = img.dataset.mobileSrc;
            }
        });
    }
};

// Initialize mobile handler when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MobileHandler();
    MobileUtils.setupOfflineHandler();
    MobileUtils.optimizeImages();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from { transform: translateX(-50%) translateY(-100%); }
        to { transform: translateX(-50%) translateY(0); }
    }
    
    @keyframes slideUp {
        from { transform: translateX(-50%) translateY(0); }
        to { transform: translateX(-50%) translateY(-100%); }
    }
    
    .touch-optimized {
        -webkit-tap-highlight-color: rgba(0, 0, 0, 0.1);
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        user-select: none;
    }
    
    .swipeable {
        transition: transform 0.3s ease;
    }
    
    .swiped-right {
        transform: translateX(20px);
        background-color: rgba(5, 150, 105, 0.1);
    }
    
    .swiped-left {
        transform: translateX(-20px);
        background-color: rgba(220, 38, 38, 0.1);
    }
`;
document.head.appendChild(style);
