/**
 * Avatar System JavaScript
 * AgentMath.app - Animal Avatars
 * 
 * This file contains all client-side avatar functionality:
 * - SVG avatar rendering
 * - Shop interactions
 * - Avatar customization
 * 
 * BACKOUT: Remove this file and script tags to disable avatar JS.
 */

// ==================== AVATAR SVG GENERATOR ====================

const AvatarRenderer = {
    
    // Color definitions for each animal (20 avatar-friendly animals)
    animalColors: {
        // Original 4
        panda: { face: '#ffffff', ears: '#1a1a1a', patches: '#1a1a1a', nose: '#1a1a1a' },
        fox: { face: '#ff6b35', ears: '#ff6b35', patches: '#ffffff', nose: '#1a1a1a' },
        cat: { face: '#ffa94d', ears: '#ffa94d', patches: '#ffffff', nose: '#ffb6c1' },
        owl: { face: '#8b4513', ears: '#654321', patches: '#f5deb3', nose: '#ffa500' },
        // New 16
        lion: { face: '#daa520', ears: '#b8860b', patches: '#f4a460', nose: '#1a1a1a' },
        bear: { face: '#8b4513', ears: '#654321', patches: '#a0522d', nose: '#1a1a1a' },
        wolf: { face: '#708090', ears: '#4a4a4a', patches: '#d3d3d3', nose: '#1a1a1a' },
        rabbit: { face: '#f5f5f5', ears: '#ffb6c1', patches: '#ffffff', nose: '#ffb6c1' },
        tiger: { face: '#ff8c00', ears: '#ff6600', patches: '#1a1a1a', nose: '#1a1a1a' },
        penguin: { face: '#1a1a1a', ears: '#1a1a1a', patches: '#ffffff', nose: '#ffa500' },
        koala: { face: '#808080', ears: '#696969', patches: '#d3d3d3', nose: '#1a1a1a' },
        elephant: { face: '#808080', ears: '#696969', patches: '#a9a9a9', nose: '#696969' },
        monkey: { face: '#deb887', ears: '#d2691e', patches: '#ffe4c4', nose: '#8b4513' },
        dog: { face: '#d2691e', ears: '#8b4513', patches: '#ffe4c4', nose: '#1a1a1a' },
        dolphin: { face: '#4682b4', ears: '#4169e1', patches: '#87ceeb', nose: '#4682b4' },
        horse: { face: '#8b4513', ears: '#654321', patches: '#d2691e', nose: '#1a1a1a' },
        deer: { face: '#d2691e', ears: '#8b4513', patches: '#f5deb3', nose: '#1a1a1a' },
        eagle: { face: '#8b4513', ears: '#654321', patches: '#ffffff', nose: '#ffa500' },
        parrot: { face: '#32cd32', ears: '#228b22', patches: '#ff4500', nose: '#ffa500' },
        turtle: { face: '#228b22', ears: '#006400', patches: '#90ee90', nose: '#2e8b57' }
    },
    
    // Background colors
    backgroundColors: {
        none: '#e8e8e8',
        forest: 'url(#bg-forest)',
        ocean: 'url(#bg-ocean)',
        sunset: 'url(#bg-sunset)',
        space: '#2C3E50',
        rainbow: 'url(#bg-rainbow)'
    },
    
    /**
     * Generate SVG for an avatar
     * @param {Object} config - Avatar configuration
     * @param {string} config.animal - Animal type (panda, fox, cat, owl)
     * @param {string} config.hat - Hat type
     * @param {string} config.glasses - Glasses type
     * @param {string} config.background - Background type
     * @param {string} config.accessory - Accessory type
     * @returns {string} SVG markup
     */
    generateSVG(config) {
        const { animal = 'panda', hat = 'none', glasses = 'none', background = 'none', accessory = 'none' } = config;
        const colors = this.animalColors[animal] || this.animalColors.panda;
        
        return `
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    ${this.getGradientDefs()}
                </defs>
                
                <!-- Background -->
                <rect width="100" height="100" fill="${this.getBackgroundFill(background)}"/>
                
                <!-- Ears -->
                ${this.renderEars(animal, colors)}
                
                <!-- Face -->
                ${this.renderFace(animal, colors)}
                
                <!-- Eyes -->
                ${this.renderEyes(animal)}
                
                <!-- Nose & Mouth -->
                ${this.renderNoseAndMouth(animal, colors)}
                
                <!-- Whiskers (cat/fox only) -->
                ${this.renderWhiskers(animal)}
                
                <!-- Glasses -->
                ${this.renderGlasses(glasses)}
                
                <!-- Hat -->
                ${this.renderHat(hat)}
                
                <!-- Accessory -->
                ${this.renderAccessory(accessory)}
            </svg>
        `;
    },
    
    getGradientDefs() {
        return `
            <linearGradient id="bg-forest" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#90EE90"/>
                <stop offset="100%" style="stop-color:#228B22"/>
            </linearGradient>
            <linearGradient id="bg-ocean" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#87CEEB"/>
                <stop offset="100%" style="stop-color:#4169E1"/>
            </linearGradient>
            <linearGradient id="bg-sunset" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#FFB347"/>
                <stop offset="100%" style="stop-color:#FF6B6B"/>
            </linearGradient>
            <linearGradient id="bg-rainbow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#ff6b6b"/>
                <stop offset="33%" style="stop-color:#feca57"/>
                <stop offset="66%" style="stop-color:#48dbfb"/>
                <stop offset="100%" style="stop-color:#ff9ff3"/>
            </linearGradient>
        `;
    },
    
    getBackgroundFill(background) {
        if (background === 'none') return '#e8e8e8';
        if (background === 'space') return '#2C3E50';
        return `url(#bg-${background})`;
    },
    
    renderEars(animal, colors) {
        let svg = `
            <circle cx="25" cy="25" r="15" fill="${colors.ears}"/>
            <circle cx="75" cy="25" r="15" fill="${colors.ears}"/>
        `;
        
        if (animal === 'panda') {
            svg += `
                <circle cx="25" cy="25" r="8" fill="#333"/>
                <circle cx="75" cy="25" r="8" fill="#333"/>
            `;
        } else if (animal === 'fox') {
            svg += `
                <circle cx="25" cy="25" r="8" fill="#1a1a1a"/>
                <circle cx="75" cy="25" r="8" fill="#1a1a1a"/>
            `;
        } else if (animal === 'cat') {
            svg += `
                <polygon points="20,15 25,30 30,15" fill="#ffb6c1"/>
                <polygon points="70,15 75,30 80,15" fill="#ffb6c1"/>
            `;
        } else if (animal === 'owl') {
            svg += `
                <polygon points="20,18 25,28 30,18" fill="${colors.ears}"/>
                <polygon points="70,18 75,28 80,18" fill="${colors.ears}"/>
            `;
        }
        
        return svg;
    },
    
    renderFace(animal, colors) {
        let svg = `<ellipse cx="50" cy="55" rx="35" ry="32" fill="${colors.face}"/>`;
        
        if (animal === 'panda') {
            svg += `
                <ellipse cx="35" cy="50" rx="12" ry="10" fill="${colors.patches}"/>
                <ellipse cx="65" cy="50" rx="12" ry="10" fill="${colors.patches}"/>
            `;
        } else if (animal === 'fox' || animal === 'cat') {
            svg += `<ellipse cx="50" cy="70" rx="20" ry="15" fill="${colors.patches}"/>`;
        } else if (animal === 'owl') {
            svg += `
                <circle cx="35" cy="50" r="14" fill="${colors.patches}"/>
                <circle cx="65" cy="50" r="14" fill="${colors.patches}"/>
            `;
        }
        
        return svg;
    },
    
    renderEyes(animal) {
        return `
            <circle cx="35" cy="50" r="8" fill="#fff"/>
            <circle cx="65" cy="50" r="8" fill="#fff"/>
            <circle cx="37" cy="50" r="5" fill="#333"/>
            <circle cx="67" cy="50" r="5" fill="#333"/>
            <circle cx="38" cy="48" r="2" fill="#fff"/>
            <circle cx="68" cy="48" r="2" fill="#fff"/>
        `;
    },
    
    renderNoseAndMouth(animal, colors) {
        if (animal === 'owl') {
            return `<polygon points="50,58 45,68 55,68" fill="${colors.nose}"/>`;
        }
        
        return `
            <ellipse cx="50" cy="62" rx="5" ry="4" fill="${colors.nose}"/>
            <path d="M 45 68 Q 50 73 55 68" stroke="#333" stroke-width="2" fill="none"/>
        `;
    },
    
    renderWhiskers(animal) {
        if (animal !== 'cat' && animal !== 'fox') return '';
        
        return `
            <line x1="20" y1="60" x2="35" y2="62" stroke="#333" stroke-width="1"/>
            <line x1="20" y1="65" x2="35" y2="65" stroke="#333" stroke-width="1"/>
            <line x1="65" y1="62" x2="80" y2="60" stroke="#333" stroke-width="1"/>
            <line x1="65" y1="65" x2="80" y2="65" stroke="#333" stroke-width="1"/>
        `;
    },
    
    renderGlasses(glasses) {
        if (glasses === 'none') return '';
        
        if (glasses === 'round') {
            return `
                <circle cx="35" cy="50" r="12" fill="none" stroke="#333" stroke-width="2"/>
                <circle cx="65" cy="50" r="12" fill="none" stroke="#333" stroke-width="2"/>
                <line x1="47" y1="50" x2="53" y2="50" stroke="#333" stroke-width="2"/>
            `;
        }
        
        if (glasses === 'cool') {
            return `
                <rect x="22" y="44" width="26" height="14" rx="2" fill="#1a1a2e"/>
                <rect x="52" y="44" width="26" height="14" rx="2" fill="#1a1a2e"/>
                <line x1="48" y1="50" x2="52" y2="50" stroke="#333" stroke-width="2"/>
            `;
        }
        
        if (glasses === 'heart') {
            return `
                <path d="M 25 50 C 25 42 35 42 35 50 C 35 42 45 42 45 50 C 45 60 35 65 35 65 C 35 65 25 60 25 50" fill="#ff6b6b"/>
                <path d="M 55 50 C 55 42 65 42 65 50 C 65 42 75 42 75 50 C 75 60 65 65 65 65 C 65 65 55 60 55 50" fill="#ff6b6b"/>
            `;
        }
        
        if (glasses === 'star') {
            return `
                <polygon points="35,42 37,48 43,48 38,52 40,58 35,54 30,58 32,52 27,48 33,48" fill="#f1c40f"/>
                <polygon points="65,42 67,48 73,48 68,52 70,58 65,54 60,58 62,52 57,48 63,48" fill="#f1c40f"/>
            `;
        }
        
        return '';
    },
    
    renderHat(hat) {
        if (hat === 'none') return '';
        
        if (hat === 'party') {
            return `
                <polygon points="50,5 35,35 65,35" fill="#9b59b6"/>
                <circle cx="50" cy="5" r="4" fill="#f1c40f"/>
                <rect x="38" y="20" width="4" height="4" fill="#3498db"/>
                <rect x="48" y="15" width="4" height="4" fill="#e74c3c"/>
                <rect x="55" y="22" width="4" height="4" fill="#2ecc71"/>
            `;
        }
        
        if (hat === 'cap') {
            return `
                <ellipse cx="50" cy="22" rx="25" ry="12" fill="#e74c3c"/>
                <rect x="20" y="22" width="30" height="8" fill="#c0392b"/>
            `;
        }
        
        if (hat === 'beanie') {
            return `
                <ellipse cx="50" cy="25" rx="28" ry="18" fill="#e74c3c"/>
                <circle cx="50" cy="8" r="5" fill="#e74c3c"/>
                <rect x="25" y="30" width="50" height="6" fill="#c0392b"/>
            `;
        }
        
        if (hat === 'tophat') {
            return `
                <rect x="32" y="5" width="36" height="25" fill="#2c3e50"/>
                <rect x="25" y="28" width="50" height="6" fill="#34495e"/>
                <rect x="35" y="20" width="30" height="4" fill="#9b59b6"/>
            `;
        }
        
        if (hat === 'wizard') {
            return `
                <polygon points="50,0 30,35 70,35" fill="#9b59b6"/>
                <rect x="28" y="32" width="44" height="5" fill="#8e44ad"/>
                <circle cx="50" cy="15" r="4" fill="#f1c40f"/>
                <circle cx="40" cy="25" r="2" fill="#f1c40f"/>
                <circle cx="58" cy="22" r="2" fill="#f1c40f"/>
            `;
        }
        
        if (hat === 'crown') {
            return `
                <rect x="30" y="18" width="40" height="12" fill="#f1c40f"/>
                <polygon points="30,18 38,5 46,18" fill="#f1c40f"/>
                <polygon points="42,18 50,2 58,18" fill="#f1c40f"/>
                <polygon points="54,18 62,5 70,18" fill="#f1c40f"/>
                <circle cx="38" cy="22" r="3" fill="#e74c3c"/>
                <circle cx="50" cy="22" r="3" fill="#3498db"/>
                <circle cx="62" cy="22" r="3" fill="#2ecc71"/>
            `;
        }
        
        if (hat === 'graduation') {
            return `
                <rect x="30" y="18" width="40" height="10" fill="#2c3e50"/>
                <rect x="20" y="15" width="60" height="5" fill="#34495e"/>
                <rect x="48" y="8" width="4" height="8" fill="#f1c40f"/>
                <circle cx="60" cy="8" r="3" fill="#f1c40f"/>
                <line x1="50" y1="8" x2="65" y2="12" stroke="#f1c40f" stroke-width="2"/>
            `;
        }
        
        return '';
    },
    
    renderAccessory(accessory) {
        if (accessory === 'none') return '';
        
        if (accessory === 'pencil') {
            return `
                <g transform="translate(72, 55) rotate(30)">
                    <rect x="0" y="0" width="6" height="25" fill="#f1c40f"/>
                    <polygon points="0,25 3,32 6,25" fill="#ffd5b5"/>
                    <rect x="0" y="0" width="6" height="4" fill="#e74c3c"/>
                </g>
            `;
        }
        
        if (accessory === 'calculator') {
            return `
                <g transform="translate(70, 65)">
                    <rect x="0" y="0" width="18" height="25" rx="2" fill="#34495e"/>
                    <rect x="2" y="2" width="14" height="6" fill="#2ecc71"/>
                    <rect x="2" y="10" width="4" height="4" fill="#ecf0f1"/>
                    <rect x="7" y="10" width="4" height="4" fill="#ecf0f1"/>
                    <rect x="12" y="10" width="4" height="4" fill="#e74c3c"/>
                    <rect x="2" y="15" width="4" height="4" fill="#ecf0f1"/>
                    <rect x="7" y="15" width="4" height="4" fill="#ecf0f1"/>
                    <rect x="12" y="15" width="4" height="4" fill="#3498db"/>
                </g>
            `;
        }
        
        if (accessory === 'protractor') {
            return `
                <g transform="translate(68, 70)">
                    <path d="M 0,20 A 20,20 0 0,1 40,20 L 20,20 Z" fill="#3498db" opacity="0.8"/>
                    <circle cx="20" cy="20" r="3" fill="#2c3e50"/>
                </g>
            `;
        }
        
        if (accessory === 'medal') {
            return `
                <g transform="translate(42, 78)">
                    <rect x="6" y="-8" width="4" height="10" fill="#3498db"/>
                    <circle cx="8" cy="8" r="10" fill="#f1c40f"/>
                    <circle cx="8" cy="8" r="7" fill="#f39c12"/>
                    <text x="8" y="12" text-anchor="middle" font-size="10" fill="#fff" font-weight="bold">1</text>
                </g>
            `;
        }
        
        if (accessory === 'trophy') {
            return `
                <g transform="translate(70, 60)">
                    <rect x="8" y="25" width="10" height="5" fill="#f39c12"/>
                    <rect x="5" y="28" width="16" height="4" fill="#d68910"/>
                    <path d="M 3,5 L 3,15 Q 3,25 13,25 Q 23,25 23,15 L 23,5 Z" fill="#f1c40f"/>
                    <path d="M 0,5 Q 0,15 3,15 L 3,5 Z" fill="#f39c12"/>
                    <path d="M 23,5 L 23,15 Q 26,15 26,5 Z" fill="#f39c12"/>
                </g>
            `;
        }
        
        return '';
    },
    
    /**
     * Render avatar into a container element
     * @param {HTMLElement|string} container - Element or selector
     * @param {Object} config - Avatar configuration
     * @param {string} size - Size class (tiny, small, medium, large, xlarge)
     */
    render(container, config, size = 'medium') {
        const element = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        if (!element) {
            console.error('Avatar container not found');
            return;
        }
        
        const bgClass = `avatar-bg-${config.background || 'none'}`;
        
        element.className = `avatar-container avatar-${size} ${bgClass}`;
        element.innerHTML = this.generateSVG(config);
    }
};


