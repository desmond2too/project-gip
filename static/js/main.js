/**
 * GeoEstate main JavaScript file
 * This file handles all the frontend functionality and API interactions
 */

// Global variables
let map;
let propertyMarkers = [];
let currentRouteLayer = null;
let userLocationMarker = null;

// Initialize map and functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    initUI();
    loadProperties();
});

// Initialize the map
function initMap() {
    // Create map centered on Windhoek, Namibia
    map = L.map('map').setView([-22.559, 17.083], 13);
    
    // Add base map layers
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });
    
    // Add layer control
    const baseMaps = {
        "OpenStreetMap": osm,
        "Satellite": satellite
    };
    
    L.control.layers(baseMaps).addTo(map);
}

// Initialize UI elements and event listeners
function initUI() {
    // Toggle search panel
    document.getElementById('searchToggle').addEventListener('click', function() {
        const propertySearch = document.getElementById('propertySearch');
        if (propertySearch.style.display === 'block') {
            propertySearch.style.display = 'none';
        } else {
            propertySearch.style.display = 'block';
        }
    });
    
    // Toggle sidebar on mobile
    document.getElementById('toggleSidebar').addEventListener('click', function() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('hidden');
    });
    
    // Current location button
    document.getElementById('currentLocation').addEventListener('click', function() {
        getUserLocation();
    });
    
    // Price estimator button
    document.getElementById('priceEstimatorBtn').addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('priceEstimationModal'));
        modal.show();
    });
    
    // Calculate estimate button
    document.getElementById('calculateEstimateBtn').addEventListener('click', function() {
        calculatePriceEstimate();
    });
    
    // Property search form submission
    document.getElementById('property-search-form').addEventListener('submit', function(e) {
        e.preventDefault();
        searchProperties();
    });
    
    // Location search
    document.getElementById('locationSearchBtn').addEventListener('click', function() {
        searchLocation();
    });
    
    // Enter key in location search field
    document.getElementById('locationSearch').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchLocation();
        }
    });
}

// Load properties from the API
function loadProperties() {
    fetch('/api/properties')
        .then(response => response.json())
        .then(properties => {
            displayProperties(properties);
        })
        .catch(error => {
            console.error('Error loading properties:', error);
        });
}

// Display properties on the map and sidebar
function displayProperties(properties) {
    // Clear existing markers
    clearPropertyMarkers();
    
    // Clear property list
    const propertyList = document.getElementById('propertyList');
    propertyList.innerHTML = '';
    
    // Add properties to map and list
    properties.forEach(property => {
        addPropertyToMap(property);
        addPropertyToList(property);
    });
    
    // Update result count
    document.getElementById('resultCount').textContent = properties.length;
}

