let geojson;
let highlightedLayer = null;

// Initialize map
var map = L.map('map', {
    minZoom: 9.5,
    maxZoom: 16
})

// Restrict panning/zooming tightly to NYC metro (boroughs + NJ waterfront)
var bounds = L.latLngBounds(
    L.latLng(40.40, -74.45),  // SW: southern Staten Island / central NJ
    L.latLng(40.95, -73.65)   // NE: northern Bronx / eastern Queens
);
map.setMaxBounds(bounds);
map.fitBounds(bounds);
map.on('drag', function() {
    map.panInsideBounds(bounds, { animate: false });
});
/*
map.on('zoomstart', function() {
    if (highlightedLayer) {
        geojson.resetStyle(highlightedLayer);
        highlightedLayer = null;
    }
});
*/
// Add tile layer
L.tileLayer('https://api.maptiler.com/maps/openstreetmap/{z}/{x}/{y}.jpg?key=PomQwQ81LXSQaSTsapyk', {
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>'
}).addTo(map);

// ── Field definitions ──────────────────────────────────────────────────────────
// Each field has: label, color ramp (low→high), breakpoints, and a formatter
const fieldConfig = {
    median_gross_rent: {
        label: "Median Gross Rent",
        colors: ['#FEB24C','#FD8D3C','#FC4E2A','#E31A1C','#BD0026','#800026'],
        breaks: [2000, 2500, 3000, 3500, 4000],
        format: v => v != null ? `$${Number(v).toLocaleString()}` : 'N/A'
    },
    median_household_income: {
        label: "Median Household Income",
        colors: ['#EDF8E9','#BAE4B3','#74C476','#31A354','#006D2C','#00441B'],
        breaks: [40000, 60000, 80000, 100000, 130000],
        format: v => v != null ? `$${Number(v).toLocaleString()}` : 'N/A'
    },
    total_population: {
        label: "Total Population",
        colors: ['#F1EEF6','#BDC9E1','#74A9CF','#2B8CBE','#0570B0','#034E7B'],
        breaks: [5000, 10000, 20000, 35000, 50000],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    },
    housing_units_total: {
        label: "Total Housing Units",
        colors: ['#F7F4F9','#D4B9DA','#C994C7','#DF65B0','#E7298A','#91003F'],
        breaks: [2000, 4000, 7000, 11000, 16000],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    },
    renter_occupied_units: {
        label: "Renter Occupied Units",
        colors: ['#FEEDDE','#FDD0A2','#FDAE6B','#FD8D3C','#E6550D','#A63603'],
        breaks: [500, 1500, 3000, 5000, 8000],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    },
    owner_occupied_units: {
        label: "Owner Occupied Units",
        colors: ['#F7FBFF','#DEEBF7','#C6DBEF','#9ECAE1','#4292C6','#08306B'],
        breaks: [500, 1500, 3000, 5000, 8000],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    },
    rent_50pct_or_more_income: {
        label: "Rent ≥ 50% Income",
        colors: ['#FFFFD4','#FED98E','#FE9929','#D95F0E','#993404','#662200'],
        breaks: [100, 300, 600, 1000, 1500],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    }
};

// Active color field (default)
let activeColorField = 'median_gross_rent';

// ── Color helpers ──────────────────────────────────────────────────────────────
function getColor(value, field) {
    const cfg = fieldConfig[field];
    if (value == null) return '#ccc';
    for (let i = cfg.breaks.length - 1; i >= 0; i--) {
        if (value > cfg.breaks[i]) return cfg.colors[i + 1];
    }
    return cfg.colors[0];
}

function style(feature) {
    return {
        fillColor: getColor(feature.properties[activeColorField], activeColorField),
        weight: 1,
        color: 'white',
        fillOpacity: 0.7
    };
}

function highlightFeature(e) {
    const layer = e.target;

    if (highlightedLayer && highlightedLayer !== layer) {
        geojson.resetStyle(highlightedLayer);
    }

    layer.setStyle({
        weight: 3,
        color: '#666',
        fillOpacity: 0.9
    });

    layer.bringToFront();
    highlightedLayer = layer;
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    highlightedLayer = null;
}

// ── Tooltip ────────────────────────────────────────────────────────────────────
let selectedFields = new Set();

function buildTooltipContent(properties) {
    // Determine the "ID" dynamically
    let idLabel, idValue;
    if ("GEOID20" in properties) {
        idLabel = "ZIP";
        idValue = properties["GEOID20"];
    } else if ("BoroName" in properties) {
        idLabel = "Borough";
        idValue = properties["BoroName"];
    } else {
        idLabel = "ID";
        idValue = "N/A";
    }

    let content = `<strong>${idLabel}: ${idValue}</strong><br>`;

    selectedFields.forEach(field => {
        const cfg = fieldConfig[field];
        content += `${cfg.label}: ${cfg.format(properties[field])}<br>`;
    });

    return content;
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        mousemove: function() {
            layer.bindTooltip(buildTooltipContent(feature.properties), { sticky: true }).openTooltip();
        }
    });
}

// ── Legend (dynamic) ───────────────────────────────────────────────────────────
var legendControl = L.control({ position: 'bottomleft' });
var legendDiv;

legendControl.onAdd = function () {
    legendDiv = L.DomUtil.create('div', 'map-legend');
    updateLegend();
    return legendDiv;
};

