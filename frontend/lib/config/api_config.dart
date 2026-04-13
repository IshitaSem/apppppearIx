import 'package:flutter/foundation.dart';

String getBaseUrl() {
  if (kIsWeb) {
    return 'http://127.0.0.1:8000';
  }
  // Android emulator
  if (defaultTargetPlatform == TargetPlatform.android) {
    return 'http://10.0.2.2:8000';
  }
  // iOS/Windows/Linux/Mac: localhost
  return 'http://127.0.0.1:8000';
}
