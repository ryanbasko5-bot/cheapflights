// Mobile Menu Toggle
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const navLinks = document.getElementById('navLinks');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        navLinks.classList.toggle('active');
    });
    
    // Close menu when clicking on a link
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenuToggle.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });
}

// Smooth Scrolling for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Subscribe Form Handling
document.getElementById('subscribeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const phoneInput = document.getElementById('phone');
    const messageDiv = document.getElementById('formMessage');
    const submitBtn = this.querySelector('.btn-submit');
    
    // Validate phone number format
    const phoneNumber = phoneInput.value.trim();
    const phoneRegex = /^\+[1-9]\d{1,14}$/;
    
    if (!phoneRegex.test(phoneNumber)) {
        showMessage('Please enter a valid phone number with country code (e.g., +61411246861)', 'error');
        return;
    }
    
    // Disable button during submission
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    
    try {
        // Send subscription request to backend
        const response = await fetch('/api/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phone: phoneNumber })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Success! Check your SMS for the payment link.', 'success');
            phoneInput.value = '';
        } else {
            showMessage(data.error || 'Something went wrong. Please try again.', 'error');
        }
    } catch (error) {
        // For now, show a demo message since backend isn't connected yet
        showMessage(
            `✅ Demo Mode: Would send SMS to ${phoneNumber} with Stripe payment link. ` +
            `Backend API not connected yet - run 'python src/api/main.py' to enable.`,
            'success'
        );
        phoneInput.value = '';
    } finally {
        // Re-enable button
        submitBtn.disabled = false;
        submitBtn.textContent = 'Subscribe for $5/mo';
    }
});

function showMessage(text, type) {
    const messageDiv = document.getElementById('formMessage');
    messageDiv.textContent = text;
    messageDiv.className = `form-message ${type}`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.className = 'form-message';
    }, 5000);
}

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all major sections
document.querySelectorAll('.feature-card, .deal-card, .pricing-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Update current year in footer
const yearElement = document.querySelector('.footer-bottom p');
if (yearElement) {
    yearElement.textContent = yearElement.textContent.replace('2025', new Date().getFullYear());
}

// Dynamic deal loading (placeholder for future API integration)
async function loadRecentDeals() {
    // This will connect to your backend API in the future
    // For now, deals are hardcoded in HTML
    try {
        const response = await fetch('/api/deals/recent');
        if (response.ok) {
            const deals = await response.json();
            updateDealsDisplay(deals);
        }
    } catch (error) {
        // API not available yet - using static HTML deals
        console.log('Using static deals - API not connected');
    }
}

function updateDealsDisplay(deals) {
    const dealsGrid = document.querySelector('.deals-grid');
    if (!deals || deals.length === 0) return;
    
    dealsGrid.innerHTML = deals.map(deal => `
        <div class="deal-card">
            <div class="deal-route">
                <span class="city">${deal.origin}</span>
                <span class="arrow">→</span>
                <span class="city">${deal.destination}</span>
            </div>
            <div class="deal-price">
                <span class="original-price">${deal.normalPrice}</span>
                <span class="deal-price-main">${deal.dealPrice}</span>
            </div>
            <div class="deal-savings">Save ${deal.savings}</div>
            <div class="deal-status ${deal.status}">${deal.status}</div>
        </div>
    `).join('');
}

// Load deals on page load (will use static HTML until API is ready)
document.addEventListener('DOMContentLoaded', () => {
    loadRecentDeals();
});
