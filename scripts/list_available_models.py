import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def check_available_models():
    """List all available Gemini models in your account"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set in .env")
        sys.exit(1)

    # Configure Gemini client
    genai.configure(api_key=api_key)

    print("Available Gemini Models:")
    print("-" * 60)
    try:
        for model in genai.list_models():
            if hasattr(model, "supported_generation_methods") and \
               "generateContent" in model.supported_generation_methods:
                print(f"✓ {model.name.replace('models/', '')}")
                print(f"  Display Name: {model.display_name}")
                print(f"  Description: {model.description[:100]}...")
                print()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTry these common models:")
        print("- gemini-pro")
        print("- gemini-1.5-pro")
        print("- gemini-1.5-flash")
        print("- gemini-2.0-flash")

if __name__ == "__main__":
    check_available_models()
