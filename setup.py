"""
Setup script for BespokeToMe Voice Assistant
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False
    return True

def main():
    print("🚀 BespokeToMe Voice Assistant Setup")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("❌ Python 3.9+ is required")
        print(f"   Current version: {python_version.major}.{python_version.minor}")
        sys.exit(1)
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    
    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    ):
        return
    
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    ):
        return
    
    # Check for PyAudio
    try:
        import pyaudio
        print("✅ PyAudio is installed")
    except ImportError:
        print("⚠️ PyAudio installation may have failed")
        print("   On Windows, you may need to install PyAudio manually:")
        print("   Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        print("   Then: pip install PyAudio-0.2.11-cpXX-cpXX-win_amd64.whl")
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Install Ollama from https://ollama.ai")
    print("2. Pull a model: ollama pull llama3.2:3b-instruct")
    print("3. (Optional) Set up SearxNG for web search")
    print("4. Configure settings in Alexa/config.py")
    print("5. Run: python Alexa/launch.py")
    print("\nFor more info, see README.md")

if __name__ == "__main__":
    main()


