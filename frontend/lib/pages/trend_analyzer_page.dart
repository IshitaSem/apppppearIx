import 'package:flutter/material.dart';

class TrendAnalyzerPage extends StatelessWidget {
  const TrendAnalyzerPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F6),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Color(0xFF2D2620)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Trend Analyzer',
          style: TextStyle(
            color: Color(0xFF2D2620),
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
      ),
      body: const SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.trending_up, size: 64, color: Color(0xFF8B7E74)),
              SizedBox(height: 24),
              Text(
                'Trend Analyzer',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF2D2620),
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Coming soon!',
                style: TextStyle(fontSize: 16, color: Color(0xFF8B7E74)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
