import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../data/app_data.dart';
import 'edit_profile_page.dart';
import 'notifications_page.dart';
import 'favorites_page.dart';
import 'login_page.dart';

const _profilePageBackground = Color(0xFFFAF8F6);
const _profileTextPrimary = Color(0xFF2D2620);
const _profileTextSecondary = Color(0xFF8B7E74);
const _profileAccent = Color(0xFFB8957A);
const _profileCardBackground = Color(0xFFFFFFFF);

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final appData = Provider.of<AppData>(context);
    final profile = appData.userProfile;

    return Scaffold(
      backgroundColor: _profilePageBackground,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 110),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Profile',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF2D2620),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Manage your style journey',
                style: const TextStyle(
                  fontSize: 14,
                  color: _profileTextSecondary,
                ),
              ),
              const SizedBox(height: 24),

              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: _profileCardBackground,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x1F000000),
                      blurRadius: 20,
                      offset: Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 72,
                          height: 72,
                          decoration: BoxDecoration(
                            gradient:
                                (appData.profileImagePath == null ||
                                    appData.profileImagePath!.isEmpty)
                                ? const LinearGradient(
                                    colors: [
                                      Color(0xFFB8957A),
                                      Color(0xFFD4B5A0),
                                    ],
                                  )
                                : null,
                            color:
                                (appData.profileImagePath != null &&
                                    appData.profileImagePath!.isNotEmpty)
                                ? Colors.transparent
                                : null,
                            shape: BoxShape.circle,
                            image:
                                (appData.profileImagePath != null &&
                                    appData.profileImagePath!.isNotEmpty)
                                ? DecorationImage(
                                    image: NetworkImage(
                                      appData.profileImagePath!,
                                    ),
                                    fit: BoxFit.cover,
                                  )
                                : null,
                          ),
                          child:
                              (appData.profileImagePath == null ||
                                  appData.profileImagePath!.isEmpty)
                              ? const Icon(
                                  Icons.person,
                                  color: Color(0xFF5B2E91),
                                  size: 34,
                                )
                              : null,
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                profile?.name.isNotEmpty == true
                                    ? profile!.name
                                    : 'Fashion Lover',
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                profile?.aesthetic.isNotEmpty == true
                                    ? profile!.aesthetic
                                    : 'Style Enthusiast',
                                style: const TextStyle(
                                  color: Color(0xFF8B7E74),
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Size: ${profile?.size.isNotEmpty == true ? profile!.size : 'M'}',
                                style: const TextStyle(
                                  color: Color(0xFF8B7E74),
                                  fontSize: 14,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const EditProfilePage(),
                            ),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFF5F0EB),
                          foregroundColor: const Color(0xFF2D2620),
                          elevation: 0,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(18),
                          ),
                        ),
                        child: const Text(
                          'Edit Profile',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              Row(
                children: [
                  Expanded(
                    child: _StatCard(
                      icon: Icons.shopping_bag_outlined,
                      color: const Color(0xFFB8957A),
                      bg: const Color(0xFFE0D5CC),
                      value: '${appData.wardrobeItems.length}',
                      label: 'Total Items',
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _StatCard(
                      icon: Icons.calendar_today_outlined,
                      color: const Color(0xFFB8957A),
                      bg: const Color(0xFFE0D5CC),
                      value: '${appData.plannedOutfits.length}',
                      label: 'Outfits Planned',
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _StatCard(
                      icon: Icons.favorite_border,
                      color: const Color(0xFFB8957A),
                      bg: const Color(0xFFE0D5CC),
                      label: 'Saved Outfits',
                      value: '${appData.favoritesPosts.length}',
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              _MenuCard(
                icon: Icons.settings_outlined,
                title: 'Edit Profile',
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const EditProfilePage()),
                  );
                },
              ),
              const SizedBox(height: 14),
              _MenuCard(
                icon: Icons.notifications_none,
                title: 'Notifications',
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const NotificationsPage(),
                    ),
                  );
                },
              ),
              const SizedBox(height: 14),
              _MenuCard(
                icon: Icons.favorite_border,
                title: 'Global Saves',
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const FavoritesPage()),
                  );
                },
              ),
              const SizedBox(height: 14),
              _MenuCard(
                icon: Icons.help_outline,
                title: 'Terms and Conditions',
                onTap: () {
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      return AlertDialog(
                        backgroundColor: _profileCardBackground,
                        title: const Text(
                          'Terms and Conditions',
                          style: TextStyle(color: _profileTextPrimary),
                        ),
                        content: SingleChildScrollView(
                          child: Text(
                            'Welcome to Appearix! By using our app, you agree to the following terms and conditions:\\n\\n'
                            '1. You must be at least 13 years old to use this app.\\n'
                            '2. All content you upload remains your property, but you grant us a license to display it.\\n'
                            '3. You agree not to upload harmful, offensive, or copyrighted content without permission.\\n'
                            '4. We respect your privacy and do not share your personal information with third parties.\\n'
                            '5. We reserve the right to modify these terms at any time.\\n'
                            '6. Continued use of the app constitutes acceptance of updated terms.\\n\\n'
                            'If you have any questions, please contact our support team.',
                            style: const TextStyle(color: _profileTextPrimary),
                          ),
                        ),
                        actions: [
                          TextButton(
                            onPressed: () {
                              Navigator.of(context).pop();
                            },
                            child: const Text(
                              'Close',
                              style: TextStyle(color: _profileAccent),
                            ),
                          ),
                        ],
                      );
                    },
                  );
                },
              ),
              const SizedBox(height: 14),
              _MenuCard(
                icon: Icons.logout,
                title: 'Logout',
                onTap: () {
                  final appData = Provider.of<AppData>(context, listen: false);
                  appData.logout();
                  Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(builder: (context) => const LoginPage()),
                    (route) => false,
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final Color bg;
  final String value;
  final String label;

  const _StatCard({
    required this.icon,
    required this.color,
    required this.bg,
    required this.value,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE8DDD3), width: 1),
      ),
      child: Column(
        children: [
          Container(
            decoration: BoxDecoration(color: bg, shape: BoxShape.circle),
            padding: const EdgeInsets.all(10),
            child: Icon(icon, color: color),
          ),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Color(0xFF2D2620),
            ),
          ),
          Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Color(0xFF8B7E74), fontSize: 12),
          ),
        ],
      ),
    );
  } 
}

class _MenuCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback? onTap;

  const _MenuCard({required this.icon, required this.title, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFFE8DDD3), width: 1),
        ),
        child: Row(
          children: [
            Icon(icon, color: const Color(0xFFB8957A)),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(color: Color(0xFF2D2620)),
              ),
            ),
            Icon(Icons.arrow_forward, color: const Color(0xFF8B7E74)),
          ],
        ),
      ),
    );
  }
}
