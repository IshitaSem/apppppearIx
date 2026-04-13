import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import '../models/wardrobe_item.dart';
import '../data/app_data.dart';
import '../services/api_service.dart';

const _pageBackgroundColor = Color(0xFFFAF8F6);
const _textPrimaryColor = Color(0xFF2D2620);
const _textSecondaryColor = Color(0xFF8B7E74);
const _cardBackgroundColor = Color(0xFFFFFFFF);
const _primaryAccentColor = Color(0xFFB8957A);
const _borderColor = Color(0xFFE8DDD3);

class AddItemPage extends StatefulWidget {
  const AddItemPage({super.key});

  @override
  State<AddItemPage> createState() => _AddItemPageState();
}

class _AddItemPageState extends State<AddItemPage> {
  final TextEditingController nameController = TextEditingController();

  final List<String> categories = [
    'Tops',
    'Bottoms',
    'Dresses',
    'Outerwear',
    'Shoes',
    'Accessories',
  ];

  String selectedCategory = 'Tops';
  XFile? selectedImage;
  bool _isLoading = false;

  String? _previewImageUrl;
  Uint8List? _processedPreviewBytes;

  Future<void> pickFromCamera() async {
    final pickedFile = await ImagePicker().pickImage(
      source: ImageSource.camera,
      imageQuality: 85,
    );

    if (pickedFile != null) {
      setState(() {
        selectedImage = pickedFile;
        _previewImageUrl = null;
        _processedPreviewBytes = null;
      });
    }
  }

  Future<void> pickFromGallery() async {
    final pickedFile = await ImagePicker().pickImage(
      source: ImageSource.gallery,
      imageQuality: 85,
    );

    if (pickedFile != null) {
      setState(() {
        selectedImage = pickedFile;
        _previewImageUrl = null;
        _processedPreviewBytes = null;
      });
    }
  }

  Future<void> curateItem() async {
    final appData = Provider.of<AppData>(context, listen: false);

    print('[DEBUG] curateItem() - Current userId: ${appData.userId}');

    if (appData.userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please login first')),
      );
      return;
    }

