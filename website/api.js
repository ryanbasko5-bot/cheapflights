/**
 * FareGlitch API Client
 * 
 * Handles authentication and deal fetching from the backend API.
 */

// Auto-detect API URL based on environment
const API_BASE_URL = (() => {
    // In Codespaces, construct the API URL from the current hostname
    if (window.location.hostname.includes('app.github.dev')) {
        // Extract the codespace name and construct API URL
        // Format: https://codespace-name-8888.app.github.dev -> https://codespace-name-8000.app.github.dev
        const apiUrl = window.location.origin.replace('-8888.', '-8000.');
        console.log('🔧 Codespaces detected - API URL:', apiUrl);
        return apiUrl;
    }
    // Local development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    // Default fallback
    console.log('⚠️ Using default API URL');
    return 'http://localhost:8000';
})();

console.log('✅ FareGlitch API configured:', API_BASE_URL);

class FareGlitchAPI {
    constructor() {
        this.token = localStorage.getItem('fareglitch_token');
    }

    /**
     * Get authorization headers
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    /**
     * Login with email/phone
     */
    async login(email, phoneNumber = null) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email: email,
                    phone_number: phoneNumber
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            this.token = data.access_token;
            localStorage.setItem('fareglitch_token', this.token);
            localStorage.setItem('fareglitch_user', JSON.stringify(data.subscriber));
            
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    /**
     * Logout
     */
    logout() {
        this.token = null;
        localStorage.removeItem('fareglitch_token');
        localStorage.removeItem('fareglitch_user');
    }

    /**
     * Get current user info
     */
    getCurrentUser() {
        const userStr = localStorage.getItem('fareglitch_user');
        return userStr ? JSON.parse(userStr) : null;
    }

    /**
     * Check if user is premium member
     */
    isPremiumMember() {
        const user = this.getCurrentUser();
        return user && user.is_premium === true;
    }

    /**
     * Fetch active deals
     */
    async getActiveDeals(limit = 10) {
        try {
            const response = await fetch(
                `${API_BASE_URL}/deals/active?limit=${limit}`,
                { headers: this.getHeaders() }
            );

            if (!response.ok) {
                throw new Error('Failed to fetch deals');
            }

            const deals = await response.json();
            return deals;
        } catch (error) {
            console.error('Error fetching deals:', error);
            return [];
        }
    }

