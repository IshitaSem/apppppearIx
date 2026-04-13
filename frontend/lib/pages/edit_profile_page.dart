import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../data/app_data.dart';

class EditProfilePage extends StatefulWidget {
  const EditProfilePage({super.key});

  @override
  State<EditProfilePage> createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {
  late TextEditingController nameController;
  late TextEditingController emailController;
  late TextEditingController customAestheticController;

  String gender = 'Other';
  String size = 'M';
  String aesthetic = 'Minimalist';
  String customAesthetic = '';

  @override
  void initState() {
    super.initState();
    final appData = Provider.of<AppData>(context, listen: false);
    final profile = appData.userProfile;

    nameController = TextEditingController(text: profile?.name ?? '');
    emailController = TextEditingController(text: profile?.email ?? '');
    customAestheticController = TextEditingController(text: customAesthetic);

    gender = (profile?.gender.isNotEmpty ?? false) ? profile!.gender : 'Other';
    size = (profile?.size.isNotEmpty ?? false) ? profile!.size : 'M';
    aesthetic = (profile?.aesthetic.isNotEmpty ?? false)
        ? profile!.aesthetic
        : 'Minimalist';

    // Check if aesthetic is custom
    final predefinedAesthetics = [
      'Minimalist',
      'Streetwear',
      'Coquette',
      'Y2K',
      'Classic',
      'Custom',
    ];
    if (!predefinedAesthetics.contains(aesthetic)) {
      customAesthetic = aesthetic;
      aesthetic = 'Custom';
    }

    customAestheticController = TextEditingController(text: customAesthetic);
  }

  Future<void> _pickProfileImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);

    if (picked != null && mounted) {
      Provider.of<AppData>(
        context,
        listen: false,
      ).updateProfileImage(picked.path);
    }
  }

  void _saveProfile() {
    String finalAesthetic = aesthetic;
    if (aesthetic == 'Custom') {
      finalAesthetic = customAesthetic.trim().isNotEmpty
          ? customAesthetic.trim()
          : 'Minimalist';
    }

    Provider.of<AppData>(context, listen: false).updateUserProfile(
      name: nameController.text.trim(),
      email: emailController.text.trim(),
      gender: gender,
      size: size,
      aesthetic: finalAesthetic,
    );

    Navigator.pop(context);
  }

  @override
  void dispose() {
    nameController.dispose();
    emailController.dispose();
    customAestheticController.dispose();
    super.dispose();
  }

  Widget _field(TextEditingController controller, String hint) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(
        hintText: hint,
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: BorderSide.none,
        ),
      ),
    );
  }

  Widget _dropdown({
    required String label,
    required String value,
    required List<String> items,
    required void Function(String?) onChanged,
  }) {
    return DropdownButtonFormField<String>(
      initialValue: value,
      onChanged: onChanged,
      items: items
          .map((item) => DropdownMenuItem(value: item, child: Text(item)))
          .toList(),
      decoration: InputDecoration(
        labelText: label,
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: BorderSide.none,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appData = Provider.of<AppData>(context);

    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F6),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAF8F6),
        scrolledUnderElevation: 0,
        title: const Text(
          'Edit Profile',
          style: TextStyle(color: Color(0xFF2D2620)),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 30),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 45,
                    backgroundColor: const Color(0xFFE8DDD3),
                    backgroundImage:
                        (appData.profileImagePath != null &&
                            appData.profileImagePath!.isNotEmpty)
                        ? NetworkImage(appData.profileImagePath!)
                        : null,
                    child:
                        (appData.profileImagePath == null ||
                            appData.profileImagePath!.isEmpty)
                        ? const Icon(
                            Icons.person,
                            size: 40,
                            color: Color(0xFF5B2E91),
                          )
                        : null,
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton(
                    onPressed: _pickProfileImage,
                    child: const Text('Choose Profile Picture'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            _field(nameController, 'Full Name'),
            const SizedBox(height: 16),
            _field(emailController, 'Email'),
            const SizedBox(height: 16),
            _dropdown(
              label: 'Gender',
              value: gender,
              items: const ['Male', 'Female', 'Other'],
              onChanged: (v) => setState(() => gender = v!),
            ),
            const SizedBox(height: 16),
            _dropdown(
              label: 'Size',
              value: size,
              items: const ['XS', 'S', 'M', 'L', 'XL'],
              onChanged: (v) => setState(() => size = v!),
            ),
            const SizedBox(height: 16),
            _dropdown(
              label: 'Aesthetic',
              value: aesthetic,
              items: const [
                'Custom',
                'Minimalist',
                'Streetwear',
                'Coquette',
                'Y2K',
                'Classic',
              ],
              onChanged: (v) => setState(() => aesthetic = v!),
            ),
            if (aesthetic == 'Custom') ...[
              const SizedBox(height: 16),
              TextField(
                controller: customAestheticController,
                onChanged: (value) => customAesthetic = value,
                decoration: InputDecoration(
                  hintText: 'Enter your custom aesthetic',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(18),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ],
            const SizedBox(height: 28),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _saveProfile,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFB8957A),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('SAVE CHANGES'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
