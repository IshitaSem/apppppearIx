import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../data/app_data.dart';
import '../models/generated_outfit.dart';
import '../models/wardrobe_item.dart';
import 'outfit_generator_page.dart';
import 'cat_judge_page.dart';

class ToolsPage extends StatefulWidget {
  const ToolsPage({super.key});

  @override
  State<ToolsPage> createState() => _ToolsPageState();
}

class _ToolsPageState extends State<ToolsPage> {
  @override
  Widget build(BuildContext context) {
    final appData = Provider.of<AppData>(context);
    final generatedOutfits = appData.generatedOutfits;

    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F6),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 110),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Fashion Tools',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF2D2620),
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Your personal styling toolkit',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: Color(0xFF8B7E74),
                ),
              ),
              const SizedBox(height: 32),

              // Two buttons side by side
              Row(
                children: [
                  Expanded(
                    child: _ToolButton(
                      title: 'Outfit Generator',
                      description: 'AI-powered outfit\nsuggestions',
                      icon: Icons.auto_awesome_outlined,
                      iconColor: const Color(0xFFB8957A),
                      bgStart: const Color(0xFFFFE5CC),
                      bgEnd: const Color(0xFFFFF5E6),
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const OutfitGeneratorPage(),
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _ToolButton(
                      title: 'Cat Judges Your\nOutfit',
                      description: 'Get sassy feedback',
                      icon: Icons.pets,
                      iconColor: const Color(0xFF2D2620),
                      bgStart: const Color(0xFFFFE5CC),
                      bgEnd: const Color(0xFFFFF5E6),
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const CatJudgePage(),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 32),

              // Partition line
              Container(
                height: 1,
                color: const Color(0xFFE5E5E5),
                margin: const EdgeInsets.symmetric(vertical: 16),
              ),

              // Generated Outfits Section
              if (generatedOutfits.isNotEmpty) ...[
                const Text(
                  'Your Generated Outfits',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2D2620),
                  ),
                ),
                const SizedBox(height: 16),
                ...generatedOutfits.map(
                  (outfit) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _GeneratedOutfitCard(outfit: outfit),
                  ),
                ),
              ] else ...[
                const SizedBox(height: 32),
                Center(
                  child: Column(
                    children: [
                      Icon(
                        Icons.auto_awesome_outlined,
                        size: 48,
                        color: const Color(0xFF8B7E74),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'No outfits generated yet',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF8B7E74),
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Tap "Outfit Generator" to create your first outfit!',
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF8B7E74),
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _ToolButton extends StatefulWidget {
  final String title;
  final String description;
  final IconData icon;
final String? assetPath = null;

  final Color iconColor;
  final Color bgStart;
  final Color bgEnd;
  final VoidCallback onTap;

  const _ToolButton({
    required this.title,
    required this.description,
    required this.icon,
    required this.iconColor,
    required this.bgStart,
    required this.bgEnd,
    required this.onTap,
  });

  @override
  State<_ToolButton> createState() => _ToolButtonState();
}

class _ToolButtonState extends State<_ToolButton> {
  bool isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => isHovered = true),
      onExit: (_) => setState(() => isHovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOut,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: isHovered
                  ? const Color(0x1F000000)
                  : const Color(0x0F000000),
              offset: Offset(0, isHovered ? 8 : 4),
              blurRadius: isHovered ? 32 : 20,
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            borderRadius: BorderRadius.circular(24),
            onTap: widget.onTap,
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [widget.bgStart, widget.bgEnd],
                      ),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: const [
                        BoxShadow(
                          color: Color(0x0A000000),
                          offset: Offset(0, 2),
                          blurRadius: 8,
                        ),
                      ],
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(10),
                      child: widget.assetPath != null
                          ? Image.asset(
                              widget.assetPath!,
                              fit: BoxFit.contain,
                              errorBuilder: (context, error, stackTrace) {
                                return Icon(
                                  widget.icon,
                                  size: 28,
                                  color: widget.iconColor,
                                );
                              },
                            )
                          : Icon(
                              widget.icon,
                              size: 28,
                              color: widget.iconColor,
                            ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    widget.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF2D2620),
                      height: 1.4,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.description,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w400,
                      color: Color(0xFF8B7E74),
                      height: 1.5,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _GeneratedOutfitCard extends StatelessWidget {
  final GeneratedOutfit outfit;

  const _GeneratedOutfitCard({required this.outfit});

  void _showOutfitDetails(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => _OutfitDetailsDialog(outfit: outfit),
    );
  }

  @override
  Widget build(BuildContext context) {
    final dateStr =
        '${outfit.dateCreated.day}/${outfit.dateCreated.month}/${outfit.dateCreated.year}';

    return Container(
      padding: const EdgeInsets.all(16),
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
      child: Row(
        children: [
          // Outfit preview (simplified)
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: const Color(0xFFF3F4F6),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.checkroom,
              color: Color(0xFF8B7E74),
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  outfit.name,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2D2620),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${outfit.occasion} • ${outfit.mood}',
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF8B7E74),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Created on $dateStr',
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF8B7E74),
                  ),
                ),
              ],
            ),
          ),
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () => _showOutfitDetails(context),
              borderRadius: BorderRadius.circular(8),
              child: const Padding(
                padding: EdgeInsets.all(8.0),
                child: Icon(Icons.chevron_right, color: Color(0xFFB8957A)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _OutfitDetailsDialog extends StatelessWidget {
  final GeneratedOutfit outfit;

  const _OutfitDetailsDialog({required this.outfit});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.all(16),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
        ),
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            outfit.name,
                            style: const TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF2D2620),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${outfit.occasion} • ${outfit.mood}',
                            style: const TextStyle(
                              fontSize: 14,
                              color: Color(0xFF8B7E74),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: () => Navigator.pop(context),
                        borderRadius: BorderRadius.circular(8),
                        child: const Padding(
                          padding: EdgeInsets.all(8.0),
                          child: Icon(Icons.close, color: Color(0xFF8B7E74)),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Outfit details
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFAF8F6),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Outfit Details',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF2D2620),
                        ),
                      ),
                      const SizedBox(height: 12),
                      _DetailRow(label: 'Occasion', value: outfit.occasion),
                      const SizedBox(height: 8),
                      _DetailRow(label: 'Mood', value: outfit.mood),
                      const SizedBox(height: 8),
                      _DetailRow(label: 'Weather', value: outfit.weather),
                      const SizedBox(height: 8),
                      _DetailRow(label: 'Fit', value: outfit.fitPreference),
                      const SizedBox(height: 8),
                      _DetailRow(label: 'Color', value: outfit.colorMood),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Outfit items with images
                const Text(
                  'Items Used',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2D2620),
                  ),
                ),
                const SizedBox(height: 12),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: 0.8,
                  ),
                  itemCount: outfit.items.length,
                  itemBuilder: (context, index) {
                    final item = outfit.items[index];
                    return _OutfitItemCard(item: item);
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Color(0xFF8B7E74),
            fontWeight: FontWeight.w500,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            color: Color(0xFF2D2620),
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}

class _OutfitItemCard extends StatelessWidget {
  final WardrobeItem item;

  const _OutfitItemCard({required this.item});

  @override
  Widget build(BuildContext context) {
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
          // Image
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
                child: Image.asset(
                  item.imagePath,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    return Container(
                      color: const Color(0xFFF3F4F6),
                      child: const Icon(
                        Icons.image_not_supported,
                        color: Color(0xFF8B7E74),
                      ),
                    );
                  },
                ),
              ),
            ),
          ),
          // Item info
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
