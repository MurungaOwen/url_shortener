// API Base URL
const API_BASE = 'http://localhost:8000';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadHealth();
    loadUrls();

    // Set up form submission
    document.getElementById('createUrlForm').addEventListener('submit', createShortUrl);

    // Set up search input
    document.getElementById('searchQuery').addEventListener('input', debounce(performSearch, 300));

    // Load stats when tab is clicked
    setInterval(loadHealth, 30000); // Update health every 30s
});

// Tab Switching
function switchTab(tab) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));

    // Reset all tab buttons
    document.querySelectorAll('.tab-button').forEach(el => {
        el.classList.remove('border-blue-600', 'text-blue-600');
        el.classList.add('border-transparent', 'text-gray-500');
    });

    // Show selected tab
    document.getElementById(`${tab}Content`).classList.remove('hidden');
    const tabButton = document.getElementById(`${tab}Tab`);
    tabButton.classList.add('border-blue-600', 'text-blue-600');
    tabButton.classList.remove('border-transparent', 'text-gray-500');

    // Load data for the tab
    if (tab === 'stats') loadStats();
    if (tab === 'urls') loadUrls();
}

// Health Check
async function loadHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        document.getElementById('totalUrls').textContent = `${data.total_urls} URLs`;
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// Create Short URL
async function createShortUrl(e) {
    e.preventDefault();

    const url = document.getElementById('originalUrl').value;
    const customCode = document.getElementById('customCode').value;

    const payload = { url };
    if (customCode) payload.custom_code = customCode;

    try {
        const response = await fetch(`${API_BASE}/shorten`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(data);
            document.getElementById('createUrlForm').reset();
            loadUrls();
            loadHealth();
        } else {
            showToast(data.detail || 'Error creating short URL', 'error');
        }
    } catch (error) {
        showToast('Error creating short URL', 'error');
        console.error(error);
    }
}

