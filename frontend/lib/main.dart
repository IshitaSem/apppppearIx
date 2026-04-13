import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'data/app_data.dart';
import 'pages/login_page.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => AppData(),
      child: const AppearixApp(),
    ),
  );
}

class AppearixApp extends StatelessWidget {
  const AppearixApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Appearix',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFFAF8F6),
        cardColor: Colors.white,
        colorScheme: const ColorScheme(
          brightness: Brightness.light,
          primary: Color(0xFFB8957A),
          onPrimary: Color(0xFF2D2620),
          secondary: Color(0xFFD4B5A0),
          onSecondary: Color(0xFF2D2620),
          error: Color(0xFFEF4444),
          onError: Colors.white,
          surface: Colors.white,
          onSurface: Color(0xFF2D2620),
        ),
      ),
      home: LoginPage(),
    );
  }
}