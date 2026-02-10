// Theme Management & Global Map Utilities

document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    // 1. Initialize Theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);

    if(toggleBtn) {
        const icon = toggleBtn.querySelector('i');
        
        toggleBtn.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyTheme(newTheme);
        });
    }

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update Icon
        const icon = document.querySelector('#theme-toggle i');
        if (icon) {
            if (theme === 'light') {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
                icon.style.color = 'orange';
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
                icon.style.color = '';
            }
        }

        // Update Map Tiles if map exists
        if (typeof map !== 'undefined' && map.hasLayer) {
            updateMapTile(theme);
        }
    }
});

function updateMapTile(theme) {
    // Tile URLs
    const darkTile = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
    const lightTile = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
    const newUrl = theme === 'light' ? lightTile : darkTile;

    // Find and update tile layer
    if (typeof map !== 'undefined') {
        map.eachLayer((layer) => {
            if (layer instanceof L.TileLayer) {
                layer.setUrl(newUrl);
            }
        });
    }
}