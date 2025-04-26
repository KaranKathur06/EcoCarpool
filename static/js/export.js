class ReportExporter {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('export-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.exportReport();
        });
    }

    async exportReport() {
        const formData = new FormData(document.getElementById('export-form'));
        const params = new URLSearchParams(formData);
        
        try {
            const response = await fetch(`/api/export-report?${params}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report-${new Date().toISOString()}.${formData.get('format')}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Export failed:', error);
            // Show error notification
        }
    }
} 