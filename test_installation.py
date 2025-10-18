"""
Test script to verify installation and configuration
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_python_version():
    """Test Python version"""
    print_header("Testing Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 11:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.11 or higher is required")
        return False

def test_imports():
    """Test required imports"""
    print_header("Testing Required Packages")
    
    packages = [
        ("streamlit", "Streamlit"),
        ("langchain", "LangChain"),
        ("arcgis", "ArcGIS Python API"),
        ("requests", "Requests"),
        ("dotenv", "Python-dotenv"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
    ]
    
    all_passed = True
    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name} - NOT INSTALLED")
            all_passed = False
    
    return all_passed

def test_ollama_connection():
    """Test Ollama connection"""
    print_header("Testing Ollama Connection")
    
    try:
        import requests
        
        url = "http://localhost:11434/api/tags"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✓ Ollama is running")
            
            data = response.json()
            models = data.get("models", [])
            
            if models:
                print(f"\nAvailable models:")
                for model in models:
                    print(f"  - {model.get('name')}")
                
                # Check for Qwen2
                qwen_models = [m for m in models if 'qwen' in m.get('name', '').lower()]
                if qwen_models:
                    print("\n✓ Qwen2 model found")
                    return True
                else:
                    print("\n✗ Qwen2 model not found")
                    print("  Run: ollama pull qwen2:latest")
                    return False
            else:
                print("✗ No models installed")
                print("  Run: ollama pull qwen2:latest")
                return False
        else:
            print(f"✗ Ollama returned status code: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama")
        print("  Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_env_file():
    """Test .env file"""
    print_header("Testing Environment Configuration")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file exists")
        
        # Check if it has content
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "ARCGIS_API_KEY" in content:
            print("✓ .env file is configured")
            
            # Check if values are set
            if "your_arcgis_api_key_here" in content:
                print("⚠ Warning: ArcGIS API key not set (using default)")
                print("  Edit .env file to add your API key")
            
            return True
        else:
            print("✗ .env file is not properly configured")
            return False
    else:
        print("✗ .env file not found")
        print("  Copy .env.example to .env and configure it")
        return False

def test_project_structure():
    """Test project structure"""
    print_header("Testing Project Structure")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "src/__init__.py",
        "src/llm_handler.py",
        "src/arcgis_handler.py",
        "src/query_processor.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_arcgis_connection():
    """Test ArcGIS connection"""
    print_header("Testing ArcGIS Connection")
    
    try:
        from arcgis.gis import GIS
        
        # Try anonymous connection
        gis = GIS()
        print("✓ ArcGIS connection successful (anonymous)")
        
        # Try a simple geocode
        from arcgis.geocoding import geocode
        results = geocode("New York City", max_locations=1)
        
        if results:
            print("✓ Geocoding service working")
            return True
        else:
            print("⚠ Geocoding returned no results")
            return True
    
    except Exception as e:
        print(f"✗ ArcGIS connection failed: {str(e)}")
        return False

def test_custom_modules():
    """Test custom modules"""
    print_header("Testing Custom Modules")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from src.llm_handler import LLMHandler, OllamaLLM
        print("✓ llm_handler module")
        
        from src.arcgis_handler import ArcGISHandler
        print("✓ arcgis_handler module")
        
        from src.query_processor import QueryProcessor
        print("✓ query_processor module")
        
        return True
    
    except ImportError as e:
        print(f"✗ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "ArcGIS AI Assistant" + " "*24 + "║")
    print("║" + " "*15 + "Installation Test" + " "*26 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Required Packages", test_imports()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Environment Config", test_env_file()))
    results.append(("Custom Modules", test_custom_modules()))
    results.append(("Ollama Connection", test_ollama_connection()))
    results.append(("ArcGIS Connection", test_arcgis_connection()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("\n" + "-"*60)
    print(f"Tests Passed: {passed}/{total}")
    print("-"*60)
    
    if passed == total:
        print("\n✓ All tests passed! You're ready to run the application.")
        print("\nTo start the application, run: streamlit run app.py")
        print("Or use the batch script: run.bat")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nRefer to README.md for troubleshooting help.")
    
    print("\n")

if __name__ == "__main__":
    main()

