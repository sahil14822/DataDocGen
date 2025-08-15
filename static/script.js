// Web Scraper & Document Generator JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('scrapeForm');
    const urlInput = document.getElementById('url');
    const scrapeBtn = document.getElementById('scrapeBtn');
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');
    
    // URL validation regex
    const urlRegex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    
    // No URL validation - just remove any styling
    urlInput.addEventListener('input', function() {
        this.classList.remove('is-valid', 'is-invalid');
    });
    
    // Temporarily disable JavaScript form handling to test
    // The form will submit naturally without any JavaScript interference
    
    // URL validation function
    function isValidUrl(url) {
        // Add protocol if missing
        if (!/^https?:\/\//i.test(url)) {
            url = 'https://' + url;
        }
        
        try {
            const urlObj = new URL(url);
            return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
        } catch (e) {
            return false;
        }
    }
    
    // Set loading state
    function setLoadingState(loading) {
        if (loading) {
            scrapeBtn.disabled = true;
            btnText.classList.add('d-none');
            btnLoading.classList.remove('d-none');
            urlInput.disabled = true;
        } else {
            scrapeBtn.disabled = false;
            btnText.classList.remove('d-none');
            btnLoading.classList.add('d-none');
            urlInput.disabled = false;
        }
    }
    
    // Show alert function
    function showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        
        const icon = type === 'danger' ? 'exclamation-triangle' : 'info-circle';
        alertDiv.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert alert
        const container = document.querySelector('.container');
        const formRow = document.querySelector('.row:has(.card)');
        container.insertBefore(alertDiv, formRow);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.classList.remove('show');
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, 150);
            }
        }, 5000);
    }
    
    // Handle page unload to reset loading state
    window.addEventListener('beforeunload', function() {
        setLoadingState(false);
    });
    
    // Reset loading state when page becomes visible again
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            setLoadingState(false);
        }
    });
    
    // Auto-focus URL input
    urlInput.focus();
    
    // Handle URL input placeholder cycling for better UX
    const placeholders = [
        'https://example.com/article',
        'https://news.ycombinator.com',
        'https://medium.com/@username/article',
        'https://blog.example.com/post'
    ];
    
    let placeholderIndex = 0;
    setInterval(() => {
        if (!urlInput.value && document.activeElement !== urlInput) {
            placeholderIndex = (placeholderIndex + 1) % placeholders.length;
            urlInput.placeholder = placeholders[placeholderIndex];
        }
    }, 3000);
    
    // Enhanced error handling for network issues
    window.addEventListener('online', function() {
        showAlert('Connection restored', 'success');
    });
    
    window.addEventListener('offline', function() {
        showAlert('No internet connection. Please check your network.', 'warning');
        setLoadingState(false);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
        
        // Escape to clear URL input
        if (e.key === 'Escape' && document.activeElement === urlInput) {
            urlInput.value = '';
            urlInput.classList.remove('is-valid', 'is-invalid');
        }
    });
});