// Add a property marker to the map
function addPropertyToMap(property) {
    // Create custom price marker
    const markerSize = property.price > 200000 ? 50 : 40;
    const priceMarker = L.divIcon({
        className: 'price-marker',
        html: `N$${property.price.toLocaleString()}`,
        iconSize: [markerSize, markerSize]
    });
    
    // Add marker to map
    const marker = L.marker([property.lat, property.lng], {icon: priceMarker});
    
    // Create popup content
    const popupContent = `
        <div class="property-popup">
            <img src="${property.image}" alt="Property">
            <h5>N$ ${property.price.toLocaleString()}</h5>
            <p>${property.bedrooms} bedrooms • ${property.bathrooms} baths • ${property.area} sqm</p>
            <p>${property.address}</p>
            <button class="btn btn-sm btn-primary route-btn" data-lat="${property.lat}" data-lng="${property.lng}">
                <i class="fas fa-route"></i> Show Route
            </button>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    marker.on('popupopen', function() {
        // Add route button click handler
        document.querySelectorAll('.route-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const lat = parseFloat(this.dataset.lat);
                const lng = parseFloat(this.dataset.lng);
                
                if (userLocationMarker) {
                    const userLatLng = userLocationMarker.getLatLng();
                    showRoute(userLatLng.lat, userLatLng.lng, lat, lng);
                } else {
                    getUserLocation(function(userLat, userLng) {
                        showRoute(userLat, userLng, lat, lng);
                    });
                }
            });
        });
    });
    
    marker.addTo(map);
    propertyMarkers.push(marker);
}

// Add a property to the sidebar list
function addPropertyToList(property) {
    const propertyList = document.getElementById('propertyList');
    const propertyCard = document.createElement('div');
    propertyCard.classList.add('card', 'property-card');
    propertyCard.innerHTML = `
        <div class="card-body">
            <h6>N$${property.price.toLocaleString()}</h6>
            <p class="small mb-0">${property.bedrooms} beds • ${property.bathrooms} baths</p>
            <p class="small mb-0">${property.address}</p>
            <p class="small mb-0">Property Type ${property.type}</p>
        </div>
    `;
    
    propertyCard.addEventListener('click', function() {
        map.setView([property.lat, property.lng], 16);
        // Find and open the popup for this property
        propertyMarkers.forEach(marker => {
            const markerLatLng = marker.getLatLng();
            if (markerLatLng.lat === property.lat && markerLatLng.lng === property.lng) {
                marker.openPopup();
            }
        });
    });
    
    propertyList.appendChild(propertyCard);
}

// Clear all property markers from the map
function clearPropertyMarkers() {
    propertyMarkers.forEach(marker => {
        map.removeLayer(marker);
    });
    propertyMarkers = [];
}

// Get user's current location
function getUserLocation(callback) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            // Update or create user location marker
            if (userLocationMarker) {
                userLocationMarker.setLatLng([lat, lng]);
            } else {
                userLocationMarker = L.marker([lat, lng], {
                    icon: L.divIcon({
                        className: 'user-location-marker',
                        html: '<i class="fas fa-user-circle fa-3x" style="color: #0d6efd;"></i>',
                        iconSize: [30, 30],
                        iconAnchor: [15, 15]
                    })
                }).addTo(map);
            }
            
            map.setView([lat, lng], 15);
            
            if (callback) {
                callback(lat, lng);
            }
        }, function(error) {
            console.error('Error getting location:', error);
            alert('Could not determine your location. Please allow location access.');
        });
    } else {
        alert('Geolocation is not supported by your browser.');
    }
}

// Search for properties based on form inputs
function searchProperties() {
    // Gather form data
    const location = document.getElementById('location').value;
    
    // Get selected property types
    const propertyTypes = [];
    if (document.getElementById('residential').checked) propertyTypes.push('residential');
    if (document.getElementById('commercial').checked) propertyTypes.push('commercial');
    if (document.getElementById('industrial').checked) propertyTypes.push('industrial');
    
    // Get selected deal types
    const dealTypes = [];
    if (document.getElementById('for-sale').checked) dealTypes.push('sale');
    if (document.getElementById('for-rent').checked) dealTypes.push('rent');
    
    // Price range
    const minPrice = document.getElementById('min-price').value;
    const maxPrice = document.getElementById('max-price').value;
    
    // Features
    const bedrooms = document.getElementById('bedrooms').value;
    const bathrooms = document.getElementById('bathrooms').value;
    
    // Proximity
    const proximities = [];
    if (document.getElementById('schools').checked) proximities.push('schools');
    if (document.getElementById('hospitals').checked) proximities.push('hospitals');
    if (document.getElementById('transport').checked) proximities.push('transport');
    if (document.getElementById('shopping').checked) proximities.push('shopping');
    
    // Search criteria
    const searchCriteria = {
        location: location,
        property_types: propertyTypes,
        deal_types: dealTypes,
        min_price: minPrice,
        max_price: maxPrice,
        bedrooms: bedrooms,
        bathrooms: bathrooms,
        proximities: proximities
    };
    
    // Send search request to API
    fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(searchCriteria)
    })
    .then(response => response.json())
    .then(properties => {
        displayProperties(properties);
        
        // If location is specified, center map there
        if (location) {
            searchLocation(location);
        }
    })
    .catch(error => {
        console.error('Error searching properties:', error);
    });
}

// Search for a location and center the map
function searchLocation(locationQuery) {
    // Use the value from input field if not provided
    if (!locationQuery) {
        locationQuery = document.getElementById('locationSearch').value;
    }
    
    if (!locationQuery) return;
    
    // Call geocoding API
    fetch(`/api/geocode?location=${encodeURIComponent(locationQuery)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                map.setView([data.lat, data.lng], 14);
                
                // Add a marker for the location
                L.marker([data.lat, data.lng])
                    .addTo(map)
                    .bindPopup(data.formatted_address)
                    .openPopup();
            } else {
                alert(data.error || 'Location not found');
            }
        })
        .catch(error => {
            console.error('Error searching location:', error);
        });
}