// Show Success Result
function showSuccess(data) {
    const resultDiv = document.getElementById('createResult');
    resultDiv.innerHTML = `
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-start">
                <i class="fas fa-check-circle text-green-600 mt-0.5 mr-3"></i>
                <div class="flex-1">
                    <p class="text-sm font-medium text-green-800 mb-2">URL shortened successfully!</p>
                    <div class="flex items-center space-x-2">
                        <input type="text" value="${data.short_url}" readonly
                            class="flex-1 px-3 py-1 bg-white border border-green-300 rounded text-sm">
                        <button onclick="copyToClipboard('${data.short_url}')"
                            class="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                            <i class="fas fa-copy mr-1"></i>Copy
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Load All URLs
async function loadUrls() {
    try {
        const response = await fetch(`${API_BASE}/api/urls`);
        const data = await response.json();

        const urlsList = document.getElementById('urlsList');

        if (data.urls.length === 0) {
            urlsList.innerHTML = '<p class="text-gray-500 text-center py-8">No URLs yet. Create one above!</p>';
            return;
        }

        urlsList.innerHTML = data.urls.map(url => createUrlCard(url)).join('');
    } catch (error) {
        console.error('Error loading URLs:', error);
    }
}

// Create URL Card
function createUrlCard(url) {
    return `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-2 mb-2">
                        <code class="text-blue-600 font-mono font-semibold">${url.short_code}</code>
                        <span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                            <i class="fas fa-eye mr-1"></i>${url.access_count || 0} views
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 truncate" title="${url.original_url}">
                        <i class="fas fa-link mr-1"></i>${url.original_url}
                    </p>
                    <p class="text-xs text-gray-400 mt-1">${url.short_url}</p>
                </div>
                <div class="flex items-center space-x-2 ml-4">
                    <button onclick="viewDetails('${url.short_code}')"
                        class="text-blue-600 hover:text-blue-700 p-2" title="View Details">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <button onclick="copyToClipboard('${url.short_url}')"
                        class="text-gray-600 hover:text-gray-700 p-2" title="Copy URL">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button onclick="updateUrl('${url.short_code}', '${url.original_url}')"
                        class="text-green-600 hover:text-green-700 p-2" title="Update URL">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="deleteUrl('${url.short_code}')"
                        class="text-red-600 hover:text-red-700 p-2" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

// View URL Details
async function viewDetails(shortCode) {
    try {
        const response = await fetch(`${API_BASE}/api/urls/${shortCode}`);
        const data = await response.json();

        alert(`
URL Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Short Code: ${data.short_code}
Original URL: ${data.original_url}
Short URL: ${data.short_url}
Access Count: ${data.access_count}
Created: ${data.created_at || 'N/A'}
        `);
    } catch (error) {
        showToast('Error loading details', 'error');
    }
}

// Update URL
async function updateUrl(shortCode, currentUrl) {
    const newUrl = prompt('Enter new URL:', currentUrl);
    if (!newUrl || newUrl === currentUrl) return;

    try {
        const response = await fetch(`${API_BASE}/api/urls/${shortCode}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: newUrl })
        });

        if (response.ok) {
            showToast('URL updated successfully', 'success');
            loadUrls();
        } else {
            const data = await response.json();
            showToast(data.detail || 'Error updating URL', 'error');
        }
    } catch (error) {
        showToast('Error updating URL', 'error');
    }
}

// Delete URL
async function deleteUrl(shortCode) {
    if (!confirm(`Delete short URL "${shortCode}"?`)) return;

    try {
        const response = await fetch(`${API_BASE}/api/urls/${shortCode}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('URL deleted successfully', 'success');
            loadUrls();
            loadHealth();
        } else {
            showToast('Error deleting URL', 'error');
        }
    } catch (error) {
        showToast('Error deleting URL', 'error');
    }
}

// Load Statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();

        const statsDiv = document.getElementById('statsData');
        statsDiv.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div class="bg-blue-50 rounded-lg p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm text-blue-600 font-medium">Total URLs</p>
                            <p class="text-3xl font-bold text-blue-900 mt-1">${data.total_urls}</p>
                        </div>
                        <i class="fas fa-link text-blue-400 text-4xl"></i>
                    </div>
                </div>
                <div class="bg-green-50 rounded-lg p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm text-green-600 font-medium">Total Accesses</p>
                            <p class="text-3xl font-bold text-green-900 mt-1">${data.total_accesses}</p>
                        </div>
                        <i class="fas fa-eye text-green-400 text-4xl"></i>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 class="font-semibold text-gray-700 mb-3">
                        <i class="fas fa-arrow-up text-green-600 mr-2"></i>Most Accessed
                    </h4>
                    <div class="space-y-2">
                        ${data.most_accessed.length > 0 ?
                            data.most_accessed.map(item => `
                                <div class="flex items-center justify-between bg-gray-50 p-3 rounded">
                                    <code class="text-sm font-mono text-blue-600">${item.short_code}</code>
                                    <span class="text-sm text-gray-600">${item.access_count} views</span>
                                </div>
                            `).join('') :
                            '<p class="text-gray-500 text-sm">No data yet</p>'
                        }
                    </div>
                </div>
                <div>
                    <h4 class="font-semibold text-gray-700 mb-3">
                        <i class="fas fa-arrow-down text-orange-600 mr-2"></i>Least Accessed
                    </h4>
                    <div class="space-y-2">
                        ${data.least_accessed.length > 0 ?
                            data.least_accessed.map(item => `
                                <div class="flex items-center justify-between bg-gray-50 p-3 rounded">
                                    <code class="text-sm font-mono text-blue-600">${item.short_code}</code>
                                    <span class="text-sm text-gray-600">${item.access_count} views</span>
                                </div>
                            `).join('') :
                            '<p class="text-gray-500 text-sm">No data yet</p>'
                        }
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Search URLs
async function performSearch() {
    const query = document.getElementById('searchQuery').value;

    if (!query) {
        document.getElementById('searchResults').innerHTML =
            '<p class="text-gray-500 text-center py-8">Enter a search term to find URLs</p>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        const resultsDiv = document.getElementById('searchResults');

        if (data.urls.length === 0) {
            resultsDiv.innerHTML = '<p class="text-gray-500 text-center py-8">No results found</p>';
            return;
        }

        resultsDiv.innerHTML = data.urls.map(url => createUrlCard(url)).join('');
    } catch (error) {
        console.error('Error searching:', error);
    }
}

// Utility Functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    toastMessage.textContent = message;
    toast.classList.remove('hidden', 'bg-gray-800', 'bg-green-600', 'bg-red-600');

    if (type === 'success') toast.classList.add('bg-green-600');
    else if (type === 'error') toast.classList.add('bg-red-600');
    else toast.classList.add('bg-gray-800');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

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
