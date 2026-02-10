document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Map
    window.map = L.map('map').setView([31.95, 35.91], 11);
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const tileUrl = isDark ? 
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' : 
        'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
    
    L.tileLayer(tileUrl, { maxZoom: 20 }).addTo(map);

    // 2. Setup Draw Tools
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
        edit: { featureGroup: drawnItems },
        draw: {
            polygon: true, rectangle: true, circle: true,
            marker: false, polyline: false, circlemarker: false
        }
    });
    map.addControl(drawControl);

    let currentLayer = null;

    // 3. Event Listeners
    map.on(L.Draw.Event.CREATED, function (e) {
        currentLayer = e.layer;
        const modal = new bootstrap.Modal(document.getElementById('zoneModal'));
        modal.show();
    });

    document.getElementById('saveZoneBtn').addEventListener('click', saveZone);

    // 4. Load Initial Zones
    fetchZones();

    // --- Helper Functions ---

    function saveZone() {
        if(!currentLayer) return;

        const name = document.getElementById('zoneName').value;
        const colorType = document.getElementById('zoneColor').value;
        
        if(!name) { alert("Please enter a name"); return; }

        let coords;
        if (currentLayer instanceof L.Circle) {
            coords = { 
                type: 'circle',
                lat: currentLayer.getLatLng().lat, 
                lng: currentLayer.getLatLng().lng, 
                radius: currentLayer.getRadius() 
            };
        } else {
            coords = currentLayer.getLatLngs();
        }

        fetch('/admin/add_zone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                type: colorType,
                coords: coords
            })
        })
        .then(res => res.json())
        .then(() => {
            const modalEl = document.getElementById('zoneModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
            document.getElementById('zoneForm').reset();
            location.reload(); 
        });
    }

    function fetchZones() {
        fetch('/admin/get_zones')
        .then(res => res.json())
        .then(data => {
            const zonesList = document.getElementById('zones-list');
            
            data.forEach(zone => {
                const color = zone.type === 'red' ? '#ff2a6d' : (zone.type === 'yellow' ? '#ffc107' : '#00f0b5');
                let coords = zone.coords;
                
                if (typeof coords === 'string') {
                    try { coords = JSON.parse(coords); } catch(e) {}
                }

                try {
                    if (coords.type === 'circle' || coords.radius) {
                        L.circle([coords.lat, coords.lng], {
                            radius: coords.radius,
                            color: color,
                            fillOpacity: 0.4
                        }).addTo(map).bindPopup(`<b>${zone.name}</b>`);
                    } else {
                        L.polygon(coords, {
                            color: color, 
                            fillOpacity: 0.4
                        }).addTo(map).bindPopup(`<b>${zone.name}</b>`);
                    }

                    // Add to sidebar list
                    if(zonesList) {
                        zonesList.innerHTML += `
                            <div class="p-2 mb-2 border rounded" style="border-color: ${color} !important; border-left-width: 5px !important;">
                                <strong>${zone.name}</strong> <br>
                                <small style="color:${color}">${zone.type.toUpperCase()}</small>
                            </div>`;
                    }
                } catch(e) { console.error("Error displaying zone", e); }
            });
        });
    }
});