    if (nameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter item name')),
      );
      return;
    }

    if (selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an image')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final imageBytes = await selectedImage!.readAsBytes();

      final uploadResult = await ApiService.uploadImage(
        userId: appData.userId!,
        fileName: selectedImage!.name,
        imageBytes: imageBytes,
        itemName: nameController.text.trim(),
        category: selectedCategory,
        useBgRemoval: true,
      );

      if (!mounted) return;

      if (uploadResult != null) {
        final imageUrl = uploadResult['image_url']?.toString();
        if (imageUrl != null) {
          _previewImageUrl = ApiService.makeImageUrl(imageUrl);
        }

        final item = WardrobeItem.fromBackend(uploadResult);
        Navigator.pop(context, item);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Upload failed')),
        );
      }
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Upload failed: $error')),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _clearSelection() {
    setState(() {
      selectedImage = null;
      _previewImageUrl = null;
      _processedPreviewBytes = null;
    });
  }

  Future<void> _removeBackground() async {
    if (selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an image first')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final imageBytes = await selectedImage!.readAsBytes();
      final result = await ApiService.removeBackground(imageBytes);

      if (!mounted) return;

      setState(() {
        _isLoading = false;
      });

      if (result['imageBytes'] != null) {
        setState(() {
          _processedPreviewBytes = result['imageBytes'] as Uint8List;
          _previewImageUrl = null;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result['message']?.toString().isNotEmpty == true
                  ? result['message'].toString()
                  : 'Background processed',
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result['message']?.toString().isNotEmpty == true
                  ? result['message'].toString()
                  : 'BG removal failed',
            ),
          ),
        );
      }
    } catch (error) {
      if (!mounted) return;

      setState(() {
        _isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $error')),
      );
    }
  }

  Widget _buildPreview() {
    if (_previewImageUrl != null) {
      return Stack(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Image.network(
              _previewImageUrl!,
              fit: BoxFit.cover,
              width: double.infinity,
              height: 240,
              loadingBuilder: (context, child, loadingProgress) {
                if (loadingProgress == null) return child;
                return Container(
                  height: 240,
                  color: _borderColor,
                  child: const Center(child: CircularProgressIndicator()),
                );
              },
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  height: 240,
                  color: _cardBackgroundColor,
                  child: const Icon(Icons.error, color: Colors.red),
                );
              },
            ),
          ),
          if (_isLoading)
            Container(
              color: Colors.black54,
              child: const Center(
                child: CircularProgressIndicator(color: Colors.white),
              ),
            ),
        ],
      );
    }

    if (_processedPreviewBytes != null) {
      return Stack(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Image.memory(
              _processedPreviewBytes!,
              fit: BoxFit.contain,
              width: double.infinity,
              height: 240,
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  height: 240,
                  color: _cardBackgroundColor,
                  child: const Icon(Icons.error, color: Colors.red),
                );
              },
            ),
          ),
          if (_isLoading)
            Container(
              color: Colors.black54,
              child: const Center(
                child: CircularProgressIndicator(color: Colors.white),
              ),
            ),
        ],
      );
    }

    if (selectedImage == null) {
      return Container(
        height: 240,
        decoration: BoxDecoration(
          color: _cardBackgroundColor,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: _borderColor),
        ),
        child: const Center(
          child: Text(
            'No image selected',
            style: TextStyle(color: Color(0xFF8B7E74), fontSize: 16),
          ),
        ),
      );
    }

    Widget imageWidget;
    if (kIsWeb) {
      imageWidget = Image.network(
        selectedImage!.path,
        fit: BoxFit.cover,
        width: double.infinity,
        height: 240,
        errorBuilder: (context, error, stackTrace) {
          return Container(
            height: 240,
            color: _cardBackgroundColor,
            child: const Icon(Icons.error, color: Colors.red),
          );
        },
      );
    } else {
      imageWidget = Image.file(
        File(selectedImage!.path),
        fit: BoxFit.cover,
        width: double.infinity,
        height: 240,
        errorBuilder: (context, error, stackTrace) {
          return Container(
            height: 240,
            color: _cardBackgroundColor,
            child: const Icon(Icons.error, color: Colors.red),
          );
        },
      );
    }

    return Stack(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: imageWidget,
        ),
        if (_isLoading)
          Container(
            color: Colors.black54,
            child: const Center(
              child: CircularProgressIndicator(color: Colors.white),
            ),
          ),
      ],
    );
  }

  @override
  void dispose() {
    nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _pageBackgroundColor,
      appBar: AppBar(
        backgroundColor: _pageBackgroundColor,
        elevation: 0,
        scrolledUnderElevation: 0,
        title: const Text(
          'Add Wardrobe Item',
          style: TextStyle(
            color: _textPrimaryColor,
            fontWeight: FontWeight.w600,
          ),
        ),
        iconTheme: const IconThemeData(color: _textPrimaryColor),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 30),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Add a new piece to your wardrobe',
              style: TextStyle(fontSize: 14, color: _textSecondaryColor),
            ),
            const SizedBox(height: 20),

            Container(
              height: 240,
              width: double.infinity,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                border: _previewImageUrl == null && _processedPreviewBytes == null
                    ? Border.all(color: _borderColor)
                    : Border.all(color: Colors.transparent),
              ),
              child: _buildPreview(),
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : pickFromCamera,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _primaryAccentColor,
                      foregroundColor: _cardBackgroundColor,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                      ),
                    ),
                    icon: const Icon(Icons.camera_alt_outlined),
                    label: const Text('Camera'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _isLoading ? null : pickFromGallery,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: _textPrimaryColor,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                      ),
                    ),
                    icon: const Icon(Icons.photo_library_outlined),
                    label: const Text('Gallery'),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: selectedImage == null || _isLoading ? null : _clearSelection,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: _primaryAccentColor,
                      side: BorderSide(color: _borderColor),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                      ),
                    ),
                    icon: const Icon(Icons.close),
                    label: const Text('Clear'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: selectedImage == null || _isLoading ? null : _removeBackground,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: _primaryAccentColor,
                      side: BorderSide(color: _borderColor),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                      ),
                    ),
                    icon: const Icon(Icons.photo_filter),
                    label: const Text('BG Remove'),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            TextField(
              controller: nameController,
              readOnly: _isLoading,
              decoration: InputDecoration(
                labelText: 'Item Name',
                hintText: 'e.g. White Blouse',
                filled: true,
                fillColor: _cardBackgroundColor,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20),
                  borderSide: BorderSide.none,
                ),
              ),
            ),

            const SizedBox(height: 20),

            DropdownButtonFormField<String>(
              initialValue: selectedCategory,
              items: categories.map((category) {
                return DropdownMenuItem<String>(
                  value: category,
                  child: Text(category),
                );
              }).toList(),
              onChanged: _isLoading
                  ? null
                  : (value) {
                      if (value != null) {
                        setState(() {
                          selectedCategory = value;
                        });
                      }
                    },
              decoration: InputDecoration(
                labelText: 'Category',
                filled: true,
                fillColor: _cardBackgroundColor,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20),
                  borderSide: BorderSide.none,
                ),
              ),
            ),

            const SizedBox(height: 28),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : curateItem,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _primaryAccentColor,
                  foregroundColor: _cardBackgroundColor,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          color: _cardBackgroundColor,
                          strokeWidth: 2,
                        ),
                      )
                    : const Text(
                        'CURATE',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}