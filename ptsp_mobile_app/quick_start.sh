#!/bin/bash
# Quick start script for PTSP Mobile App development

echo "🚀 PTSP Mobile App Quick Start"
echo "================================"

# Check if we're in the right directory
if [ ! -f "pubspec.yaml" ]; then
    echo "❌ Error: Not in Flutter project directory"
    echo "Please run this script from the ptsp_mobile_app directory"
    exit 1
fi

echo "📱 Setting up Flutter dependencies..."
flutter pub get

echo "🔧 Checking Flutter configuration..."
flutter doctor

echo "📋 Running code analysis..."
flutter analyze --no-fatal-infos

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start your FastAPI backend: cd ../.. && python rag_api.py"
echo "2. Update API URL in lib/utils/api_config.dart if needed"
echo "3. Connect Android device or start emulator"
echo "4. Run the app: flutter run"
echo ""
echo "💡 Tips:"
echo "- For Android emulator: use http://10.0.2.2:8000"
echo "- For physical device: use http://YOUR_COMPUTER_IP:8000"
echo "- Check your computer's IP with: ipconfig (Windows) or ifconfig (Mac/Linux)"
