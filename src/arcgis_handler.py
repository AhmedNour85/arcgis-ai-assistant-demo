"""
ArcGIS Handler Module
Handles all ArcGIS operations including map creation, geocoding, and feature services
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Any
from arcgis.gis import GIS
from arcgis.geocoding import geocode, reverse_geocode
from arcgis.geometry import Point, Polygon, Polyline
from arcgis.features import FeatureLayer, FeatureSet, Feature
from arcgis.mapping import WebMap
import requests


class ArcGISHandler:
    """Handler for ArcGIS operations"""
    
    def __init__(self, api_key: Optional[str] = None, username: Optional[str] = None, 
                 password: Optional[str] = None):
        """
        Initialize ArcGIS Handler
        
        Args:
            api_key: ArcGIS API key
            username: ArcGIS username
            password: ArcGIS password
        """
        self.api_key = api_key
        self.username = username
        self.password = password
        self.gis = None
        
        self._initialize_gis()
    
    def _initialize_gis(self):
        """Initialize GIS connection"""
        try:
            # Try to connect with different authentication methods
            if self.api_key:
                # Connect with API key
                self.gis = GIS(api_key=self.api_key)
                print('Connected using Api Key')
            elif self.username and self.password:
                # Connect with username/password
                self.gis = GIS(username=self.username, password=self.password)
                print('Connected using usename')
            else:
                # Connect anonymously (limited functionality)
                self.gis = GIS()
                print('Connected Anonymous')
            
            #print(f"Connected to ArcGIS as: {self.gis.users.me.username if self.gis.users.me else 'Anonymous'}")
        
        except Exception as e:
            # Fallback to anonymous connection
            print(f"Warning: Could not authenticate with ArcGIS. Using anonymous access: {str(e)}")
            try:
                self.gis = GIS()
            except Exception as e2:
                raise Exception(f"Failed to initialize ArcGIS: {str(e2)}")
    
    def geocode_location(self, location: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Geocode a location string to coordinates
        
        Args:
            location: Location string (address, city, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of geocoding results with coordinates and attributes
        """
        try:
            results = geocode(location, max_locations=max_results)
            
            geocoded_results = []
            for result in results:
                geocoded_results.append({
                    'address': result.get('address', ''),
                    'location': {
                        'x': result['location']['x'],
                        'y': result['location']['y']
                    },
                    'score': result.get('score', 0),
                    'attributes': result.get('attributes', {})
                })
            
            return geocoded_results
        
        except Exception as e:
            raise Exception(f"Error geocoding location '{location}': {str(e)}")
    
    def reverse_geocode_point(self, longitude: float, latitude: float) -> Dict[str, Any]:
        """
        Reverse geocode coordinates to address
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            
        Returns:
            Address information
        """
        try:
            result = reverse_geocode([longitude, latitude])
            
            return {
                'address': result.get('address', {}),
                'location': {
                    'x': longitude,
                    'y': latitude
                }
            }
        
        except Exception as e:
            raise Exception(f"Error reverse geocoding ({longitude}, {latitude}): {str(e)}")
    
    def search_features(self, query: str, feature_type: Optional[str] = None, 
                       bbox: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        """
        Search for features in ArcGIS Online
        
        Args:
            query: Search query
            feature_type: Type of feature to search for
            bbox: Bounding box [xmin, ymin, xmax, ymax]
            
        Returns:
            List of features found
        """
        try:
            # Build search query
            search_query = query
            if feature_type:
                search_query += f" AND type:{feature_type}"
            
            # Search for content
            items = self.gis.content.search(
                query=search_query,
                item_type="Feature Layer",
                max_items=10
            )
            
            features = []
            for item in items:
                features.append({
                    'id': item.id,
                    'title': item.title,
                    'type': item.type,
                    'url': item.url,
                    'snippet': item.snippet,
                    'extent': item.extent
                })
            
            return features
        
        except Exception as e:
            print(f"Warning: Error searching features: {str(e)}")
            return []
    
    def create_map_widget(self, map_style: str = "streets", zoom_level: int = 10,
                         center: Optional[Tuple[float, float]] = None,
                         map_data: Optional[Dict] = None) -> str:
        """
        Create an HTML map widget
        
        Args:
            map_style: Base map style
            zoom_level: Zoom level
            center: Center coordinates (longitude, latitude)
            map_data: Data to display on map
            
        Returns:
            HTML string for map widget
        """
        try:
            # Default center (USA)
            if center is None:
                center = (-98.5795, 39.8283)
            
            # Map style URLs
            basemap_urls = {
                'streets': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer',
                'satellite': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer',
                'hybrid': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer',
                'topo': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer',
                'gray': 'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer',
                'dark-gray': 'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer',
                'oceans': 'https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer'
            }
            
            basemap_url = basemap_urls.get(map_style, basemap_urls['streets'])
            
            # Prepare features for display
            features_json = "[]"
            if map_data and 'features' in map_data:
                features_json = json.dumps(map_data['features'])
            
            # Create HTML with Leaflet (simpler alternative to ArcGIS JS API)
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArcGIS Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        #map {{
            width: 100%;
            height: 100vh;
        }}
        .feature-popup {{
            font-family: Arial, sans-serif;
        }}
        .feature-popup h3 {{
            margin: 0 0 10px 0;
            color: #0079c1;
        }}
        .feature-popup p {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // Initialize map
        var map = L.map('map').setView([{center[1]}, {center[0]}], {zoom_level});
        
        // Add base map
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Powered by ArcGIS',
            maxZoom: 19
        }}).addTo(map);
        
        // Add features
        var features = {features_json};
        
        features.forEach(function(feature) {{
            if (feature.geometry && feature.geometry.type === 'Point') {{
                var coords = feature.geometry.coordinates;
                var marker = L.marker([coords[1], coords[0]]).addTo(map);
                
                // Create popup content
                var popupContent = '<div class="feature-popup">';
                if (feature.properties) {{
                    if (feature.properties.name) {{
                        popupContent += '<h3>' + feature.properties.name + '</h3>';
                    }}
                    for (var key in feature.properties) {{
                        if (key !== 'name') {{
                            popupContent += '<p><strong>' + key + ':</strong> ' + feature.properties[key] + '</p>';
                        }}
                    }}
                }}
                popupContent += '</div>';
                
                marker.bindPopup(popupContent);
            }}
            else if (feature.geometry && feature.geometry.type === 'Polygon') {{
                var coords = feature.geometry.coordinates[0].map(function(coord) {{
                    return [coord[1], coord[0]];
                }});
                var polygon = L.polygon(coords, {{
                    color: '#0079c1',
                    fillColor: '#0079c1',
                    fillOpacity: 0.3
                }}).addTo(map);
                
                if (feature.properties && feature.properties.name) {{
                    polygon.bindPopup('<div class="feature-popup"><h3>' + feature.properties.name + '</h3></div>');
                }}
            }}
        }});
        
        // Fit bounds if features exist
        if (features.length > 0) {{
            var group = new L.featureGroup(map._layers);
            if (Object.keys(group._layers).length > 0) {{
                map.fitBounds(group.getBounds().pad(0.1));
            }}
        }}
    </script>
