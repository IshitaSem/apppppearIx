import 'wardrobe_item.dart';

class PlannedOutfit {
  final String id;
  final int dateNumber;
  final int month;
  final int year;
  final String dateLabel;
  final String name;
  final String? occasion;
  final List<WardrobeItem> items;  // From generated outfit

  PlannedOutfit({
    required this.id,
    required this.dateNumber,
    required this.month,
    required this.year,
    required this.dateLabel,
    required this.name,
    this.occasion,
    required this.items,
  });

  PlannedOutfit copyWith({
    String? id,
    int? dateNumber,
    int? month,
    int? year,
    String? dateLabel,
    String? name,
    String? occasion,
    List<WardrobeItem>? items,
  }) {
    return PlannedOutfit(
      id: id ?? this.id,
      dateNumber: dateNumber ?? this.dateNumber,
      month: month ?? this.month,
      year: year ?? this.year,
      dateLabel: dateLabel ?? this.dateLabel,
      name: name ?? this.name,
      occasion: occasion ?? this.occasion,
      items: items ?? this.items,
    );
  }

  // For planner UI compatibility
  int get itemCount => items.length;

  // First item for thumbnail
  WardrobeItem get firstItem => items.isNotEmpty ? items.first : WardrobeItem(id: '', name: 'No Item', category: '', imagePath: '', imageUrl: '', dateAdded: DateTime.now());
}

