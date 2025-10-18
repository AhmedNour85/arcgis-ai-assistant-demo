"""
LLM Handler Module
Handles interaction with Ollama and LangChain for processing queries
"""

import os
import json
from typing import Dict, List, Optional, Any
import requests
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pydantic import Field


class OllamaLLM(LLM):
    """Custom Ollama LLM wrapper for LangChain"""
    
    base_url: str = Field(default="http://localhost:11434")
    model: str = Field(default="qwen2:latest")
    temperature: float = Field(default=0.7)
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Ollama API"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature
                }
            }
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Ollama API: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error in Ollama LLM: {str(e)}")


class LLMHandler:
    """Handler for LLM operations using Ollama and LangChain"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2:latest"):
        """
        Initialize LLM Handler
        
        Args:
            base_url: Base URL for Ollama API
            model: Model name to use
        """
        self.base_url = base_url
        self.model = model
        self.llm = None
        self.chains = {}
        
        self._initialize_llm()
        self._initialize_chains()
    
    def _initialize_llm(self):
        """Initialize the Ollama LLM"""
        try:
            self.llm = OllamaLLM(
                base_url=self.base_url,
                model=self.model,
                temperature=0.7
            )
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            raise Exception(f"Failed to initialize LLM: {str(e)}")
    
    def _test_connection(self):
        """Test connection to Ollama"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            
            if not any(self.model in name for name in model_names):
                print(f"Warning: Model '{self.model}' not found in available models: {model_names}")
        
        except Exception as e:
            raise Exception(f"Failed to connect to Ollama at {self.base_url}: {str(e)}")
    
    def _initialize_chains(self):
        """Initialize LangChain chains for different tasks"""
        
        # Query Analysis Chain
        query_analysis_template = """You are an AI assistant specialized in analyzing geographic and spatial queries.

User Query: {query}

Analyze this query and extract the following information in JSON format:
1. intent: The main intent (e.g., "search_location", "find_features", "analyze_area", "get_directions")
2. location: Primary location mentioned (city, state, country, coordinates)
3. feature_type: Type of geographic feature (e.g., "city", "park", "hospital", "earthquake")
4. spatial_operation: Any spatial operation (e.g., "within", "near", "buffer", "intersect")
5. parameters: Additional parameters (e.g., distance, time range, filters)
6. keywords: Important keywords from the query

Return ONLY valid JSON without any additional text or explanation.

JSON Response:"""
        
        query_analysis_prompt = PromptTemplate(
            input_variables=["query"],
            template=query_analysis_template
        )
        
        self.chains['query_analysis'] = LLMChain(
            llm=self.llm,
            prompt=query_analysis_prompt
        )
        
        # Response Generation Chain
        response_generation_template = """You are an AI assistant helping users understand geographic information.

User Query: {query}
Analysis Results: {analysis}
Map Data: {map_data}

Generate a clear, concise, and informative response that:
1. Directly answers the user's question
2. Describes what is shown on the map
3. Provides relevant context or additional information
4. Is written in a friendly, conversational tone

Response:"""
        
        response_generation_prompt = PromptTemplate(
            input_variables=["query", "analysis", "map_data"],
            template=response_generation_template
        )
        
        self.chains['response_generation'] = LLMChain(
            llm=self.llm,
            prompt=response_generation_prompt
        )
        
        # Geocoding Chain
        geocoding_template = """You are a geocoding expert. Extract location information from the query.

Query: {query}

Extract and return in JSON format:
1. location_name: The main location name
2. location_type: Type (city, state, country, address, coordinates)
3. search_terms: List of search terms for geocoding
4. coordinates: If coordinates are mentioned, extract them (format: [longitude, latitude])

Return ONLY valid JSON.

JSON Response:"""
        
        geocoding_prompt = PromptTemplate(
            input_variables=["query"],
            template=geocoding_template
        )
        
        self.chains['geocoding'] = LLMChain(
            llm=self.llm,
            prompt=geocoding_prompt
        )
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze user query to extract intent and parameters
        
        Args:
            query: User query string
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            result = self.chains['query_analysis'].run(query=query)
            
            # Parse JSON response
            # Remove any markdown code blocks if present
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            
            analysis = json.loads(result)
            return analysis
        
        except json.JSONDecodeError as e:
            # Fallback to basic analysis
            return {
                "intent": "search_location",
                "location": query,
                "feature_type": "general",
                "spatial_operation": None,
                "parameters": {},
                "keywords": query.split()
            }
        except Exception as e:
            raise Exception(f"Error analyzing query: {str(e)}")
    
    def generate_response(self, query: str, analysis: Dict, map_data: Dict) -> str:
        """
        Generate natural language response
        
        Args:
            query: Original user query
            analysis: Query analysis results
            map_data: Map data and results
            
        Returns:
            Generated response string
        """
        try:
            response = self.chains['response_generation'].run(
                query=query,
                analysis=json.dumps(analysis, indent=2),
                map_data=json.dumps(map_data, indent=2)
            )
            
            return response.strip()
        
        except Exception as e:
            return f"I found some results for your query. Please check the map for details."
    
    def extract_location(self, query: str) -> Dict[str, Any]:
        """
        Extract location information from query
        
        Args:
            query: User query string
            
        Returns:
            Dictionary containing location information
        """
        try:
            result = self.chains['geocoding'].run(query=query)
            
            # Parse JSON response
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            
            location_info = json.loads(result)
            return location_info
        
        except json.JSONDecodeError:
            # Fallback to simple extraction
            return {
                "location_name": query,
                "location_type": "general",
                "search_terms": [query],
                "coordinates": None
            }
        except Exception as e:
            raise Exception(f"Error extracting location: {str(e)}")
    
    def chat(self, prompt: str) -> str:
        """
        Simple chat interface
        
        Args:
            prompt: User prompt
            
        Returns:
            LLM response
        """
        try:
            response = self.llm(prompt)
            return response
        except Exception as e:
            raise Exception(f"Error in chat: {str(e)}")
    
    def is_available(self) -> bool:
        """
        Check if LLM is available
        
        Returns:
            True if available, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

