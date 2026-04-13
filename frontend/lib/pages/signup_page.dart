import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app_shell.dart';
import '../data/app_data.dart';
import '../services/api_service.dart';

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController nameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController phoneController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController confirmPasswordController =
      TextEditingController();
  bool _showPassword = false;
  bool _showConfirmPassword = false;

  bool _isValidGmail(String value) {
    final email = value.trim().toLowerCase();
    return RegExp(r'^[^@\s]+@gmail\.com$').hasMatch(email);
  }

Future<void> _createAccount() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final email = emailController.text.trim();
    final password = passwordController.text;

    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Creating account...')));

    final appData = Provider.of<AppData>(context, listen: false);
    final result = await ApiService.register(
      email: emailController.text.trim(),
      password: passwordController.text,
    );

    print('SIGNUP RESPONSE: $result');

    if (result != null && result['success']) {
      // Auto-login after signup
      final email = emailController.text.trim();
      final password = passwordController.text;
      final loginResult = await ApiService.login(email: email, password: password);
      
      if (loginResult != null && loginResult['success'] != false) {
        final userId = loginResult['user_id']?.toString() ?? result['data']['user_id']?.toString() ?? '';
        final token = loginResult['access_token']?.toString() ?? '';
        print('[DEBUG] Auto-login after signup - userId: $userId');
        print('[DEBUG] Auth token saved: ${token.isNotEmpty}');
        await appData.setAuth(userId, token);
      }

      final name = nameController.text.trim();
      appData.updateLoginInfo(
        name: name,
        email: email,
        phone: phoneController.text.trim(),
        gender: '',
        size: '',
        aesthetic: '',
        favoriteColors: [],
      );
      if (mounted) {
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (_) => const AppShell()),
          (route) => false,
        );
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Account created and logged in!')));
      }
    } else {
      if (mounted) {
        final errorMsg = result?['message'] ?? 'Signup failed. Try again.';
        print('SIGNUP FAILED: $errorMsg');
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(errorMsg)));
      }
    }
  }

  @override
  void dispose() {
    nameController.dispose();
    emailController.dispose();
    phoneController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  Widget _buildField(
    TextEditingController controller,
    String hint, {
    bool obscure = false,
    bool showText = false,
    VoidCallback? toggleVisibility,
    TextInputType keyboardType = TextInputType.text,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: obscure && !showText,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        hintText: hint,
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 16,
        ),
        suffixIcon: obscure
            ? IconButton(
                icon: Icon(
                  showText ? Icons.visibility : Icons.visibility_off,
                  color: const Color(0xFF8B7E74),
                ),
                onPressed: toggleVisibility,
              )
            : null,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: BorderSide.none,
        ),
      ),
      validator: validator,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F6),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAF8F6),
        elevation: 0,
        scrolledUnderElevation: 0,
        title: const Text(
          'Sign Up',
          style: TextStyle(color: Color(0xFF2D2620)),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 30),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Create your account',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w700,
                color: Color(0xFF2D2620),
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'Enter your basic details to sign up.',
              style: TextStyle(fontSize: 14, color: Color(0xFF8B7E74)),
            ),
            const SizedBox(height: 24),

            Form(
              key: _formKey,
              child: Column(
                children: [
                  _buildField(
                    nameController,
                    'Full Name',
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Enter your full name';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  _buildField(
                    emailController,
                    'Email Address',
                    keyboardType: TextInputType.emailAddress,
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Enter your email address';
                      }
                      if (!_isValidGmail(value)) {
                        return 'Use a valid Gmail address ending with @gmail.com';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  _buildField(
                    phoneController,
                    'Phone Number',
                    keyboardType: TextInputType.phone,
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Enter your phone number';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'OTP can be sent to this email or phone number later.',
                    style: TextStyle(fontSize: 12, color: Color(0xFF8B7E74)),
                  ),
                  const SizedBox(height: 16),
                  _buildField(
                    passwordController,
                    'Password',
                    obscure: true,
                    showText: _showPassword,
                    toggleVisibility: () {
                      setState(() {
                        _showPassword = !_showPassword;
                      });
                    },
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Enter your password';
                      }
                      if (value.length < 6) {
                        return 'Password must be at least 6 characters';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  _buildField(
                    confirmPasswordController,
                    'Confirm Password',
                    obscure: true,
                    showText: _showConfirmPassword,
                    toggleVisibility: () {
                      setState(() {
                        _showConfirmPassword = !_showConfirmPassword;
                      });
                    },
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Confirm your password';
                      }
                      if (value != passwordController.text) {
                        return 'Passwords do not match';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 28),
                ],
              ),
            ),
            const SizedBox(height: 0),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _createAccount,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFB8957A),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24),
                  ),
                ),
                child: const Text(
                  'CREATE ACCOUNT',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
