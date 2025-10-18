# ArcGIS AI Assistant

A full-stack AI assistant web application that integrates Large Language Models (LLMs) with ArcGIS mapping capabilities. Users can ask natural language questions and receive intelligent responses visualized on an interactive map.

## Technologies Used

- **Streamlit** - Web application framework for building the user interface
- **LangChain** - LLM orchestration framework for connecting AI with external tools
- **Ollama** - Framework for running large language models locally
- **Qwen2** - Open-source LLM for natural language understanding
- **Model Context Protocol (MCP)** - Standard for connecting AI agents with external data sources
- **ArcGIS Python API** - Geospatial operations and map rendering

## Features

- 🗺️ **Interactive Map Display** - View results on an ArcGIS-powered map
- 💬 **Natural Language Interface** - Ask questions in plain English
- 🤖 **AI-Powered Responses** - Intelligent query processing using LLMs
- 📍 **Geocoding** - Convert addresses to coordinates automatically
- 🔍 **Feature Search** - Find locations, landmarks, and geographic features
- 📊 **Spatial Analysis** - Buffer zones, area analysis, and more
- 🎨 **Multiple Map Styles** - Choose from various base map styles
- 📱 **Responsive Design** - Works on desktop and mobile devices

## Prerequisites

### Windows Environment Setup