// Show route between two points
function showRoute(startLat, startLng, endLat, endLng) {
    // Clear existing route
    if (currentRouteLayer) {
        map.removeLayer(currentRouteLayer);
    }
    
    // Get route from API
    fetch(`/api/route?start_lat=${startLat}&start_lng=${startLng}&end_lat=${endLat}&end_lng=${endLng}`)
        .then(response => response.json())
        .then(routeData => {
            if (routeData.success) {
                // Create array of points for the polyline
                const points = [routeData.start, ...routeData.waypoints, routeData.end];
                
                // Create route polyline
                currentRouteLayer = L.polyline(points, {
                    color: '#0d6efd',
                    weight: 5,
                    opacity: 0.7
                }).addTo(map);
                
                // Fit map to show the entire route
                map.fitBounds(currentRouteLayer.getBounds(), {
                    padding: [50, 50]
                });
                
                // Show route information
                const message = `Distance: ${routeData.distance} km, Duration: ${Math.round(routeData.duration)} minutes`;
                L.popup()
                    .setLatLng(points[Math.floor(points.length / 2)])
                    .setContent(message)
                    .openOn(map);
            }
        })
        .catch(error => {
            console.error('Error calculating route:', error);
        });
}

// Calculate and display price estimate
function calculatePriceEstimate() {
    // Gather form data
    const propertyType = document.getElementById('est-property-type').value;
    const location = document.getElementById('est-location').value;
    const bedrooms = parseInt(document.getElementById('est-bedrooms').value);
    const bathrooms = parseInt(document.getElementById('est-bathrooms').value);
    const area = parseFloat(document.getElementById('est-area').value);
    const age = parseInt(document.getElementById('est-age').value);
    const condition = document.getElementById('est-condition').value;
    
    // Features
    const garage = document.getElementById('est-garage').checked;
    const pool = document.getElementById('est-pool').checked;
    const garden = document.getElementById('est-garden').checked;
    const security = document.getElementById('est-security').checked;
    const aircon = document.getElementById('est-aircon').checked;
    const furnished = document.getElementById('est-furnished').checked;
    
    // Validate inputs
    if (!propertyType || !location || isNaN(area) || area <= 0) {
        alert('Please fill in all required fields.');
        return;
    }
    
    // Prepare data for API
    const estimateData = {
        property_type: propertyType,
        location: location,
        bedrooms: bedrooms,
        bathrooms: bathrooms,
        area: area,
        age: age,
        condition: condition,
        garage: garage,
        pool: pool,
        garden: garden,
        security: security,
        aircon: aircon,
        furnished: furnished
    };
    
    // Send to API
    fetch('/api/estimate-price', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(estimateData)
    })
    .then(response => response.json())
    .then(data => {
        // Display result
        document.getElementById('estimated-price-value').textContent = `$${data.estimated_price.toLocaleString()}`;
        document.getElementById('estimation-result').style.display = 'block';
    })
    .catch(error => {
        console.error('Error calculating estimate:', error);
        alert('An error occurred while calculating the price estimate.');
    });
}