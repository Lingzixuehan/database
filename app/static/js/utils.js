/**
 * Utility functions for frontend performance optimization.
 */

/**
 * Debounce function to limit rate of function execution.
 * @param {Function} func - The function to debounce
 * @param {number} wait - The delay in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function to limit execution to once per interval.
 * @param {Function} func - The function to throttle
 * @param {number} limit - The interval in milliseconds
 * @returns {Function} - Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Create a pagination object.
 * @param {number} totalItems - Total number of items
 * @param {number} itemsPerPage - Items per page
 * @param {number} currentPage - Current page number
 * @returns {Object} - Pagination info
 */
function createPagination(totalItems, itemsPerPage = 10, currentPage = 1) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

    return {
        totalItems,
        itemsPerPage,
        currentPage,
        totalPages,
        startIndex,
        endIndex,
        hasNext: currentPage < totalPages,
        hasPrev: currentPage > 1
    };
}

/**
 * Render pagination controls.
 * @param {Object} pagination - Pagination object
 * @param {Function} onPageChange - Callback when page changes
 * @returns {HTMLElement} - Pagination element
 */
function renderPaginationControls(pagination, onPageChange) {
    const container = document.createElement('nav');
    container.className = 'pagination-container mt-3';
    container.setAttribute('aria-label', 'Page navigation');

    const ul = document.createElement('ul');
    ul.className = 'pagination justify-content-center';

    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${!pagination.hasPrev ? 'disabled' : ''}`;
    const prevLink = document.createElement('a');
    prevLink.className = 'page-link';
    prevLink.href = '#';
    prevLink.textContent = 'Previous';
    prevLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (pagination.hasPrev) {
            onPageChange(pagination.currentPage - 1);
        }
    });
    prevLi.appendChild(prevLink);
    ul.appendChild(prevLi);

    // Page numbers
    const maxPages = 5;
    let startPage = Math.max(1, pagination.currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(pagination.totalPages, startPage + maxPages - 1);

    if (endPage - startPage < maxPages - 1) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === pagination.currentPage ? 'active' : ''}`;
        const link = document.createElement('a');
        link.className = 'page-link';
        link.href = '#';
        link.textContent = i;
        link.addEventListener('click', (e) => {
            e.preventDefault();
            onPageChange(i);
        });
        li.appendChild(link);
        ul.appendChild(li);
    }

    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${!pagination.hasNext ? 'disabled' : ''}`;
    const nextLink = document.createElement('a');
    nextLink.className = 'page-link';
    nextLink.href = '#';
    nextLink.textContent = 'Next';
    nextLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (pagination.hasNext) {
            onPageChange(pagination.currentPage + 1);
        }
    });
    nextLi.appendChild(nextLink);
    ul.appendChild(nextLi);

    container.appendChild(ul);

    // Info text
    const info = document.createElement('div');
    info.className = 'text-center text-muted small mt-2';
    info.textContent = `Showing ${pagination.startIndex + 1}-${pagination.endIndex} of ${pagination.totalItems} items`;
    container.appendChild(info);

    return container;
}

/**
 * Lazy load images with Intersection Observer.
 * @param {string} selector - CSS selector for images
 */
function lazyLoadImages(selector = 'img[data-src]') {
    const images = document.querySelectorAll(selector);

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

/**
 * Simple in-memory cache.
 */
class SimpleCache {
    constructor(ttl = 60000) { // Default TTL: 1 minute
        this.cache = new Map();
        this.ttl = ttl;
    }

    set(key, value) {
        this.cache.set(key, {
            value,
            expiry: Date.now() + this.ttl
        });
    }

    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;

        if (Date.now() > item.expiry) {
            this.cache.delete(key);
            return null;
        }

        return item.value;
    }

    has(key) {
        return this.get(key) !== null;
    }

    clear() {
        this.cache.clear();
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        debounce,
        throttle,
        createPagination,
        renderPaginationControls,
        lazyLoadImages,
        SimpleCache
    };
}
