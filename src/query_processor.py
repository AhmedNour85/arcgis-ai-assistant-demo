"""
Query Processor Module
Coordinates between LLM and ArcGIS handlers to process user queries
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from .llm_handler import LLMHandler
from .arcgis_handler import ArcGISHandler


class QueryProcessor:
    """Processes user queries and coordinates between LLM and ArcGIS"""
    
    def __init__(self, llm_handler: LLMHandler, arcgis_handler: ArcGISHandler):
        """
        Initialize Query Processor
        
        Args:
            llm_handler: LLM handler instance
            arcgis_handler: ArcGIS handler instance
        """
        self.llm_handler = llm_handler
        self.arcgis_handler = arcgis_handler
    
    def process_query(self, query: str, map_style: str = "streets", 
                     zoom_level: int = 10) -> Dict[str, Any]:
        """
        Process user query and return results with map data
        
        Args:
            query: User query string
            map_style: Map style to use
            zoom_level: Default zoom level
            
        Returns:
            Dictionary containing response and map data
        """
        try:
            # Step 1: Analyze query using LLM
            analysis = self.llm_handler.analyze_query(query)
            
            # Step 2: Process based on intent
            intent = analysis.get('intent', 'search_location')
            
            if intent == 'search_location' or intent == 'find_features':
                result = self._process_location_query(query, analysis, map_style, zoom_level)
            elif intent == 'analyze_area':
                result = self._process_area_analysis(query, analysis, map_style, zoom_level)
            elif intent == 'get_directions':
                result = self._process_directions(query, analysis, map_style, zoom_level)
            else:
                result = self._process_general_query(query, analysis, map_style, zoom_level)
            
            return result
        
        except Exception as e:
            return {
                'response': f"I encountered an error processing your query: {str(e)}",
                'map_data': None,
                'error': str(e)
            }
    
    def _process_location_query(self, query: str, analysis: Dict, 
                               map_style: str, zoom_level: int) -> Dict[str, Any]:
        """Process location search query"""
        try:
            # Extract location from analysis
            location = analysis.get('location', query)
            
            # Geocode the location
            geocode_results = self.arcgis_handler.geocode_location(location, max_results=5)
            
            if not geocode_results:
                return {
                    'response': f"I couldn't find any results for '{location}'. Please try a different search term.",
                    'map_data': None
                }
            
            # Create features from geocode results
            features = []
            for result in geocode_results:
                feature = self.arcgis_handler.create_feature_from_geocode(result)
                features.append(feature)
            
            # Get center from first result
            center = (
                geocode_results[0]['location']['x'],
                geocode_results[0]['location']['y']
            )
            
            # Create map data
            map_data = {
                'features': features,
                'center': center,
                'zoom_level': zoom_level,
                'feature_count': len(features),
                'layer_count': 1
            }
            
            # Generate response using LLM
            response = self.llm_handler.generate_response(query, analysis, map_data)
            
            return {
                'response': response,
                'map_data': map_data
            }
        
        except Exception as e:
            raise Exception(f"Error processing location query: {str(e)}")
    
    def _process_area_analysis(self, query: str, analysis: Dict,
                              map_style: str, zoom_level: int) -> Dict[str, Any]:
        """Process area analysis query"""
        try:
            # Extract location and parameters
            location = analysis.get('location', '')
            parameters = analysis.get('parameters', {})
            
            # Geocode the location
            geocode_results = self.arcgis_handler.geocode_location(location, max_results=1)
            
            if not geocode_results:
                return {
                    'response': f"I couldn't find the location '{location}'.",
                    'map_data': None
                }
            
            center_point = geocode_results[0]['location']
            
            # Check if buffer/radius is specified
            distance = self._extract_distance(query)
            
            features = []
            
            # Add center point
            center_feature = self.arcgis_handler.create_feature_from_geocode(geocode_results[0])
            features.append(center_feature)
            
            # Add buffer if distance specified
            if distance:
                buffer_feature = self.arcgis_handler.create_buffer(
                    center_point['x'],
                    center_point['y'],
                    distance['value'],
                    distance['unit']
                )
                if buffer_feature:
                    features.append(buffer_feature)
            
            # Create map data
            map_data = {
                'features': features,
                'center': (center_point['x'], center_point['y']),
                'zoom_level': zoom_level,
                'feature_count': len(features),
                'layer_count': 1
            }
            
            # Generate response
            response = self.llm_handler.generate_response(query, analysis, map_data)
            
            return {
                'response': response,
                'map_data': map_data
            }
        
        except Exception as e:
            raise Exception(f"Error processing area analysis: {str(e)}")
    
    def _process_directions(self, query: str, analysis: Dict,
                          map_style: str, zoom_level: int) -> Dict[str, Any]:
        """Process directions query"""
        # For now, return a message that directions are not yet implemented
        return {
            'response': "Directions functionality is coming soon! For now, I can help you find locations and analyze areas.",
            'map_data': None
        }
    
    def _process_general_query(self, query: str, analysis: Dict,
                              map_style: str, zoom_level: int) -> Dict[str, Any]:
        """Process general query"""
        try:
            # Try to extract any location mentioned
            location_info = self.llm_handler.extract_location(query)
            
            if location_info and location_info.get('location_name'):
                # Try to geocode
                geocode_results = self.arcgis_handler.geocode_location(
                    location_info['location_name'],
                    max_results=3
                )
                
                if geocode_results:
                    features = []
                    for result in geocode_results:
                        feature = self.arcgis_handler.create_feature_from_geocode(result)
                        features.append(feature)
                    
                    center = (
                        geocode_results[0]['location']['x'],
                        geocode_results[0]['location']['y']
                    )
                    
                    map_data = {
                        'features': features,
                        'center': center,
                        'zoom_level': zoom_level,
                        'feature_count': len(features),
                        'layer_count': 1
                    }
                    
                    response = self.llm_handler.generate_response(query, analysis, map_data)
                    
                    return {
                        'response': response,
                        'map_data': map_data
                    }
            
            # If no location found, return a helpful message
            response = self.llm_handler.chat(
                f"The user asked: '{query}'. "
                "This seems to be a geographic question, but I need more specific location information. "
                "Please provide a helpful response asking for clarification."
            )
            
            return {
                'response': response,
                'map_data': None
            }
        
        except Exception as e:
            raise Exception(f"Error processing general query: {str(e)}")
    
    def _extract_distance(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract distance and unit from query
        
        Args:
            query: Query string
            
        Returns:
            Dictionary with distance value and unit, or None
        """
        # Patterns for distance extraction
        patterns = [
            r'(\d+\.?\d*)\s*(mile|miles|mi)',
            r'(\d+\.?\d*)\s*(kilometer|kilometers|km)',
            r'(\d+\.?\d*)\s*(meter|meters|m)',
            r'within\s+(\d+\.?\d*)\s*(mile|miles|mi|kilometer|kilometers|km)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                value = float(match.group(1))
                unit_str = match.group(2)
                
                # Normalize unit
                if unit_str in ['mile', 'miles', 'mi']:
                    unit = 'miles'
                elif unit_str in ['kilometer', 'kilometers', 'km']:
                    unit = 'kilometers'
                elif unit_str in ['meter', 'meters', 'm']:
                    unit = 'meters'
                else:
                    unit = 'miles'
                
                return {
                    'value': value,
                    'unit': unit
                }
        
        return None
    
    def _extract_coordinates(self, query: str) -> Optional[Tuple[float, float]]:
        """
        Extract coordinates from query
        
        Args:
            query: Query string
            
        Returns:
            Tuple of (longitude, latitude) or None
        """
        # Pattern for coordinates
        patterns = [
            r'(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)',
            r'lat:\s*(-?\d+\.?\d*)\s+lon:\s*(-?\d+\.?\d*)',
            r'latitude:\s*(-?\d+\.?\d*)\s+longitude:\s*(-?\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                # Determine if it's lat,lon or lon,lat based on values
                val1 = float(match.group(1))
                val2 = float(match.group(2))
                
                # Latitude is typically between -90 and 90
                # Longitude is typically between -180 and 180
                if -90 <= val1 <= 90 and -180 <= val2 <= 180:
                    # Likely lat, lon
                    return (val2, val1)
                elif -180 <= val1 <= 180 and -90 <= val2 <= 90:
                    # Likely lon, lat
                    return (val1, val2)
        
        return None