    /**
     * Fetch specific deal
     */
    async getDeal(dealNumber) {
        try {
            const response = await fetch(
                `${API_BASE_URL}/deals/${dealNumber}`,
                { headers: this.getHeaders() }
            );

            if (!response.ok) {
                throw new Error('Deal not found');
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching deal:', error);
            throw error;
        }
    }

    /**
     * Get current user details
     */
    async getMe() {
        if (!this.token) {
            return null;
        }

        try {
            const response = await fetch(
                `${API_BASE_URL}/auth/me`,
                { headers: this.getHeaders() }
            );

            if (!response.ok) {
                // Token invalid, clear it
                this.logout();
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching user:', error);
            this.logout();
            return null;
        }
    }
}

// Create global API instance
window.fareglitchAPI = new FareGlitchAPI();

/**
 * Format currency with proper symbol
 */
function formatCurrency(amount, currency = 'USD') {
    const symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'AUD': 'A$',
        'CAD': 'C$',
        'JPY': '¥',
        'HKD': 'HK$',
        'SGD': 'S$',
        'NZD': 'NZ$',
        'CNY': '¥',
        'INR': '₹',
        'KRW': '₩',
        'THB': '฿',
        'MYR': 'RM',
        'IDR': 'Rp',
        'PHP': '₱',
        'AED': 'AED ',
        'QAR': 'QAR ',
        'ILS': '₪',
        'ZAR': 'R',
        'BRL': 'R$',
        'MXN': 'MX$'
    };
    
    const symbol = symbols[currency] || currency + ' ';
    
    // Special formatting for certain currencies
    if (['JPY', 'KRW', 'IDR'].includes(currency)) {
        // No decimals for these currencies
        return `${symbol}${Math.round(amount).toLocaleString()}`;
    }
    
    return `${symbol}${Math.round(amount).toLocaleString()}`;
}

/**
 * Calculate time since published
 */
function getTimeSincePublished(publishedAt) {
    const now = new Date();
    const published = new Date(publishedAt);
    const hoursDiff = (now - published) / (1000 * 60 * 60);
    
    if (hoursDiff < 1) {
        const minutesDiff = Math.round((now - published) / (1000 * 60));
        return `${minutesDiff} min ago`;
    } else if (hoursDiff < 24) {
        return `${Math.round(hoursDiff)} hrs ago`;
    } else {
        return `${Math.round(hoursDiff / 24)} days ago`;
    }
}

/**
 * Check if deal is available (for non-members, check 1-hour delay)
 */
function isDealAvailable(deal) {
    const user = window.fareglitchAPI.getCurrentUser();
    
    // Premium members see all deals
    if (user && user.is_premium) {
        return true;
    }
    
    // Non-members need to wait 1 hour
    if (!deal.published_at) {
        return false;
    }
    
    const published = new Date(deal.published_at);
    const now = new Date();
    const hoursDiff = (now - published) / (1000 * 60 * 60);
    
    return hoursDiff >= 1.0;
}

/**
 * Render a deal card
 */
function renderDealCard(deal) {
    const isAvailable = isDealAvailable(deal);
    const isPremium = window.fareglitchAPI.isPremiumMember();
    
    // Check if it's a mistake fare (>50% savings = likely mistake)
    const isMistakeFare = deal.savings_percentage >= 50;
    
    const statusBadge = isAvailable 
        ? (isMistakeFare 
            ? '<span style="background: linear-gradient(135deg, #FF4444, #FF0000); color: white; padding: 0.5rem 1rem; border-radius: 50px; font-size: 0.75rem; font-weight: 700; animation: pulse 2s infinite;">⚡ MISTAKE FARE</span>'
            : '<span style="background: #7DB84D; color: white; padding: 0.5rem 1rem; border-radius: 50px; font-size: 0.75rem; font-weight: 700;">ACTIVE DEAL</span>')
        : `<span style="background: #FFA500; color: white; padding: 0.5rem 1rem; border-radius: 50px; font-size: 0.75rem; font-weight: 700;">MEMBERS ONLY</span>`;
    
    const timeInfo = deal.published_at 
        ? `<p style="font-family: 'Inter', sans-serif; color: #626784; font-size: 0.95rem; margin: 0; font-weight: 500;">⏱️ Published ${getTimeSincePublished(deal.published_at)}</p>`
        : '';
    
    // Booking button - only show if deal is available AND has a booking link
    const bookingButton = (isAvailable && deal.booking_link) 
        ? `<a href="${deal.booking_link}" target="_blank" style="display: block; margin-top: 1.5rem; background: linear-gradient(135deg, #1E5BA8, #4A9FDB); color: white; padding: 1rem 2rem; border-radius: 50px; text-decoration: none; font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.1rem; text-align: center; transition: transform 0.3s; box-shadow: 0 4px 15px rgba(30, 91, 168, 0.3);">
            ✈️ Book This Flight Now →
        </a>`
        : '';
    
    return `
        <div style="background: white; box-shadow: 0 10px 40px rgba(0,0,0,0.1); border: 3px solid ${isMistakeFare ? '#FF4444' : '#4A9FDB'}; border-radius: 24px; padding: 2.5rem; transition: transform 0.3s ease;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.5rem;">
                <div>
                    <h3 style="font-family: 'Poppins', sans-serif; font-size: 1.75rem; color: #1E5BA8; font-weight: 800; margin-bottom: 0.5rem;">
                        ${deal.origin || ''} → ${deal.destination || ''}
                    </h3>
                    <p style="font-family: 'Inter', sans-serif; color: #626784; font-size: 1rem; margin: 0; font-weight: 500;">
                        ${deal.route_description || ''}
                    </p>
                </div>
                ${statusBadge}
            </div>
            <div style="margin: 2rem 0;">
                <p style="font-family: 'Inter', sans-serif; color: #626784; font-size: 0.95rem; margin-bottom: 0.5rem; font-weight: 600;">Typical Price <span style="font-size: 0.85rem; color: #9CA3AF;">(based on recent searches)</span></p>
                <p style="font-family: 'Poppins', sans-serif; color: #9CA3AF; text-decoration: line-through; font-size: 1.4rem; margin-bottom: 1rem; font-weight: 600;">
                    ${formatCurrency(deal.normal_price, deal.currency)}
                </p>
                <p style="font-family: 'Inter', sans-serif; color: #626784; font-size: 0.95rem; margin-bottom: 0.5rem; font-weight: 600;">${isMistakeFare ? '⚡ Error Price' : 'Deal Price'} <span style="font-size: 0.85rem; color: #9CA3AF;">(verified available)</span></p>
                <p style="font-family: 'Poppins', sans-serif; color: ${isMistakeFare ? '#FF4444' : '#4A9FDB'}; font-size: 2.5rem; font-weight: 900; margin-bottom: 0.75rem;">
                    ${isAvailable ? formatCurrency(deal.mistake_price, deal.currency) : '🔒 Members Only'}
                </p>
                <p style="font-family: 'Inter', sans-serif; color: #7DB84D; font-weight: 700; font-size: 1.25rem; margin: 0;">
                    💰 You Save: ${formatCurrency(deal.savings_amount, deal.currency)} (${deal.savings_percentage.toFixed(0)}% off!)
                </p>
                ${isMistakeFare ? `
                    <div style="margin-top: 1rem; padding: 0.75rem; background: linear-gradient(135deg, #FFE5E5, #FFCCCC); border-radius: 12px; border-left: 4px solid #FF4444;">
                        <p style="font-family: 'Inter', sans-serif; color: #CC0000; font-size: 0.9rem; margin: 0; font-weight: 700;">
                            🔥 MISTAKE FARE ALERT: This pricing error won't last long! Book ASAP.
                        </p>
                    </div>
                ` : ''}
            </div>
            ${timeInfo}
            ${bookingButton}
            ${!isAvailable && !isPremium ? `
                <div style="margin-top: 1.5rem; padding: 1rem; background: #FFF3E0; border-radius: 12px;">
                    <p style="font-family: 'Inter', sans-serif; color: #E65100; font-size: 0.9rem; margin: 0; font-weight: 600;">
                        ⏰ Available to members immediately. Public access in ${getTimeUntilPublic(deal.published_at)}.
                    </p>
                </div>
            ` : ''}
        </div>
    `;
}

function getTimeUntilPublic(publishedAt) {
    if (!publishedAt) return 'soon';
    
    const published = new Date(publishedAt);
    const publicTime = new Date(published.getTime() + (60 * 60 * 1000)); // +1 hour
    const now = new Date();
    const minutesLeft = Math.round((publicTime - now) / (1000 * 60));
    
    if (minutesLeft <= 0) return 'now';
    if (minutesLeft < 60) return `${minutesLeft} minutes`;
    return `${Math.round(minutesLeft / 60)} hour`;
}
