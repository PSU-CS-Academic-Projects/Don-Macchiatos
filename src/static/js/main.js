/* ═══════════════════════════════════════════════
   DON MACCHIATOS — MAIN JAVASCRIPT
   Premium redesign: Cart AJAX, Navbar scroll effect,
   Intersection Observer animations
   ═══════════════════════════════════════════════ */

'use strict';

// ─────────────────────────────────────────────
// CSRF TOKEN UTILITY
// ─────────────────────────────────────────────
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const CSRF_TOKEN = getCookie('csrftoken');

// ─────────────────────────────────────────────
// CART BADGE UPDATE
// ─────────────────────────────────────────────
function updateCartBadge(count) {
    const badge = document.getElementById('cart-badge');
    if (badge) {
        badge.textContent = count > 0 ? count : '';
    }
}

// ─────────────────────────────────────────────
// SHOW TOAST NOTIFICATION
// ─────────────────────────────────────────────
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `message message--${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="message__close" onclick="this.parentElement.remove()" aria-label="Close notification">×</button>
    `;

    let container = document.querySelector('.messages-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'messages-container';
        document.body.appendChild(container);
    }

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ─────────────────────────────────────────────
// ADD TO CART
// ─────────────────────────────────────────────
async function addToCart(itemId, itemName) {
    try {
        const response = await fetch(`/cart/add/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            updateCartBadge(data.cart_count);
            showToast(`${itemName} added to cart! ☕`);
        } else {
            showToast('Could not add item. Try again.', 'error');
        }
    } catch (error) {
        console.error('Add to cart error:', error);
        showToast('Something went wrong. Please try again.', 'error');
    }
}

// ─────────────────────────────────────────────
// REMOVE FROM CART
// ─────────────────────────────────────────────
async function removeFromCart(itemId) {
    try {
        const response = await fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': CSRF_TOKEN },
        });

        const data = await response.json();

        if (data.success) {
            const row = document.getElementById(`cart-item-${itemId}`);
            if (row) {
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                row.style.transition = 'all 0.3s ease';
                setTimeout(() => {
                    row.remove();
                    if (document.querySelectorAll('.cart-item').length === 0) {
                        location.reload();
                    }
                }, 300);
            }
            updateCartBadge(data.cart_count);
        }
    } catch (error) {
        console.error('Remove from cart error:', error);
    }
}

// ─────────────────────────────────────────────
// UPDATE CART QUANTITY
// ─────────────────────────────────────────────
async function updateCartQuantity(itemId, newQuantity) {
    if (newQuantity <= 0) {
        removeFromCart(itemId);
        return;
    }

    try {
        const response = await fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity: newQuantity }),
        });

        const data = await response.json();

        if (data.success) {
            updateCartBadge(data.cart_count);
            const qtyDisplay = document.getElementById(`qty-${itemId}`);
            if (qtyDisplay) qtyDisplay.textContent = newQuantity;
            refreshCartTotals();
        }
    } catch (error) {
        console.error('Update cart error:', error);
    }
}

// ─────────────────────────────────────────────
// REFRESH CART TOTALS
// ─────────────────────────────────────────────
async function refreshCartTotals() {
    setTimeout(() => location.reload(), 200);
}

// ─────────────────────────────────────────────
// NAVBAR SCROLL EFFECT
// Add .scrolled class after 80px scroll
// ─────────────────────────────────────────────
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 80) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ─────────────────────────────────────────────
// INTERSECTION OBSERVER — Scroll Animations
// ─────────────────────────────────────────────
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'none';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all animated elements
    document.querySelectorAll('.fade-in, .slide-left, .slide-right, .slide-up, .scale-in').forEach(el => {
        observer.observe(el);
    });

    // Stagger children animations
    const staggerChildren = document.querySelectorAll('.stagger-child');
    if (staggerChildren.length > 0) {
        staggerChildren.forEach((el, index) => {
            el.style.animationDelay = `${index * 0.12}s`;
            observer.observe(el);
        });
    }
}

// ─────────────────────────────────────────────
// INITIALIZATION
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // Initialize navbar scroll
    initNavbarScroll();

    // Initialize scroll animations
    initScrollAnimations();

    // ── Add to Cart buttons ──
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            const itemName = this.dataset.itemName;

            const originalText = this.textContent;
            this.textContent = '✓ Added';
            this.disabled = true;
            setTimeout(() => {
                this.textContent = originalText;
                this.disabled = false;
            }, 1500);

            addToCart(itemId, itemName);
        });
    });

    // ── Cart page: quantity buttons ──
    document.querySelectorAll('.qty-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            const action = this.dataset.action;
            const qtyDisplay = document.getElementById(`qty-${itemId}`);

            if (!qtyDisplay) return;

            let currentQty = parseInt(qtyDisplay.textContent, 10);
            const newQty = action === 'increase' ? currentQty + 1 : currentQty - 1;

            qtyDisplay.textContent = newQty > 0 ? newQty : 0;
            updateCartQuantity(itemId, newQty);
        });
    });

    // ── Cart page: remove buttons ──
    document.querySelectorAll('.cart-item__remove').forEach(btn => {
        btn.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            removeFromCart(itemId);
        });
    });

    // ── Navbar mobile toggle ──
    const toggle = document.getElementById('navToggle');
    const navLinks = document.querySelector('.navbar__links');

    if (toggle && navLinks) {
        toggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
        });

        // Close menu when a link is clicked
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
            });
        });
    }

    // ── Menu filter buttons ──
    const filterBtns = document.querySelectorAll('.filter-btn');
    const menuCards = document.querySelectorAll('.card--menu');

    if (filterBtns.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                filterBtns.forEach(b => b.classList.remove('filter-btn--active'));
                this.classList.add('filter-btn--active');

                const filter = this.dataset.filter;

                menuCards.forEach(card => {
                    if (filter === 'all' || card.dataset.category === filter) {
                        card.style.display = '';
                        card.style.animation = 'fadeIn 0.3s ease';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }
});