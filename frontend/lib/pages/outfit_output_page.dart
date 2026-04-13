import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/api_config.dart';
import '../data/app_data.dart';
import '../models/wardrobe_item.dart';
import '../models/generated_outfit.dart';

class OutfitOutputPage extends StatefulWidget {
  final GeneratedOutfit outfit;

  const OutfitOutputPage({super.key, required this.outfit});

  @override
  State<OutfitOutputPage> createState() => _OutfitOutputPageState();
}

class _OutfitOutputPageState extends State<OutfitOutputPage> {
  late final TextEditingController _nameController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.outfit.name);
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  void _saveOutfit() {
    final appData = Provider.of<AppData>(context, listen: false);
    final namedOutfit = GeneratedOutfit(
      id: widget.outfit.id,
      name: _nameController.text.trim().isEmpty ? 'My Outfit' : _nameController.text.trim(),
      dateCreated: widget.outfit.dateCreated,
      occasion: widget.outfit.occasion,
      mood: widget.outfit.mood,
      weather: widget.outfit.weather,
      fitPreference: widget.outfit.fitPreference,
      colorMood: widget.outfit.colorMood,
      items: widget.outfit.items,
      accessoriesSuggestion: widget.outfit.accessoriesSuggestion,
      stylingNotes: widget.outfit.stylingNotes,
    );

    appData.addGeneratedOutfit(namedOutfit);
    Navigator.popUntil(context, (route) => route.isFirst);
  }

  void _generateAgain() {
    final appData = Provider.of<AppData>(context, listen: false);
    final newOutfit = GeneratedOutfit.random(
      name: 'Generated Outfit',
      availableItems: appData.wardrobeItems,
    );

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => OutfitOutputPage(outfit: newOutfit),
      ),
    );
  }

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
          'Your Outfit ✨',
          style: TextStyle(
            color: Color(0xFF2D2620),
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x0F000000),
                      offset: Offset(0, 2),
                      blurRadius: 8,
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Name your outfit',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF2D2620),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _nameController,
                      decoration: InputDecoration(
                        hintText: 'Enter outfit name...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFFE5E5E5)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFFB8957A)),
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                      style: const TextStyle(fontSize: 16, color: Color(0xFF2D2620)),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x0F000000),
                      offset: Offset(0, 2),
                      blurRadius: 8,
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Your Generated Outfit',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF2D2620),
                      ),
                    ),
                    const SizedBox(height: 16),

                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                        childAspectRatio: 0.8,
                      ),
                      itemCount: widget.outfit.items.length,
                      itemBuilder: (context, index) {
                        final item = widget.outfit.items[index];
                        return _OutfitItemPreview(item: item);
                      },
                    ),

                    if (widget.outfit.accessoriesSuggestion != null) ...[
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFFE5CC),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.lightbulb_outline, color: Color(0xFFB8957A), size: 20),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                widget.outfit.accessoriesSuggestion!,
                                style: const TextStyle(
                                  fontSize: 14,
                                  color: Color(0xFFB8957A),
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              const SizedBox(height: 32),

              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(context),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: const BorderSide(color: Color(0xFFE5E5E5)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text(
                        'Cancel',
                        style: TextStyle(color: Color(0xFF8B7E74), fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),

                  Expanded(
                    child: OutlinedButton(
                      onPressed: _generateAgain,
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: const BorderSide(color: Color(0xFFB8957A)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text(
                        'Generate Again',
                        style: TextStyle(color: Color(0xFFB8957A), fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),

                  Expanded(
                    child: ElevatedButton(
                      onPressed: _saveOutfit,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: const Color(0xFFB8957A),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text(
                        'Save Outfit',
                        style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _saveToPlanner,
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: const BorderSide(color: Color(0xFFB8957A)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text(
                        'Save to Planner',
                        style: TextStyle(color: Color(0xFFB8957A), fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _saveToPlanner() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now().add(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );

    if (picked != null) {
      final name = _nameController.text.trim().isEmpty ? 'My Outfit' : _nameController.text.trim();
      final appData = Provider.of<AppData>(context, listen: false);
      final namedOutfit = GeneratedOutfit(
        id: widget.outfit.id,
        name: name,
        dateCreated: widget.outfit.dateCreated,
        occasion: widget.outfit.occasion,
        mood: widget.outfit.mood,
        weather: widget.outfit.weather,
        fitPreference: widget.outfit.fitPreference,
        colorMood: widget.outfit.colorMood,
        items: widget.outfit.items,
        accessoriesSuggestion: widget.outfit.accessoriesSuggestion,
        stylingNotes: widget.outfit.stylingNotes,
      );
      appData.saveToPlanner(namedOutfit, picked, name: name);
      appData.addGeneratedOutfit(namedOutfit);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Outfit saved to planner for ${picked.day} ${_getMonthName(picked.month)}!')),
        );
        Navigator.pop(context);
      }
    }
  }

  String _getMonthName(int month) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[month - 1];
  }
}

String _buildImageUrl(String imagePath, String imageUrl) {
  if (imageUrl.isNotEmpty) return imageUrl;
  if (imagePath.isEmpty) return '';
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  if (imagePath.startsWith('/uploads/')) {
    return '${getBaseUrl()}$imagePath';
  }
  return imagePath;
}

Widget imageWidget(String imagePath, String imageUrl) {
  Widget imageWidget;
  if (imagePath.isEmpty && imageUrl.isEmpty) {
    imageWidget = Container(
      color: const Color(0xFFF3F4F6),
      child: const Icon(Icons.image_not_supported, color: Color(0xFF8B7E74)),
    );
  } else if (imagePath.startsWith('assets/')) {
    imageWidget = Image.asset(
      imagePath,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        return Container(
          color: const Color(0xFFF3F4F6),
          child: const Icon(Icons.broken_image_outlined, color: Color(0xFF8B7E74)),
        );
      },
    );
  } else {
    imageWidget = Image.network(
      _buildImageUrl(imagePath, imageUrl),
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        return Container(
          color: const Color(0xFFF3F4F6),
          child: const Icon(Icons.broken_image_outlined, color: Color(0xFF8B7E74)),
        );
      },
    );
  }
  return imageWidget;
}

class _OutfitItemPreview extends StatelessWidget {
  final WardrobeItem item;

  const _OutfitItemPreview({required this.item});

  @override
  Widget build(BuildContext context) {
    final finalImageUrl = _buildImageUrl(item.imagePath, item.imageUrl);
    print("Generated outfit image URL: $finalImageUrl for item: ${item.name}");
    
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE5E5E5)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            offset: Offset(0, 2),
            blurRadius: 4,
          ),
        ],
      ),
      child: Column(
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(12),
                  topRight: Radius.circular(12),
                ),
                color: const Color(0xFFF3F4F6),
              ),
              child: ClipRRect(
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(12),
                  topRight: Radius.circular(12),
                ),
                child: imageWidget(item.imagePath, item.imageUrl),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  item.name,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2D2620),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  item.category,
                  style: const TextStyle(
                    fontSize: 11,
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

