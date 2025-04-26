class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.initialize();
    }

    initialize() {
        this.applyTheme();
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        document.body.classList.toggle('dark', this.theme === 'dark');
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.theme);
        this.applyTheme();
    }
} 