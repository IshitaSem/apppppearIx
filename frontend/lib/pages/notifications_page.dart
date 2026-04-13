import 'package:flutter/material.dart';

class NotificationsPage extends StatelessWidget {
  const NotificationsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F6),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAF8F6),
        scrolledUnderElevation: 0,
        title: const Text(
          'Notifications',
          style: TextStyle(color: Color(0xFF2D2620)),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF2D2620)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Your Notifications',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF2D2620),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Stay updated with your fashion journey',
                style: TextStyle(fontSize: 14, color: Color(0xFF8B7E74)),
              ),
              const SizedBox(height: 24),

              // Sample notifications - in a real app, these would come from a data source
              _NotificationCard(
                icon: Icons.favorite,
                iconColor: const Color(0xFFDB2777),
                title: 'New Trend Alert!',
                message:
                    'Check out the latest minimalist fashion trends that match your style.',
                time: '2 hours ago',
              ),
              const SizedBox(height: 16),

              _NotificationCard(
                icon: Icons.palette,
                iconColor: const Color(0xFF9333EA),
                title: 'Color Match Found',
                message:
                    'We found perfect color combinations for your wardrobe items.',
                time: '1 day ago',
              ),
              const SizedBox(height: 16),

              _NotificationCard(
                icon: Icons.star,
                iconColor: const Color(0xFFD97706),
                title: 'Style Achievement',
                message:
                    'Congratulations! You\'ve completed your wardrobe organization.',
                time: '3 days ago',
              ),
              const SizedBox(height: 16),

              _NotificationCard(
                icon: Icons.camera_alt,
                iconColor: const Color(0xFF2563EB),
                title: 'Virtual Try-On Ready',
                message:
                    'Your virtual try-on feature is now available for all outfits.',
                time: '1 week ago',
              ),

              const SizedBox(height: 32),
              const Center(
                child: Text(
                  'No more notifications',
                  style: TextStyle(color: Color(0xFF8B7E74), fontSize: 16),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NotificationCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String message;
  final String time;

  const _NotificationCard({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.message,
    required this.time,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0F000000),
            blurRadius: 10,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0x1A000000), // 10% black opacity
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2D2620),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  message,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF8B7E74),
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  time,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF8B7E74),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
