// Utilitários para obter CSRF token do Django

export function getCsrfToken() {
    // Tentar obter do cookie primeiro
    const cookieValue = getCsrfTokenFromCookie();
    if (cookieValue) {
        return cookieValue;
    }
    
    // Fallback: tentar obter do input hidden no DOM
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // Fallback: tentar obter do meta tag
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    
    console.warn('CSRF token não encontrado');
    return '';
}

export function getCsrfTokenFromCookie() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export function setupCsrfHeaders(options = {}) {
    const token = getCsrfToken();
    return {
        ...options,
        headers: {
            'X-CSRFToken': token,
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
}