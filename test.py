import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from fastapi import FastAPI
        from agent.agent import GraphBuilder
        from utils.doc import save_document
        from utils.config_loader import ConfigLoader
        from utils.model_loader import ModelLoader
        print("✅ All imports successful")
        assert True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        assert False

def test_config_loading():
    """Test configuration loading"""
    try:
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()
        print("✅ Configuration loading successful")
        assert True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        assert False

def test_health_check():
    """Test that the application can start without errors"""
    try:
        # This is a basic test to ensure the app can be imported
        import main
        print("✅ Application can be imported successfully")
        assert True
    except Exception as e:
        print(f"❌ Application import failed: {e}")
        assert False

if __name__ == "__main__":
    print("Running tests...")
    test_imports()
    test_config_loading()
    test_health_check()
    print("All tests completed!")
