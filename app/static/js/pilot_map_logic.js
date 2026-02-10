document.addEventListener('DOMContentLoaded', () => {
    // Initialize Map
    window.map = L.map('map').setView([31.95, 35.91], 12);
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const tileUrl = isDark ? 
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' : 
        'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
    
    L.tileLayer(tileUrl, { maxZoom: 20 }).addTo(map);

    // Fetch and Draw Zones
    fetch('/pilot/get_operational_zones')
    .then(res => res.json())
    .then(data => {
        data.forEach(zone => {
            const color = zone.type === 'red' ? '#ff2a6d' : (zone.type === 'yellow' ? '#ffc107' : '#00f0b5');
            let coords = zone.coords;

            if (typeof coords === 'string') {
                try { coords = JSON.parse(coords); } catch(e) {}
            }

            try {
                if (coords.type === 'circle' || (coords.lat && coords.radius)) {
                    L.circle([coords.lat, coords.lng], {
                        radius: coords.radius,
                        color: color,
                        fillOpacity: 0.2,
                        weight: 1
                    }).addTo(map);
                } else {
                    L.polygon(coords, {
                        color: color, 
                        fillOpacity: 0.2,
                        weight: 1
                    }).addTo(map);
                }
            } catch(e) { console.error(e); }
        });
    });

    // --- Drawing Logic (Only if on request page) ---
    if (typeof L.Control.Draw !== 'undefined' && document.getElementById('pathCoordsInput')) {
        const drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);

        const drawControl = new L.Control.Draw({
            edit: { featureGroup: drawnItems },
            draw: {
                polygon: false, rectangle: false, circle: false, 
                marker: false, circlemarker: false,
                polyline: {
                    shapeOptions: { color: '#00d4ff', weight: 4 }
                }
            }
        });
        map.addControl(drawControl);

        map.on(L.Draw.Event.CREATED, function (e) {
            drawnItems.clearLayers();
            const layer = e.layer;
            drawnItems.addLayer(layer);
            
            const coords = layer.getLatLngs();
            document.getElementById('pathCoordsInput').value = JSON.stringify(coords);
            
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Plan';
        });

        map.on(L.Draw.Event.DELETED, function() {
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('pathCoordsInput').value = '';
        });
    }
});