</body>
</html>
"""
            
            return html
        
        except Exception as e:
            raise Exception(f"Error creating map widget: {str(e)}")
    
    def create_feature_from_geocode(self, geocode_result: Dict) -> Dict[str, Any]:
        """
        Create a GeoJSON feature from geocode result
        
        Args:
            geocode_result: Geocode result dictionary
            
        Returns:
            GeoJSON feature
        """
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    geocode_result['location']['x'],
                    geocode_result['location']['y']
                ]
            },
            'properties': {
                'name': geocode_result.get('address', 'Unknown'),
                'score': geocode_result.get('score', 0),
                **geocode_result.get('attributes', {})
            }
        }
    
    def create_buffer(self, longitude: float, latitude: float, 
                     distance: float, unit: str = "miles") -> Dict[str, Any]:
        """
        Create a buffer around a point
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            distance: Buffer distance
            unit: Distance unit (miles, kilometers, meters)
            
        Returns:
            GeoJSON polygon feature
        """
        try:
            from arcgis.geometry import Point, buffer
            
            point = Point({'x': longitude, 'y': latitude, 'spatialReference': {'wkid': 4326}})
            
            # Convert distance to meters
            distance_meters = distance
            if unit == "miles":
                distance_meters = distance * 1609.34
            elif unit == "kilometers":
                distance_meters = distance * 1000
            
            buffered = buffer([point], distance_meters, unit='meters')
            
            # Convert to GeoJSON
            if buffered and len(buffered) > 0:
                geom = buffered[0]
                return {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': geom['rings'] if geom['rings'] else []
                    },
                    'properties': {
                        'buffer_distance': distance,
                        'buffer_unit': unit
                    }
                }
            
            return None
        
        except Exception as e:
            print(f"Warning: Error creating buffer: {str(e)}")
            return None
    
    def get_feature_layer(self, url: str) -> Optional[FeatureLayer]:
        """
        Get a feature layer from URL
        
        Args:
            url: Feature layer URL
            
        Returns:
            FeatureLayer object or None
        """
        try:
            return FeatureLayer(url)
        except Exception as e:
            print(f"Error getting feature layer: {str(e)}")
            return None
    
    def query_feature_layer(self, layer_url: str, where_clause: str = "1=1",
                           geometry: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Query a feature layer
        
        Args:
            layer_url: Feature layer URL
            where_clause: SQL where clause
            geometry: Geometry for spatial query
            
        Returns:
            List of features
        """
        try:
            layer = FeatureLayer(layer_url)
            
            query_result = layer.query(
                where=where_clause,
                geometry_filter=geometry,
                return_geometry=True,
                out_fields="*"
            )
            
            features = []
            for feature in query_result.features:
                geom = feature.geometry
                attrs = feature.attributes
                
                # Convert to GeoJSON
                geojson_feature = {
                    'type': 'Feature',
                    'geometry': self._arcgis_geometry_to_geojson(geom),
                    'properties': attrs
                }
                features.append(geojson_feature)
            
            return features
        
        except Exception as e:
            print(f"Error querying feature layer: {str(e)}")
            return []
    
    def _arcgis_geometry_to_geojson(self, geometry: Dict) -> Dict:
        """
        Convert ArcGIS geometry to GeoJSON
        
        Args:
            geometry: ArcGIS geometry dictionary
            
        Returns:
            GeoJSON geometry
        """
        if 'x' in geometry and 'y' in geometry:
            # Point
            return {
                'type': 'Point',
                'coordinates': [geometry['x'], geometry['y']]
            }
        elif 'paths' in geometry:
                # Polyline
                if geometry['paths']:
                    if len(geometry['paths']) > 1:
                        return {
                            'type': 'MultiLineString',
                            'coordinates': geometry['paths']
                        }
                    else:
                        return {
                            'type': 'LineString',
                            'coordinates': geometry['paths'][0]
                        }
                else:
                    return None
        elif 'rings' in geometry:
                # Polygon
                # ArcGIS 'rings' format is already an array of linear rings.
                # GeoJSON Polygon coordinates are an array of linear ring coordinate arrays.
                if geometry['rings']:
                    return {
                        'type': 'Polygon',
                        'coordinates': geometry['rings']
                    }
                else:
                    return None
        else:
            return None