// ==================== AVATAR SHOP ====================

const AvatarShop = {
    
    currentAvatar: {
        animal: 'panda',
        hat: 'none',
        glasses: 'none',
        background: 'none',
        accessory: 'none'
    },
    
    inventory: [],
    allItems: [],
    userPoints: 0,
    
    /**
     * Initialize the shop
     */
    async init() {
        await this.loadData();
        this.renderPreview();
        this.renderShop();
        this.setupEventListeners();
    },
    
    /**
     * Load shop data from API
     */
    async loadData() {
        try {
            // Load all items
            const itemsResponse = await fetch('/api/avatar/items');
            const itemsData = await itemsResponse.json();
            this.allItems = itemsData.items || [];
            
            // Load user inventory
            const inventoryResponse = await fetch('/api/avatar/inventory');
            const inventoryData = await inventoryResponse.json();
            this.inventory = inventoryData.inventory || [];
            this.userPoints = inventoryData.points || 0;
            console.log('🎒 Loaded inventory:', this.inventory.length, 'items, Points:', this.userPoints);
            
            // Load equipped items
            const equippedResponse = await fetch('/api/avatar/equipped');
            const equippedData = await equippedResponse.json();
            console.log('🎭 Equipped data from API:', equippedData);
            if (equippedData.equipped) {
                this.currentAvatar = equippedData.equipped;
                console.log('🎭 Current avatar set to:', this.currentAvatar);
            }
            
        } catch (error) {
            console.error('Error loading avatar data:', error);
        }
    },
    
    /**
     * Check if user owns an item
     */
    ownsItem(itemId) {
        return this.inventory.some(inv => inv.item && inv.item.id === itemId);
    },
    
    /**
     * Check if item is currently equipped
     */
    isEquipped(itemType, itemKey) {
        return this.currentAvatar[itemType] === itemKey;
    },
    
    /**
     * Render the preview avatar
     */
    renderPreview() {
        console.log('🖼️ renderPreview called with:', this.currentAvatar);
        const previewContainer = document.getElementById('avatar-preview');
        if (previewContainer) {
            AvatarRenderer.render(previewContainer, this.currentAvatar, 'xlarge');
        } else {
            console.warn('⚠️ avatar-preview container not found');
        }
        
        const pointsDisplay = document.getElementById('avatar-points');
        if (pointsDisplay) {
            pointsDisplay.textContent = this.userPoints;
        }
    },
    
    /**
     * Render the shop items
     */
    renderShop() {
        const categories = ['animal', 'hat', 'glasses', 'background', 'accessory'];
        
        categories.forEach(category => {
            const container = document.getElementById(`shop-${category}`);
            if (!container) return;
            
            const items = this.allItems.filter(item => item.item_type === category);
            
            container.innerHTML = items.map(item => this.renderShopItem(item)).join('');
        });
    },
    
    /**
     * Render a single shop item
     */
    renderShopItem(item) {
        const owned = this.ownsItem(item.id) || item.is_default;
        const equipped = this.isEquipped(item.item_type, item.item_key);
        const canAfford = this.userPoints >= item.point_cost;
        
        let statusClass = '';
        let badge = '';
        let button = '';
        
        if (equipped) {
            statusClass = 'equipped';
            badge = '<span class="shop-item-badge equipped">EQUIPPED</span>';
            button = '<button class="shop-item-buy owned" disabled>Equipped</button>';
        } else if (owned) {
            statusClass = 'owned';
            badge = '<span class="shop-item-badge">OWNED</span>';
            button = `<button class="shop-item-buy owned" onclick="AvatarShop.equipItem('${item.item_type}', '${item.item_key}')">Equip</button>`;
        } else if (item.point_cost === 0) {
            button = `<button class="shop-item-buy can-afford" onclick="AvatarShop.purchaseItem(${item.id})">Get Free</button>`;
        } else if (canAfford) {
            button = `<button class="shop-item-buy can-afford" onclick="AvatarShop.purchaseItem(${item.id})">Buy</button>`;
        } else {
            statusClass = 'locked';
            button = `<button class="shop-item-buy cannot-afford" disabled>Need ${item.point_cost - this.userPoints} more</button>`;
        }
        
        const costDisplay = item.point_cost === 0 
            ? '<span class="free">FREE</span>' 
            : `⭐ ${item.point_cost}`;
        
        return `
            <div class="shop-item ${statusClass}" data-item-id="${item.id}">
                ${badge}
                <span class="shop-item-rarity rarity-${item.rarity}">${item.rarity}</span>
                <div class="shop-item-icon">${this.getItemEmoji(item.item_type, item.item_key)}</div>
                <div class="shop-item-name">${item.display_name}</div>
                <div class="shop-item-cost">${costDisplay}</div>
                ${button}
            </div>
        `;
    },
    
    /**
     * Get emoji for item display
     */
    getItemEmoji(type, key) {
        const emojis = {
            animal: { 
                panda: '🐼', fox: '🦊', cat: '🐱', owl: '🦉',
                lion: '🦁', bear: '🐻', wolf: '🐺', rabbit: '🐰',
                tiger: '🐯', penguin: '🐧', koala: '🐨', elephant: '🐘',
                monkey: '🐵', dog: '🐕', dolphin: '🐬', horse: '🐴',
                deer: '🦌', eagle: '🦅', parrot: '🦜', turtle: '🐢'
            },
            hat: { none: '❌', party: '🎉', cap: '🧢', beanie: '🧶', tophat: '🎩', wizard: '🧙', crown: '👑', graduation: '🎓' },
            glasses: { none: '❌', round: '👓', cool: '😎', heart: '💕', star: '⭐' },
            background: { none: '⬜', forest: '🌲', ocean: '🌊', sunset: '🌅', space: '🌌', rainbow: '🌈' },
            accessory: { none: '❌', pencil: '✏️', calculator: '🔢', protractor: '📐', medal: '🥇', trophy: '🏆' }
        };
        
        return emojis[type]?.[key] || '❓';
    },
    
    /**
     * Purchase an item
     */
    async purchaseItem(itemId) {
        try {
            const response = await fetch('/api/avatar/purchase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: itemId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update points immediately
                if (data.new_points !== undefined) {
                    this.userPoints = data.new_points;
                }
                
                // Reload ALL data from server (inventory AND equipped)
                await this.loadData();
                
                // Force re-render after data loads
                this.renderPreview();
                this.renderShop();
                
                // Animate the preview to show change
                const preview = document.getElementById('avatar-preview');
                if (preview) {
                    preview.classList.add('avatar-bounce');
                    setTimeout(() => preview.classList.remove('avatar-bounce'), 500);
                }
                
                // Show success message
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message || 'Purchase failed', 'error');
            }
            
        } catch (error) {
            console.error('Purchase error:', error);
            this.showMessage('An error occurred', 'error');
        }
    },
    
    /**
     * Equip an item
     */
    async equipItem(itemType, itemKey) {
        try {
            const response = await fetch('/api/avatar/equip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_type: itemType, item_key: itemKey })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update local state
                this.currentAvatar[itemType] = itemKey;
                
                // Update UI
                this.renderPreview();
                this.renderShop();
                
                // Animate the preview
                const preview = document.getElementById('avatar-preview');
                if (preview) {
                    preview.classList.add('avatar-bounce');
                    setTimeout(() => preview.classList.remove('avatar-bounce'), 500);
                }
                
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message || 'Failed to equip', 'error');
            }
            
        } catch (error) {
            console.error('Equip error:', error);
            this.showMessage('An error occurred', 'error');
        }
    },
    
    /**
     * Show a message to the user
     */
    showMessage(message, type = 'info') {
        // You can integrate this with your existing notification system
        console.log(`[${type}] ${message}`);
        
        // Simple alert for now - replace with better UI
        if (type === 'error') {
            alert('❌ ' + message);
        }
    },
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Add any additional event listeners here
    }
};


// ==================== UTILITY FUNCTIONS ====================

/**
 * Quick function to render an avatar anywhere on the page
 * @param {string} selector - CSS selector for container
 * @param {Object} config - Avatar config (or will load from API)
 * @param {string} size - Size class
 */
async function renderAvatar(selector, config = null, size = 'medium') {
    if (!config) {
        try {
            const response = await fetch('/api/avatar/equipped');
            const data = await response.json();
            config = data.equipped || { animal: 'panda' };
        } catch (e) {
            config = { animal: 'panda' };
        }
    }
    
    AvatarRenderer.render(selector, config, size);
}


// ==================== AUTO-INIT ====================

// Initialize shop if on shop page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('avatar-shop')) {
        AvatarShop.init();
    }
});
