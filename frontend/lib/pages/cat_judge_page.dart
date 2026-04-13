import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../data/app_data.dart';
import '../models/wardrobe_item.dart';

class CatJudgePage extends StatefulWidget {
  const CatJudgePage({super.key});

  @override
  State<CatJudgePage> createState() => _CatJudgePageState();
}

class _CatJudgePageState extends State<CatJudgePage>
    with TickerProviderStateMixin {
  late AnimationController _catAnimation;
  late AnimationController _reviewAnimation;

  Set<int> selectedItems = {};
  String? currentReview;
  bool isReviewingOutfit = false;

  final List<String> sassyReviews = [
    "Cute… I approve 😼",
    "Too basic.",
    "Main character energy.",
    "We love the vibe 💅",
    "Could be worse.",
    "The color? Chef's kiss!",
    "Giving minimal aesthetic 😾",
    "Extra? Yes. Bad? No.",
    "I'd wear it.",
    "Not my style, but okay.",
    "The drip is immaculate.",
    "Serving looks, honey!",
    "I'm obsessed 🐱",
    "The fit is… it is.",
    "Purr-fect choice!",
  ];

  @override
  void initState() {
    super.initState();
    _catAnimation = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _reviewAnimation = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _catAnimation.dispose();
    _reviewAnimation.dispose();
    super.dispose();
  }

  void _toggleItemSelection(int index) {
    setState(() {
      if (selectedItems.contains(index)) {
        selectedItems.remove(index);
      } else {
        selectedItems.add(index);
      }
    });
  }

  Future<void> _submitForReview() async {
    if (selectedItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one item!')),
      );
      return;
    }

    final appData = Provider.of<AppData>(context, listen: false);
    if (appData.userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please login first')),
      );
      return;
    }

    setState(() {
      isReviewingOutfit = true;
      currentReview = null;
    });

    _catAnimation.forward();

    final reviewText = _generateReview();

    await _reviewAnimation.forward();

    if (!mounted) return;

    setState(() {
      currentReview = reviewText;
      isReviewingOutfit = false;
    });
  }

  String _generateReview() {
    final appData = Provider.of<AppData>(context, listen: false);
    final selectedWardrobeItems = selectedItems
        .map((index) => appData.wardrobeItems[index])
        .toList();

    if (selectedWardrobeItems.isEmpty) {
      return 'Meow... I cannot judge an invisible outfit.';
    }

    final hasAccessories = selectedWardrobeItems.any(
      (item) => item.category.toLowerCase() == 'accessories',
    );
    final hasMultipleItems = selectedWardrobeItems.length > 2;
    final names = selectedWardrobeItems.map((item) => item.name).join(', ');

    final randomIndex = names.hashCode.abs() % sassyReviews.length;
    String review = sassyReviews[randomIndex];

    if (!hasAccessories && hasMultipleItems) {
      review = sassyReviews[(randomIndex + 2) % sassyReviews.length];
    } else if (hasAccessories) {
      review = sassyReviews[(randomIndex + 1) % sassyReviews.length];
    }

    return '$review\n\nSelected: $names';
  }

  void _cancelReview() {
    setState(() {
      isReviewingOutfit = false;
      currentReview = null;
      selectedItems.clear();
    });
    _catAnimation.reset();
    _reviewAnimation.reset();
  }

  @override
  Widget build(BuildContext context) {
    final appData = Provider.of<AppData>(context);
    final wardrobeItems = appData.wardrobeItems;
    final selectedWardrobeItems = selectedItems
        .map((index) => wardrobeItems[index])
        .toList(growable: false);

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
          'Cat Judges Your Outfit',
          style: TextStyle(
            color: Color(0xFF2D2620),
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    ScaleTransition(
                      scale: Tween<double>(begin: 0.5, end: 1.0).animate(
                        CurvedAnimation(
                          parent: _catAnimation,
                          curve: Curves.elasticOut,
                        ),
                      ),
                      child: Container(
                        width: 120,
                        height: 120,
                        decoration: BoxDecoration(
                          color: const Color(0xFFF3F4F6),
                          borderRadius: BorderRadius.circular(60),
                          boxShadow: const [
                            BoxShadow(
                              color: Color(0x1F000000),
                              offset: Offset(0, 4),
                              blurRadius: 12,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.pets,
                          size: 60,
                          color: Color(0xFF2D2620),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    if (!isReviewingOutfit && currentReview == null) ...[
                      const Text(
                        'Show me your outfit!',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF2D2620),
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Select items from your wardrobe for the judge',
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF8B7E74),
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],

                    if (currentReview != null) ...[
                      FadeTransition(
                        opacity: _reviewAnimation,
                        child: Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(
                              color: const Color(0xFFB8957A),
                              width: 2,
                            ),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x1FB8957A),
                                offset: Offset(0, 4),
                                blurRadius: 12,
                              ),
                            ],
                          ),
                          child: Column(
                            children: [
                              const Text(
                                'The cat says:',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Color(0xFF8B7E74),
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Text(
                                currentReview!,
                                style: const TextStyle(
                                  fontSize: 22,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFFB8957A),
                                  height: 1.4,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      const Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'Your selected outfit',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF2D2620),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        height: 140,
                        child: ListView.separated(
                          scrollDirection: Axis.horizontal,
                          itemCount: selectedWardrobeItems.length,
                          separatorBuilder: (_, _) => const SizedBox(width: 12),
                          itemBuilder: (context, index) {
                            final item = selectedWardrobeItems[index];
                              return Container(
                                width: 120,
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(16),
                                  boxShadow: const [
                                    BoxShadow(
                                      color: Color(0x0A000000),
                                      offset: Offset(0, 4),
                                      blurRadius: 12,
                                    ),
                                  ],
                                ),
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(16),
                                  child: item.imagePath.startsWith('assets/')
                                      ? Image.asset(
                                          item.imagePath,
                                          fit: BoxFit.cover,
                                          errorBuilder: (context, error, stackTrace) => Container(
                                            color: const Color(0xFFF3F4F6),
                                            child: const Icon(
                                              Icons.image_not_supported,
                                              color: Color(0xFF8B7E74),
                                            ),
                                          ),
                                        )
                                      : Image.network(
                                          item.imagePath,
                                          fit: BoxFit.cover,
                                          errorBuilder: (context, error, stackTrace) => Container(
                                            color: const Color(0xFFF3F4F6),
                                            child: const Icon(
                                              Icons.image_not_supported,
                                              color: Color(0xFF8B7E74),
                                            ),
                                          ),
                                        ),
                                ),
                              );
                          },
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],

                    if (currentReview == null) ...[
                      const Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'Select Items',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF2D2620),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      if (wardrobeItems.isEmpty)
                        Container(
                          padding: const EdgeInsets.all(32),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x0A000000),
                                offset: Offset(0, 4),
                                blurRadius: 12,
                              ),
                            ],
                          ),
                          child: const Column(
                            children: [
                              Icon(
                                Icons.inventory_2_outlined,
                                size: 48,
                                color: Color(0xFF8B7E74),
                              ),
                              SizedBox(height: 16),
                              Text(
                                'Please add items in your wardrobe',
                                style: TextStyle(
                                  fontSize: 16,
                                  color: Color(0xFF8B7E74),
                                  fontWeight: FontWeight.w500,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        )
                      else
                        GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 2,
                                crossAxisSpacing: 12,
                                mainAxisSpacing: 12,
                                childAspectRatio: 0.8,
                              ),
                          itemCount: wardrobeItems.length,
                          itemBuilder: (context, index) {
                            final item = wardrobeItems[index];
                            final isSelected = selectedItems.contains(index);
                            return _WardrobeItemSelector(
                              item: item,
                              isSelected: isSelected,
                              onTap: () => _toggleItemSelection(index),
                            );
                          },
                        ),
                      const SizedBox(height: 32),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          child: Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: currentReview != null
                      ? _cancelReview
                      : () => Navigator.pop(context),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    side: BorderSide(
                      color: currentReview != null
                          ? const Color(0xFFB8957A)
                          : const Color(0xFFE5E5E5),
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    currentReview != null ? 'Try Again' : 'Cancel',
                    style: TextStyle(
                      color: currentReview != null
                          ? const Color(0xFFB8957A)
                          : const Color(0xFF8B7E74),
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: currentReview != null
                      ? () => Navigator.pop(context)
                      : _submitForReview,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: const Color(0xFFB8957A),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    currentReview != null ? 'Close' : 'Submit',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _WardrobeItemSelector extends StatefulWidget {
  final WardrobeItem item;
  final bool isSelected;
  final VoidCallback onTap;

  const _WardrobeItemSelector({
    required this.item,
    required this.isSelected,
    required this.onTap,
  });

  @override
  State<_WardrobeItemSelector> createState() => _WardrobeItemSelectorState();
}

class _WardrobeItemSelectorState extends State<_WardrobeItemSelector> {
  bool isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => isHovered = true),
      onExit: (_) => setState(() => isHovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: widget.isSelected
                ? const Color(0xFFB8957A)
                : const Color(0xFFE5E5E5),
            width: widget.isSelected ? 2 : 1,
          ),
          boxShadow: [
            BoxShadow(
              color: widget.isSelected
                  ? const Color(0x1FB8957A)
                  : const Color(0x0A000000),
              offset: Offset(0, widget.isSelected ? 4 : 2),
              blurRadius: widget.isSelected ? 12 : 4,
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: widget.onTap,
            borderRadius: BorderRadius.circular(12),
            child: Stack(
              children: [
                Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    color: const Color(0xFFF3F4F6),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: widget.item.imagePath.startsWith('assets/')
                        ? Image.asset(
                            widget.item.imagePath,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) => Container(
                              color: const Color(0xFFF3F4F6),
                              child: const Icon(
                                Icons.image_not_supported,
                                color: Color(0xFF8B7E74),
                              ),
                            ),
                          )
                        : Image.network(
                            widget.item.imagePath,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) => Container(
                              color: const Color(0xFFF3F4F6),
                              child: const Icon(
                                Icons.image_not_supported,
                                color: Color(0xFF8B7E74),
                              ),
                            ),
                          ),
                  ),
                ),
                Positioned(
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.bottomCenter,
                        end: Alignment.topCenter,
                        colors: [
                          Colors.black.withOpacity(0.7),
                          Colors.black.withOpacity(0.0),
                        ],
                      ),
                      borderRadius: const BorderRadius.only(
                        bottomLeft: Radius.circular(12),
                        bottomRight: Radius.circular(12),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          widget.item.name,
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          widget.item.category,
                          style: const TextStyle(
                            fontSize: 11,
                            color: Colors.white70,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                if (widget.isSelected)
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: const Color(0xFFB8957A),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x1F000000),
                            offset: Offset(0, 2),
                            blurRadius: 8,
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.check,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}