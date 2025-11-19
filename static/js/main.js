// Main JavaScript file for Seja Sua Management System

document.addEventListener('DOMContentLoaded', function() {
    // Highlight current page in navigation
    highlightCurrentPage();

    // Auto-save for notes (if on notes page)
    initializeAutoSave();
});

/**
 * Highlight the current page in the navigation menu
 */
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.main-nav a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Initialize auto-save functionality for notes
 */
function initializeAutoSave() {
    const noteTextarea = document.querySelector('textarea[name="content"]');
    if (noteTextarea) {
        let autoSaveTimer;

        noteTextarea.addEventListener('input', function() {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(() => {
                saveNoteDraft(this.value);
            }, 2000); // Auto-save after 2 seconds of inactivity
        });
    }
}

/**
 * Save note draft to local storage
 */
function saveNoteDraft(content) {
    const noteId = getNoteIdFromUrl();
    if (noteId) {
        localStorage.setItem(`note_draft_${noteId}`, content);
        showSaveIndicator();
    }
}

/**
 * Get note ID from URL
 */
function getNoteIdFromUrl() {
    const match = window.location.pathname.match(/\/note\/(\d+)/);
    return match ? match[1] : null;
}

/**
 * Show a save indicator
 */
function showSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.textContent = 'Rascunho salvo';
    indicator.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #c9a961;
        color: #3d2f22;
        padding: 10px 20px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;

    document.body.appendChild(indicator);

    // Fade in
    setTimeout(() => {
        indicator.style.opacity = '1';
    }, 10);

    // Fade out and remove
    setTimeout(() => {
        indicator.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(indicator);
        }, 300);
    }, 2000);
}

/**
 * Utility: Format currency to BRL
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

/**
 * Utility: Format date to Brazilian format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    }).format(date);
}

/**
 * Utility: Format datetime to Brazilian format
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Export utilities for use in other scripts
window.SejaSua = {
    formatCurrency,
    formatDate,
    formatDateTime
};
