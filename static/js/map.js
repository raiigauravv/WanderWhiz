let map;
let infoWindow;

function initMap() {
  console.log('initMap function called');
  
  // Get data from global variables (set by Flask template)
  const mapElement = document.getElementById("map");
  const lat = window.mapCenter ? window.mapCenter.lat : 43.65107;
  const lng = window.mapCenter ? window.mapCenter.lng : -79.347015;
  const placesData = window.placesData || [];
  
  console.log('🗺️ Map center:', lat, lng);
  console.log('📦 Places data:', placesData);
  console.log('📊 Number of places:', placesData.length);
  
  const mapCenter = { lat: lat, lng: lng };
  
  try {
    map = new google.maps.Map(mapElement, {
      center: mapCenter,
      zoom: 13,
      styles: [
        {
          featureType: "poi",
          elementType: "labels",
          stylers: [{ visibility: "on" }]
        }
      ]
    });
    console.log('Map created successfully');

    infoWindow = new google.maps.InfoWindow();
    
    // If we have places from search, show them
    if (placesData && placesData.length > 0) {
      console.log('Adding search results:', placesData.length, 'places');
      
      placesData.forEach(place => {
        if (place.geometry && place.geometry.location) {
          const marker = new google.maps.Marker({
            position: {
              lat: place.geometry.location.lat,
              lng: place.geometry.location.lng,
            },
            map: map,
            title: place.name,
            icon: 'https://maps.google.com/mapfiles/ms/icons/orange-dot.png' // Orange for discovered places
          });

          const content = `
            <div style="padding: 10px; max-width: 250px;">
              <h3 style="margin: 0 0 10px 0; color: #2c3e50;">${place.name}</h3>
              <p style="margin: 0; color: #666;"><strong>Rating:</strong> ${place.rating || 'N/A'} ⭐</p>
              <p style="margin: 5px 0 0 0; color: #666;"><strong>Address:</strong> ${place.vicinity || 'N/A'}</p>
              ${place.price_level ? `<p style="margin: 5px 0 0 0; color: #666;"><strong>Price:</strong> ${'$'.repeat(place.price_level)}</p>` : ''}
            </div>
          `;

          marker.addListener("click", () => {
            infoWindow.setContent(content);
            infoWindow.open(map, marker);
          });
        }
      });
      
      // If we have search results, zoom to fit all markers
      if (placesData.length > 0) {
        const bounds = new google.maps.LatLngBounds();
        placesData.forEach(place => {
          if (place.geometry && place.geometry.location) {
            bounds.extend(new google.maps.LatLng(
              place.geometry.location.lat,
              place.geometry.location.lng
            ));
          }
        });
        map.fitBounds(bounds);
      }
    } else {
      // Default Toronto cultural spots if no search results
      console.log('Showing default Toronto cultural spots');
      addDefaultTorontoSpots();
    }

  } catch (error) {
    console.error('Error creating map:', error);
  }
}

function addDefaultTorontoSpots() {
  const culturalSpots = [
    {
      position: { lat: 43.6532, lng: -79.3832 },
      title: "CN Tower",
      description: "Iconic Toronto landmark with stunning city views",
      type: "landmark"
    },
    {
      position: { lat: 43.6426, lng: -79.3871 },
      title: "St. Lawrence Market",
      description: "Historic market with local foods and crafts",
      type: "market"
    },
    {
      position: { lat: 43.6677, lng: -79.3948 },
      title: "Casa Loma",
      description: "Gothic Revival castle with beautiful gardens",
      type: "castle"
    },
    {
      position: { lat: 43.6544, lng: -79.3960 },
      title: "Kensington Market",
      description: "Bohemian neighborhood with vintage shops",
      type: "market"
    },
    {
      position: { lat: 43.6591, lng: -79.3977 },
      title: "Chinatown",
      description: "Vibrant area with authentic Asian cuisine",
      type: "culture"
    }
  ];

  // Add markers for each cultural spot
  culturalSpots.forEach(spot => {
    const marker = new google.maps.Marker({
      position: spot.position,
      map: map,
      title: spot.title,
      icon: getMarkerIcon(spot.type)
    });

    marker.addListener('click', () => {
      infoWindow.setContent(`
        <div style="padding: 10px;">
          <h3 style="margin: 0 0 10px 0; color: #2c3e50;">${spot.title}</h3>
          <p style="margin: 0; color: #666;">${spot.description}</p>
        </div>
      `);
      infoWindow.open(map, marker);
    });
  });
}

function getMarkerIcon(type) {
  const icons = {
    landmark: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
    market: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
    castle: 'https://maps.google.com/mapfiles/ms/icons/purple-dot.png',
    culture: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png'
  };
  return icons[type] || 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png';
}

// Add error handling for Google Maps API loading
window.gm_authFailure = function() {
  console.error('Google Maps API authentication failed');
  document.getElementById('map').innerHTML = '<p style="color: red; padding: 20px;">Google Maps API authentication failed. Please check your API key.</p>';
};

// Check if Google Maps API loaded
function checkGoogleMaps() {
  if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
    console.error('Google Maps API failed to load');
    document.getElementById('map').innerHTML = '<p style="color: red; padding: 20px;">Google Maps API failed to load. Please check your internet connection and API key.</p>';
  } else {
    console.log('Google Maps API loaded successfully');
  }
}

// Check after a delay
setTimeout(checkGoogleMaps, 3000);