1. **Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Ollama**
   - Download from [ollama.ai](https://ollama.ai/)
   - Install and run Ollama
   - Pull the Qwen2 model:
     ```cmd
     ollama pull qwen2:latest
     ```

3. **ArcGIS Account** (Optional but recommended)
   - Sign up at [developers.arcgis.com](https://developers.arcgis.com/)
   - Get an API key from your dashboard
   - Note: The application can run with anonymous access but with limited functionality

## Installation

### Step 1: Clone or Download the Project

```cmd
cd C:\Users\YourUsername\Documents
git clone <repository-url>
cd arcgis-ai-assistant
```

Or download and extract the ZIP file.

### Step 2: Create Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```cmd
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```cmd
   copy .env.example .env
   ```

2. Edit `.env` file with your configuration:
   ```
   ARCGIS_API_KEY=your_api_key_here
   ARCGIS_USERNAME=your_username
   ARCGIS_PASSWORD=your_password
   
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2:latest
   
   APP_HOST=localhost
   APP_PORT=8501
   DEBUG=True
   ```

## Running the Application

### Step 1: Start Ollama

Make sure Ollama is running in the background. If not, start it:

```cmd
ollama serve
```

### Step 2: Verify Qwen2 Model

```cmd
ollama list
```

If Qwen2 is not listed, pull it:

```cmd
ollama pull qwen2:latest
```

### Step 3: Start the Application

```cmd
streamlit run app.py
```

The application will open automatically in your default web browser at `http://localhost:8501`.

## Usage

### Basic Usage

1. **Enter a Question**: Type your question in the text area
2. **Submit**: Click the "Submit" button
3. **View Results**: See the AI response and map visualization

### Example Queries

- "Show me the location of New York City"
- "Find all major cities in California"
- "Where is the Eiffel Tower?"
- "Show me hospitals within 10 miles of Los Angeles"
- "What is the capital of France?"

### Map Controls

- **Zoom**: Use mouse wheel or +/- buttons
- **Pan**: Click and drag the map
- **Markers**: Click on markers to see details
- **Reset**: Click "Reset Map" to clear all features

### Configuration Options

- **LLM Settings**: Change the Ollama URL and model
- **Map Style**: Choose from different base map styles
- **Zoom Level**: Adjust default zoom level

## Project Structure

```
arcgis-ai-assistant/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
├── src/                       # Source code modules
│   ├── __init__.py
│   ├── llm_handler.py        # LLM and LangChain integration
│   ├── arcgis_handler.py     # ArcGIS operations
│   └── query_processor.py    # Query processing logic
├── static/                    # Static files (CSS, JS, images)
├── templates/                 # HTML templates
└── data/                      # Data files and cache
```

## Architecture

### Component Overview

1. **Streamlit Frontend**
   - User interface with chat and map components
   - Configuration sidebar
   - Real-time updates

2. **LLM Handler**
   - Connects to Ollama for LLM inference
   - Uses LangChain for prompt engineering
   - Analyzes user queries and generates responses

3. **ArcGIS Handler**
   - Geocoding and reverse geocoding
   - Feature search and spatial queries
   - Map widget creation

4. **Query Processor**
   - Coordinates between LLM and ArcGIS
   - Intent detection and routing
   - Result aggregation

### Data Flow

```
User Query → LLM Analysis → Intent Detection → ArcGIS Operations → Map Rendering → Response Generation
```

## Troubleshooting

### Ollama Connection Error

**Problem**: "Failed to connect to Ollama"

**Solution**:
1. Make sure Ollama is running: `ollama serve`
2. Check if the URL is correct in `.env`
3. Verify the model is installed: `ollama list`

### ArcGIS Authentication Error

**Problem**: "Could not authenticate with ArcGIS"

**Solution**:
1. Check your API key in `.env`
2. Verify your credentials are correct
3. The app will fall back to anonymous access (limited features)

### Import Errors

**Problem**: "ModuleNotFoundError"

**Solution**:
1. Make sure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.11+)

### Map Not Displaying

**Problem**: Map widget shows blank or error

**Solution**:
1. Check browser console for errors (F12)
2. Try a different map style
3. Clear browser cache
4. Check internet connection (map tiles require internet)

### Slow Response Times

**Problem**: Queries take too long to process

**Solution**:
1. Use a smaller Qwen2 model: `ollama pull qwen2:1.5b`
2. Reduce max_results in geocoding
3. Check system resources (CPU, RAM)

## Windows-Specific Notes

### Path Separators

- Use backslashes `\` or forward slashes `/` in paths
- Example: `C:\Users\YourName\Documents\arcgis-ai-assistant`

### Virtual Environment Activation

```cmd
# Command Prompt
venv\Scripts\activate.bat

# PowerShell
venv\Scripts\Activate.ps1
```

If PowerShell gives an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Firewall

If you have firewall issues:
1. Allow Python through Windows Firewall
2. Allow Ollama through Windows Firewall
3. Check if ports 8501 and 11434 are open

## Advanced Configuration

### Custom LLM Models

To use a different model:

1. Pull the model:
   ```cmd
   ollama pull llama2
   ```

2. Update `.env`:
   ```
   OLLAMA_MODEL=llama2
   ```

### Custom Map Styles

Modify `basemap_urls` in `src/arcgis_handler.py` to add custom base maps.

### Adding New Features

The modular architecture makes it easy to extend:

- Add new intents in `query_processor.py`
- Add new LLM chains in `llm_handler.py`
- Add new ArcGIS operations in `arcgis_handler.py`

## Performance Optimization

### For Better Performance

1. **Use Smaller Models**:
   ```cmd
   ollama pull qwen2:1.5b
   ```

2. **Reduce Context Length**: Modify temperature and max_tokens in `llm_handler.py`

3. **Cache Results**: Implement caching for frequent queries

4. **Limit Geocoding Results**: Reduce `max_results` parameter

## Security Considerations

- Never commit `.env` file to version control
- Keep API keys secure
- Use environment variables for sensitive data
- Consider using ArcGIS OAuth for production
- Implement rate limiting for production deployments

## Known Limitations

- Directions functionality not yet implemented
- Limited offline functionality (requires internet for maps)
- Anonymous ArcGIS access has feature limitations
- Large models require significant RAM

## Future Enhancements

- [ ] Routing and directions
- [ ] Real-time data integration (earthquakes, weather)
- [ ] User authentication and saved queries
- [ ] Export map as image/PDF
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Voice input/output

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the Troubleshooting section
- Review example queries
- Check Ollama documentation: [ollama.ai/docs](https://ollama.ai/docs)
- Check ArcGIS API documentation: [developers.arcgis.com](https://developers.arcgis.com/)

## Acknowledgments

- Streamlit team for the amazing framework
- Ollama team for local LLM capabilities
- Alibaba for the Qwen2 model
- Esri for ArcGIS Python API
- LangChain community

## Version History

- **v1.0.0** (2025-01-18)
  - Initial release
  - Basic query processing
  - Map visualization
  - Geocoding support
  - Multiple map styles

---

**Built with ❤️ using Streamlit, LangChain, Ollama, and ArcGIS**

