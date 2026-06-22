// State management
let products = [];
let filteredProducts = [];
let currentCategory = 'all';
let searchQuery = '';
let currentSort = 'default';

// DOM elements
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const categoriesTabs = document.getElementById('categoriesTabs');
const sortSelect = document.getElementById('sortSelect');
const resultsCount = document.getElementById('resultsCount');
const productsGrid = document.getElementById('productsGrid');
const printBtn = document.getElementById('printBtn');

// Lightbox elements
const lightboxModal = document.getElementById('lightboxModal');
const lightboxImg = document.getElementById('lightboxImg');
const lightboxCaption = document.getElementById('lightboxCaption');
const closeLightbox = document.getElementById('closeLightbox');

// Map of category names to Russian labels (for tags on cards)
const categoryLabels = {
    thermal: 'Тепловое',
    refrigeration: 'Холодильное',
    electromechanical: 'Электромеханика',
    bar: 'Бар & Кофе',
    neutral: 'Нейтральное',
    tableware: 'Посуда',
    furniture: 'Мебель',
    other: 'Прочее'
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    fetchProducts();
    setupEventListeners();
});

// Fetch products from products.json
async function fetchProducts() {
    try {
        const response = await fetch('./products.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        products = await response.ok ? await response.json() : [];
        filteredProducts = [...products];
        
        // Update category count badges
        updateCategoryBadges();
        
        // Render initially
        applyFiltersAndSort();
    } catch (error) {
        console.error('Error fetching catalog data:', error);
        productsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-triangle-exclamation empty-icon" style="color: #ef4444;"></i>
                <p>Не удалось загрузить каталог товаров. Пожалуйста, попробуйте перезагрузить страницу.</p>
                <button onclick="location.reload()" class="print-btn" style="margin-top: 10px;">Обновить</button>
            </div>
        `;
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Search input handler
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase().trim();
        clearSearchBtn.style.display = searchQuery ? 'block' : 'none';
        applyFiltersAndSort();
    });

    // Clear search handler
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        clearSearchBtn.style.display = 'none';
        searchInput.focus();
        applyFiltersAndSort();
    });

    // Category tabs handler
    categoriesTabs.addEventListener('click', (e) => {
        const btn = e.target.closest('.tab-btn');
        if (!btn) return;
        
        // Update active tab styling
        categoriesTabs.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        
        currentCategory = btn.getAttribute('data-category');
        applyFiltersAndSort();
    });

    // Sort select handler
    sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        applyFiltersAndSort();
    });

    // Print button handler
    printBtn.addEventListener('click', () => {
        window.print();
    });

    // Close Lightbox modal click
    closeLightbox.addEventListener('click', closeLightboxModal);
    lightboxModal.addEventListener('click', (e) => {
        if (e.target === lightboxModal) {
            closeLightboxModal();
        }
    });

    // Escape key press to close lightbox
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && lightboxModal.style.display === 'flex') {
            closeLightboxModal();
        }
    });
}

// Update badges for each category button with total items
function updateCategoryBadges() {
    const counts = {
        all: products.length,
        thermal: 0,
        refrigeration: 0,
        electromechanical: 0,
        bar: 0,
        neutral: 0,
        tableware: 0,
        furniture: 0,
        other: 0
    };
    
    products.forEach(p => {
        const cat = p.category;
        if (counts.hasOwnProperty(cat)) {
            counts[cat]++;
        } else {
            counts.other++;
        }
    });
    
    // Update DOM
    Object.keys(counts).forEach(cat => {
        const badge = document.getElementById(`count-${cat}`);
        if (badge) {
            badge.textContent = counts[cat];
        }
    });
}

// Apply Filters (search + category) and Sorting
function applyFiltersAndSort() {
    // 1. Apply Category Filter
    filteredProducts = products.filter(p => {
        if (currentCategory === 'all') return true;
        return p.category === currentCategory;
    });

    // 2. Apply Search Filter
    if (searchQuery) {
        filteredProducts = filteredProducts.filter(p => {
            const nameZh = (p.name_zh || '').toLowerCase();
            const nameRu = (p.name_ru || '').toLowerCase();
            const specs = (p.specs || '').toLowerCase();
            const size = (p.size || '').toLowerCase();
            const idStr = String(p.id);
            
            return nameZh.includes(searchQuery) || 
                   nameRu.includes(searchQuery) || 
                   specs.includes(searchQuery) || 
                   size.includes(searchQuery) ||
                   idStr === searchQuery;
        });
    }

    // 3. Apply Sorting
    if (currentSort === 'price-asc') {
        filteredProducts.sort((a, b) => {
            // handle gifts (0 price) to be sorted accordingly
            return a.price_cny - b.price_cny;
        });
    } else if (currentSort === 'price-desc') {
        filteredProducts.sort((a, b) => b.price_cny - a.price_cny);
    } else if (currentSort === 'name-asc') {
        filteredProducts.sort((a, b) => {
            const nameA = (a.name_ru || a.name_zh || '').toLowerCase();
            const nameB = (b.name_ru || b.name_zh || '').toLowerCase();
            return nameA.localeCompare(nameB, 'ru');
        });
    } else {
        // default sorting by id
        filteredProducts.sort((a, b) => a.id - b.id);
    }

    // Render cards
    renderProducts();
}

// Render product cards into the DOM grid
function renderProducts() {
    // Update stats bar counter
    resultsCount.textContent = `Найдено: ${filteredProducts.length} ${getNounDeclension(filteredProducts.length, 'товар', 'товара', 'товаров')}`;

    if (filteredProducts.length === 0) {
        productsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-cubes empty-icon"></i>
                <p>По вашему запросу ничего не найдено. Попробуйте изменить параметры поиска или фильтра.</p>
            </div>
        `;
        return;
    }

    // Generate HTML string for rendering
    let html = '';
    filteredProducts.forEach(p => {
        const hasImg = p.image && p.image !== './images/placeholder.jpg';
        const displayImg = hasImg ? p.image : 'https://placehold.co/400x340/1a1a1f/fad02c?text=Gastro+Ultima';
        
        const priceKztFormatted = p.is_gift ? 'Подарок' : p.price_kzt.toLocaleString('ru-RU') + ' ₸';
        const priceCnyFormatted = p.is_gift ? 'FREE' : p.price_cny.toLocaleString('ru-RU') + ' ¥';
        
        const catLabel = categoryLabels[p.category] || 'Товар';
        
        html += `
            <div class="product-card" data-id="${p.id}">
                <div class="product-img-wrapper" onclick="openLightboxModal('${p.image || displayImg}', '${p.name_ru || p.name_zh}')">
                    <img src="${displayImg}" alt="${p.name_ru || p.name_zh}" class="product-img" loading="lazy">
                    <span class="product-tag">${catLabel}</span>
                    ${p.is_gift ? '<span class="gift-tag">Подарок</span>' : ''}
                </div>
                <div class="product-info">
                    <h3 class="product-title">${p.name_ru || 'Без названия'}</h3>
                    <div class="product-title-zh">${p.name_zh || ''}</div>
                    
                    <div class="product-details">
                        ${p.size ? `
                        <div class="detail-item">
                            <i class="fa-solid fa-ruler-combined"></i>
                            <span class="detail-val">Размеры: <strong>${p.size}</strong></span>
                        </div>` : ''}
                        
                        ${p.specs ? `
                        <div class="detail-item">
                            <i class="fa-solid fa-sliders"></i>
                            <span class="detail-val">${p.specs}</span>
                        </div>` : ''}
                        
                        <div class="detail-item">
                            <i class="fa-solid fa-box"></i>
                            <span class="detail-val">Ед. изм: ${p.unit || 'PCS'}</span>
                        </div>
                    </div>
                    
                    <div class="product-price-section">
                        <div class="price-row">
                            <span class="price-kzt">${priceKztFormatted}</span>
                            ${!p.is_gift ? `<span class="price-cny">${priceCnyFormatted}</span>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    productsGrid.innerHTML = html;
}

// Lightbox Open Modal handler
function openLightboxModal(src, title) {
    // If it's a placeholder generator, just zoom it
    lightboxImg.src = src;
    lightboxCaption.textContent = title;
    lightboxModal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Disable page scrolling
}

// Lightbox Close Modal handler
function closeLightboxModal() {
    lightboxModal.style.display = 'none';
    document.body.style.overflow = ''; // Enable page scrolling
}

// Russian Grammar Helper: Noun Declension
function getNounDeclension(number, one, two, many) {
    let n = Math.abs(number);
    n %= 100;
    if (n >= 5 && n <= 20) {
        return many;
    }
    n %= 10;
    if (n === 1) {
        return one;
    }
    if (n >= 2 && n <= 4) {
        return two;
    }
    return many;
}

