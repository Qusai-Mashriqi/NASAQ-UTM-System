document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Map
    window.map = L.map('map').setView([31.95, 35.91], 13);
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const tileUrl = isDark ? 
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' : 
        'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
    L.tileLayer(tileUrl, { maxZoom: 20 }).addTo(map);

    // 2. Load Zones (Shared API)
    fetch('/pilot/get_operational_zones')
    .then(res => res.json())
    .then(data => {
        data.forEach(zone => {
            const color = zone.type === 'red' ? '#ff2a6d' : (zone.type === 'yellow' ? '#ffc107' : '#00f0b5');
            let coords = zone.coords;
            if (typeof coords === 'string') { try { coords = JSON.parse(coords); } catch(e) {} }
            
            try {
                if (coords.type === 'circle' || (coords.lat && coords.radius)) {
                    L.circle([coords.lat, coords.lng], { radius: coords.radius, color: color, fillOpacity: 0.2 }).addTo(map);
                } else {
                    L.polygon(coords, { color: color, fillOpacity: 0.2 }).addTo(map);
                }
            } catch(e) {}
        });
    });

    // 3. Start Simulation
    // Note: window.flightConfig must be defined in HTML before loading this script
    if (window.flightConfig) {
        startSimulation(window.flightConfig);
    }
});

function startSimulation(config) {
    const maxAllowedAlt = Number(config.maxAlt);
    const simulationDuration = 15000; // 15 seconds
    let startTime = null;
    let animationFrameId;

    try {
        const pathData = typeof config.pathData === 'string' ? JSON.parse(config.pathData) : config.pathData;
        
        if (pathData && pathData.length > 0) {
            // Draw Path
            const polyline = L.polyline(pathData, {color: 'rgba(0, 212, 255, 0.4)', weight: 3, dashArray: '5, 10'}).addTo(map);
            map.fitBounds(polyline.getBounds(), {padding: [80, 80]});

            // Drone Icon
            const droneIconHtml = `<svg class="drone-svg" viewBox="0 0 512 512" width="40" height="40" fill="${config.droneColor || '#00d4ff'}" xmlns="http://www.w3.org/2000/svg"><path d="M448 64c-17.7 0-32 14.3-32 32v32h-48V80c0-26.5-21.5-48-48-48s-48 21.5-48 48v48H240V80c0-26.5-21.5-48-48-48s-48 21.5-48 48v48H96V96c0-17.7-14.3-32-32-32S32 78.3 32 96v32c0 17.7 14.3 32 32 32h48v48c-26.5 0-48 21.5-48 48s21.5 48 48 48v48H64c-17.7 0-32 14.3-32 32s14.3 32 32 32v32c0 17.7 14.3 32 32 32s32-14.3 32-32v-32h48v48c0 26.5 21.5 48 48 48s48-21.5 48-48v-48h48v32c0 17.7 14.3 32 32 32s32-14.3 32-32v-32c0-17.7-14.3-32-32-32h-48v-48c26.5 0 48-21.5 48-48s-21.5-48-48-48v-48h48v32c0 17.7 14.3 32 32 32s32-14.3 32-32V96c0-17.7-14.3-32-32-32zM192 192a64 64 0 1 1 128 0 64 64 0 1 1 -128 0z"/></svg>`;
            const droneIcon = L.divIcon({ className: 'drone-marker', html: droneIconHtml, iconSize: [40, 40], iconAnchor: [20, 20] });
            const marker = L.marker(pathData[0], {icon: droneIcon}).addTo(map);

            // Calculate Distance
            let totalDistance = 0;
            for(let i=0; i<pathData.length-1; i++) totalDistance += map.distance(pathData[i], pathData[i+1]);

            // Helper: Get Point at %
            const getPointAtPercent = (percent) => {
                const targetDist = totalDistance * percent;
                let currentDist = 0;
                for(let i=0; i<pathData.length-1; i++) {
                    const segmentDist = map.distance(pathData[i], pathData[i+1]);
                    if (currentDist + segmentDist >= targetDist) {
                        const segmentPercent = (targetDist - currentDist) / segmentDist;
                        const lat = pathData[i].lat + (pathData[i+1].lat - pathData[i].lat) * segmentPercent;
                        const lng = pathData[i].lng + (pathData[i+1].lng - pathData[i].lng) * segmentPercent;
                        return [lat, lng];
                    }
                    currentDist += segmentDist;
                }
                return pathData[pathData.length - 1];
            };

            // Animation Loop
            const animate = (timestamp) => {
                if (!startTime) startTime = timestamp;
                const elapsed = timestamp - startTime;
                const progress = elapsed / simulationDuration;

                if (progress < 1) {
                    const newLatLng = getPointAtPercent(progress);
                    marker.setLatLng(newLatLng);
                    
                    // Update UI
                    updateUI(progress, elapsed, maxAllowedAlt);
                    
                    animationFrameId = requestAnimationFrame(animate);
                } else {
                    marker.setLatLng(pathData[pathData.length - 1]);
                    finishSimulation();
                }
            };
            requestAnimationFrame(animate);
            
            // Expose abort function to global scope if needed
            window.abortMission = () => {
                cancelAnimationFrame(animationFrameId);
                const signalEl = document.getElementById('signal-status');
                if(signalEl) {
                    signalEl.className = "badge bg-danger";
                    signalEl.innerText = "SIGNAL: LOST";
                    document.querySelector('.drone-svg').style.fill = 'red';
                    alert("MISSION ABORTED BY PILOT.");
                }
            };
        }
    } catch(e) { console.error("Sim Error", e); }
}

function updateUI(progress, elapsed, maxAlt) {
    const progressEl = document.getElementById('flight-progress');
    if(progressEl) progressEl.style.width = (progress * 100) + '%';
    
    const timerEl = document.getElementById('timer-display');
    if(timerEl) timerEl.innerText = "00:" + String(Math.floor(elapsed / 1000)).padStart(2, '0');
    
    const altEl = document.getElementById('alt-display');
    if(altEl) {
        let simulatedAlt = (maxAlt * 0.8) + (Math.sin(elapsed / 1000) * 5);
        if(simulatedAlt > maxAlt) simulatedAlt = maxAlt;
        altEl.innerText = simulatedAlt.toFixed(1) + ' m';
    }

    const speedEl = document.getElementById('speed-display');
    if(speedEl) {
        let simulatedSpeed = 25 + (Math.random() * 5) - 2.5; 
        if(simulatedSpeed > 30) simulatedSpeed = 30.0;
        speedEl.innerText = simulatedSpeed.toFixed(1) + ' km/h';
    }
}

function finishSimulation() {
    const progressEl = document.getElementById('flight-progress');
    if(progressEl) progressEl.style.width = '100%';
    
    const timerEl = document.getElementById('timer-display');
    if(timerEl) timerEl.innerText = "Finished";
    
    const speedEl = document.getElementById('speed-display');
    if(speedEl) speedEl.innerText = "0.0 km/h";

    const successModalEl = document.getElementById('successModal');
    if(successModalEl) {
        const successModal = new bootstrap.Modal(successModalEl);
        successModal.show();
    }
}