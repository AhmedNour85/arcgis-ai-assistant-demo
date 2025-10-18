"""
ArcGIS AI Assistant - Main Application
A web application that integrates AI with ArcGIS mapping capabilities
"""

import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path

# Import custom modules
from src.llm_handler import LLMHandler
from src.arcgis_handler import ArcGISHandler
from src.query_processor import QueryProcessor

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ArcGIS AI Assistant",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0079c1;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 1.1rem;
    }
    .map-container {
        border: 2px solid #0079c1;
        border-radius: 10px;
        padding: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'map_data' not in st.session_state:
        st.session_state.map_data = None
    if 'llm_handler' not in st.session_state:
        st.session_state.llm_handler = None
    if 'arcgis_handler' not in st.session_state:
        st.session_state.arcgis_handler = None
    if 'query_processor' not in st.session_state:
        st.session_state.query_processor = None


def initialize_handlers():
    """Initialize all handlers"""
    try:
        if st.session_state.llm_handler is None:
            with st.spinner("Initializing LLM Handler..."):
                st.session_state.llm_handler = LLMHandler(
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                    model=os.getenv("OLLAMA_MODEL", "qwen2:latest")
                )
        
        if st.session_state.arcgis_handler is None:
            with st.spinner("Initializing ArcGIS Handler..."):
                st.session_state.arcgis_handler = ArcGISHandler(
                    api_key=os.getenv("ARCGIS_API_KEY"),
                    username=os.getenv("ARCGIS_USERNAME"),
                    password=os.getenv("ARCGIS_PASSWORD")
                )
        
        if st.session_state.query_processor is None:
            st.session_state.query_processor = QueryProcessor(
                llm_handler=st.session_state.llm_handler,
                arcgis_handler=st.session_state.arcgis_handler
            )
        
        return True
    except Exception as e:
        st.error(f"Error initializing handlers: {str(e)}")
        return False


def render_sidebar():
    """Render sidebar with configuration options"""
    with st.sidebar:
        st.image("https://www.esri.com/content/dam/esrisites/en-us/common/icons/product-logos/ArcGIS-Pro.png", width=100)
        st.title("Configuration")
        
        st.subheader("🤖 LLM Settings")
        ollama_url = st.text_input(
            "Ollama Base URL",
            value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            help="URL where Ollama is running"
        )
        
        model_name = st.selectbox(
            "Model",
            ["qwen2:latest", "qwen2:7b", "qwen2:1.5b", "llama2", "mistral"],
            index=0,
            help="Select the LLM model to use"
        )
        
        st.subheader("🗺️ Map Settings")
        map_style = st.selectbox(
            "Map Style",
            ["streets", "satellite", "hybrid", "topo", "gray", "dark-gray", "oceans"],
            index=0,
            help="Select the base map style"
        )
        
        zoom_level = st.slider(
            "Default Zoom Level",
            min_value=1,
            max_value=18,
            value=10,
            help="Default zoom level for the map"
        )
        
        st.subheader("ℹ️ About")
        st.info(
            "This application uses AI to process your questions and "
            "visualize the results on an interactive ArcGIS map."
        )
        
        st.subheader("📊 Statistics")
        if st.session_state.messages:
            st.metric("Total Queries", len([m for m in st.session_state.messages if m['role'] == 'user']))
        else:
            st.metric("Total Queries", 0)
        
        return {
            'ollama_url': ollama_url,
            'model_name': model_name,
            'map_style': map_style,
            'zoom_level': zoom_level
        }


def render_chat_history():
    """Render chat history"""
    st.subheader("💬 Conversation History")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "map_data" in message and message["map_data"]:
                st.info(f"📍 Map updated with {message['map_data'].get('feature_count', 0)} features")


def process_query(user_query: str, config: dict):
    """Process user query and update map"""
    try:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": user_query
        })
        
        # Process query
        with st.spinner("Processing your query..."):
            result = st.session_state.query_processor.process_query(
                query=user_query,
                map_style=config['map_style'],
                zoom_level=config['zoom_level']
            )
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": result['response'],
            "map_data": result.get('map_data')
        })
        
        # Update map data
        if result.get('map_data'):
            st.session_state.map_data = result['map_data']
        
        return result
    
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        st.error(error_msg)
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg
        })
        return None


def render_map(config: dict):
    """Render the ArcGIS map"""
    st.subheader("🗺️ Interactive Map")
    
    try:
        if st.session_state.arcgis_handler:
            map_widget = st.session_state.arcgis_handler.create_map_widget(
                map_style=config['map_style'],
                zoom_level=config['zoom_level'],
                map_data=st.session_state.map_data
            )
            
            # Display map using HTML component
            st.components.v1.html(map_widget, height=600, scrolling=True)
        else:
            st.warning("ArcGIS handler not initialized. Please check your configuration.")
    
    except Exception as e:
        st.error(f"Error rendering map: {str(e)}")


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Render header
    st.markdown('<div class="main-header">🗺️ ArcGIS AI Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Ask questions and visualize answers on an interactive map</div>',
        unsafe_allow_html=True
    )
    
    # Render sidebar and get configuration
    config = render_sidebar()
    
    # Initialize handlers
    if not initialize_handlers():
        st.error("Failed to initialize application. Please check your configuration.")
        st.stop()
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Chat interface
        render_chat_history()
        
        # Query input
        st.subheader("🔍 Ask a Question")
        user_query = st.text_area(
            "Enter your question:",
            placeholder="e.g., Show me all earthquakes in California in the last month",
            height=100,
            key="query_input"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            submit_button = st.button("🚀 Submit", type="primary", use_container_width=True)
        
        with col_btn2:
            clear_button = st.button("🗑️ Clear History", use_container_width=True)
        
        with col_btn3:
            reset_map = st.button("🔄 Reset Map", use_container_width=True)
        
        # Handle button clicks
        if submit_button and user_query:
            result = process_query(user_query, config)
            st.rerun()
        
        if clear_button:
            st.session_state.messages = []
            st.rerun()
        
        if reset_map:
            st.session_state.map_data = None
            st.rerun()
        
        # Example queries
        st.subheader("💡 Example Queries")
        examples = [
            "Show me the location of New York City",
            "Find all major cities in California",
            "Display earthquake data for the last week",
            "Show me national parks in the United States",
            "Find hospitals within 10 miles of Los Angeles"
        ]
        
        for example in examples:
            if st.button(f"📌 {example}", key=f"example_{example}"):
                st.session_state.query_input = example
                result = process_query(example, config)
                st.rerun()
    
    with col2:
        # Map display
        render_map(config)
        
        # Map information
        if st.session_state.map_data:
            st.subheader("📊 Map Information")
            map_info = st.session_state.map_data
            
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                st.metric("Features", map_info.get('feature_count', 0))
            
            with info_col2:
                st.metric("Layers", map_info.get('layer_count', 1))
            
            with info_col3:
                st.metric("Zoom Level", map_info.get('zoom_level', config['zoom_level']))


if __name__ == "__main__":
    main()

