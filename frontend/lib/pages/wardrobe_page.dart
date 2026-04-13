import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../widgets/wardrobe_item_card.dart';
import '../models/wardrobe_item.dart';
import '../data/app_data.dart';
import 'add_item_page.dart';

class WardrobePage extends StatefulWidget {
  const WardrobePage({super.key});

  @override
  State<WardrobePage> createState() => _WardrobePageState();
}

class _WardrobePageState extends State<WardrobePage> {
  final List<String> categories = [
    'All',
    'Tops',
    'Bottoms',
    'Dresses',
    'Outerwear',
    'Shoes',
    'Accessories',
  ];

  String selectedCategory = 'All';
  String searchQuery = '';

  Future<void> _addNewItem() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const AddItemPage()),
    );
    await _loadWardrobe();
  }

  Future<void> _loadWardrobe() async {
    final appData = Provider.of<AppData>(context, listen: false);
    if (appData.userId != null) {
      final items = await ApiService.getWardrobe(appData.userId!);
      appData.wardrobeItems.clear();
      for (final itemJson in items) {
        appData.wardrobeItems.add(WardrobeItem.fromBackend(itemJson));
      }
      // syncWardrobeToPlans removed - planner no longer auto-populates from wardrobe
      if (mounted) {
        setState(() {});
      }
    }
  }

  void _showRenameDialog(BuildContext context, String itemId, String currentName) {
    final controller = TextEditingController(text: currentName);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Rename Item'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'New name'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              final appData = Provider.of<AppData>(context, listen: false);
              appData.updateWardrobeItem(itemId, name: controller.text.trim());
              Navigator.pop(context);
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Item renamed')),
                );
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ).then((_) => controller.dispose());
  }

  void _showDeleteDialog(BuildContext context, String itemId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Item?'),
        content: const Text('This item will be removed from your wardrobe and planner.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            onPressed: () {
              final appData = Provider.of<AppData>(context, listen: false);
              appData.deleteWardrobeItem(itemId);
              Navigator.pop(context);
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Item deleted')),
                );
              }
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  String _normalizeCategoryName(String displayName) {
    final Map<String, String> categoryMap = {
      'All': '',
      'Tops': 'top',
      'Bottoms': 'bottom',
      'Dresses': 'dress',
      'Outerwear': 'outerwear',
      'Shoes': 'shoe',
      'Accessories': 'accessory',
    };
    return categoryMap[displayName] ?? displayName.toLowerCase();
  }

  @override
  Widget build(BuildContext context) {
    final appData = Provider.of<AppData>(context);
    final normalizedCategory = _normalizeCategoryName(selectedCategory);

    final filteredItems = appData.wardrobeItems.where((item) {
      final matchesCategory =
          selectedCategory == 'All' || item.category.toLowerCase() == normalizedCategory;

      final matchesSearch =
          item.name.toLowerCase().contains(searchQuery.toLowerCase());

      return matchesCategory && matchesSearch;
    }).toList();

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'My Wardrobe',
                        style: TextStyle(
                          fontSize: 30,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF2D2620),
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Curate your personal style',
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF8B7E74),
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white,
                    boxShadow: const [
                      BoxShadow(
                        color: Color(0x14000000),
                        blurRadius: 4,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: _addNewItem,
                      customBorder: const CircleBorder(),
                      child: const Icon(
                        Icons.add,
                        color: Color(0xFFB8957A),
                        size: 24,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            if (appData.wardrobeItems.isEmpty)
              Container(
                padding: const EdgeInsets.all(48),
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
                      size: 64,
                      color: Color(0xFF8B7E74),
                    ),
                    SizedBox(height: 24),
                    Text(
                      'Add new items in your wardrobe',
                      style: TextStyle(
                        fontSize: 18,
                        color: Color(0xFF8B7E74),
                        fontWeight: FontWeight.w500,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              )
            else ...[
              TextField(
                onChanged: (value) {
                  setState(() {
                    searchQuery = value;
                  });
                },
                decoration: InputDecoration(
                  hintText: 'Search your closet...',
                  prefixIcon: const Icon(Icons.search, color: Color(0xFF8B7E74)),
                  filled: true,
                  fillColor: Colors.white,
                  contentPadding: const EdgeInsets.symmetric(vertical: 16),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              SizedBox(
                height: 44,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: categories.length,
                  separatorBuilder: (_, _) => const SizedBox(width: 10),
                  itemBuilder: (context, index) {
                    final category = categories[index];
                    final isSelected = category == selectedCategory;

                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          selectedCategory = category;
                        });
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 12,
                        ),
                        decoration: BoxDecoration(
                          color: isSelected ? const Color(0xFFB8957A) : Colors.white,
                          borderRadius: BorderRadius.circular(30),
                        ),
                        child: Text(
                          category,
                          style: TextStyle(
                            color: isSelected ? Colors.white : const Color(0xFF8B7E74),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 24),
              GridView.builder(
                itemCount: filteredItems.length,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  childAspectRatio: 0.68,
                ),
                itemBuilder: (context, index) {
                  final item = filteredItems[index];
                  return WardrobeItemCard(
                    name: item.name,
                    category: item.category,
                    imagePath: item.imagePath,
                    dateAdded: item.dateAdded,
                    onEdit: () => _showRenameDialog(context, item.id, item.name),
                    onDelete: () => _showDeleteDialog(context, item.id),
                  );
                },
              ),
            ],
          ],
        ),
      ),
    );
  }
}