function updateLegend() {
    if (!legendDiv) return;
    const cfg = fieldConfig[activeColorField];
    const breaks = cfg.breaks;
    const colors = cfg.colors;

    let items = '';

    // Build range labels from breaks
    for (let i = colors.length - 1; i >= 0; i--) {
        let label;
        if (i === colors.length - 1) {
            label = `&gt; ${cfg.format(breaks[breaks.length - 1])}`;
        } else if (i === 0) {
            label = `&le; ${cfg.format(breaks[0])}`;
        } else {
            label = `${cfg.format(breaks[i - 1])} &ndash; ${cfg.format(breaks[i])}`;
        }
        items += `
            <div class="legend-item">
                <span class="legend-swatch" style="background:${colors[i]}"></span>
                <span class="legend-label">${label}</span>
            </div>`;
    }

    legendDiv.innerHTML = `
        <div class="legend-title">${cfg.label}</div>
        <div class="legend-items">${items}</div>
    `;
}

legendControl.addTo(map);

// ── Re-color map ───────────────────────────────────────────────────────────────
function refreshMapColors() {
    if (!geojson) return;
    geojson.setStyle(style);
    updateLegend();
}

// ── Function to switch GeoJSON ──────────────────────────────────────────────
function loadGeoJSON(url) {
    console.log('Loading GeoJSON from:', url);
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Remove old layer if it exists
            if (geojson) {
                map.removeLayer(geojson);
                highlightedLayer = null;
            }

            // Add new layer
            geojson = L.geoJson(data, {
                style: style,
                onEachFeature: onEachFeature
            }).addTo(map);
        })
        .catch(err => console.error('Error loading GeoJSON:', err));
}

// ── Toolbar setup ─────────────────────────────────────────────────────────────
const toolbar = document.getElementById("toolbar");

// ── Color-by selector ──
const colorBySection = document.createElement("div");
colorBySection.className = "toolbar-section";
colorBySection.innerHTML = `<div class="toolbar-section-title">Color Map By</div>`;

Object.entries(fieldConfig).forEach(([key, cfg]) => {
    const label = document.createElement("label");
    label.className = "radio-label";
    label.innerHTML = `
        <input type="radio" name="colorBy" value="${key}" ${key === activeColorField ? 'checked' : ''}>
        ${cfg.label}
    `;
    colorBySection.appendChild(label);
});

toolbar.appendChild(colorBySection);

// Divider
const divider = document.createElement("div");
divider.className = "toolbar-divider";
toolbar.appendChild(divider);

// ── Tooltip fields ──
const tooltipSection = document.createElement("div");
tooltipSection.className = "toolbar-section";
tooltipSection.innerHTML = `<div class="toolbar-section-title">Show in Tooltip</div>`;

const selectAllLabel = document.createElement("label");
selectAllLabel.className = "checkbox-label";
selectAllLabel.innerHTML = `<input type="checkbox" id="selectAll"> <strong>Select All</strong>`;
tooltipSection.appendChild(selectAllLabel);

Object.entries(fieldConfig).forEach(([key, cfg]) => {
    const label = document.createElement("label");
    label.className = "checkbox-label";
    label.innerHTML = `<input type="checkbox" value="${key}"> ${cfg.label}`;
    tooltipSection.appendChild(label);
});

toolbar.appendChild(tooltipSection);

// ── Wire up radio buttons ──
document.querySelectorAll('input[name="colorBy"]').forEach(radio => {
    radio.addEventListener('change', () => {
        activeColorField = radio.value;
        refreshMapColors();
    });
});

// ── Wire up checkboxes ──
const checkboxes = document.querySelectorAll('#toolbar input[type="checkbox"]:not(#selectAll)');
const selectAll = document.getElementById("selectAll");

checkboxes.forEach(cb => {
    cb.addEventListener('change', () => {
        if (cb.checked) selectedFields.add(cb.value);
        else selectedFields.delete(cb.value);
        // Keep selectAll in sync
        selectAll.checked = [...checkboxes].every(c => c.checked);
    });
});

selectAll.addEventListener('change', () => {
    checkboxes.forEach(cb => {
        cb.checked = selectAll.checked;
        if (selectAll.checked) selectedFields.add(cb.value);
        else selectedFields.delete(cb.value);
    });
});

// Divider
const divider2 = document.createElement("div");
divider2.className = "toolbar-divider";
toolbar.appendChild(divider2);

// ── GeoJSON selector ──
const geojsonSection = document.createElement("div");
geojsonSection.className = "toolbar-section";
geojsonSection.innerHTML = `<div class="toolbar-section-title">Select Region</div>`;

const geojsonFiles = {
    'Boroughs': '../datasets/final-usables/merged_nyc_county.geojson',
    'ZIP Codes': '../datasets/final-usables/merged_nyc_zcta.geojson',
    //'Custom Layer': '../datasets/final-usables/custom_layer.geojson'
};

Object.entries(geojsonFiles).forEach(([labelText, url], idx) => {
    const label = document.createElement("label");
    label.className = "radio-label";
    label.innerHTML = `
        <input type="radio" name="geojsonFile" value="${url}" ${idx === 0 ? 'checked' : ''}>
        ${labelText}
    `;
    geojsonSection.appendChild(label);
});

toolbar.appendChild(geojsonSection);

// ── Wire up GeoJSON radio buttons ──
document.querySelectorAll('input[name="geojsonFile"]').forEach(radio => {
    radio.addEventListener('change', () => {
        loadGeoJSON(radio.value);
    });
});

loadGeoJSON('../datasets/final-usables/merged_nyc_county.geojson');