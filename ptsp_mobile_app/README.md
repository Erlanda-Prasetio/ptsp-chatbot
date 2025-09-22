# PTSP Jawa Tengah Mobile App

Flutter mobile application for PTSP (Pelayanan Terpadu Satu Pintu) Jawa Tengah chatbot, providing information about licensing and investment services.

## Features

- 🤖 **AI-Powered Chatbot**: Get instant answers about PTSP services
- 💾 **Chat History**: All conversations are saved locally
- 🎤 **Speech-to-Text**: Voice input support (Indonesian)
- 📱 **Responsive Design**: Optimized for mobile devices
- 🌙 **Dark Mode**: System theme support
- 📄 **Document Sources**: View source documents for answers
- ⏱️ **Real-time Processing**: Live response indicators

## Setup

### Prerequisites

- Flutter SDK (>=3.9.2)
- Dart SDK
- Android Studio / VS Code with Flutter extensions
- Physical device or emulator for testing

### Backend Configuration

1. Make sure your FastAPI backend is running
2. Update the API endpoint in `lib/utils/api_config.dart`:

```dart
class ApiConfig {
  // For local development on physical device
  static const String baseUrl = 'http://YOUR_IP_ADDRESS:8000';
  
  // For Android emulator
  static const String baseUrl = 'http://10.0.2.2:8000';
  
  // For production
  static const String baseUrl = 'https://your-api-domain.com';
}
```

### Installation

1. Install dependencies:
```bash
flutter pub get
```

2. Run the app:
```bash
# Debug mode
flutter run

# Release mode
flutter run --release
```

## API Integration

The mobile app communicates with the FastAPI backend using these endpoints:

- `POST /api/chat` - Send messages and receive AI responses
- `GET /health` - Health check
- `GET /` - Connection test

## Building for Production

### Android APK

```bash
flutter build apk --release
```

### Android App Bundle (for Play Store)

```bash
flutter build appbundle --release
```

## Configuration

Update `lib/utils/api_config.dart` with your backend URL:

- **Local Development**: `http://localhost:8001`
- **Android Emulator**: `http://10.0.2.2:8001`
- **Physical Device**: `http://YOUR_COMPUTER_IP:8001`
- **Production**: `https://your-api-domain.com`

## Troubleshooting

### Connection Issues

1. **Make sure FastAPI server is running**:
   ```bash
   cd ../../  # Go back to ptspRag directory
   python rag_api.py
   ```
   Server should show: `Uvicorn running on http://0.0.0.0:8001`

2. **Test server connection**:
   ```bash
   curl http://localhost:8001/health
   ```

3. **Check correct port**: The server runs on port **8001**, not 8000

4. **For physical device**: Update `baseUrl` with your computer's IP:
   ```bash
   ipconfig  # Windows
   ifconfig  # Mac/Linux
   ```

### Common Errors

- **"Failed to fetch"**: Server not running or wrong port
- **"Network error"**: Check IP address configuration
- **"Connection refused"**: Firewall blocking port 8001
