import 'wardrobe_item.dart';

class OutfitPlan {
  final String id;
  final int dateNumber;
  final int month;
  final int year;
  final String dateLabel;
  final String name;
  final int itemCount;
  final WardrobeItem wardrobeItem;

  OutfitPlan({
    required this.id,
    required this.dateNumber,
    required this.month,
    required this.year,
    required this.dateLabel,
    required this.name,
    required this.itemCount,
    required this.wardrobeItem,
  });

  OutfitPlan copyWith({
    String? id,
    int? dateNumber,
    int? month,
    int? year,
    String? dateLabel,
    String? name,
    int? itemCount,
    WardrobeItem? wardrobeItem,
  }) {
    return OutfitPlan(
      id: id ?? this.id,
      dateNumber: dateNumber ?? this.dateNumber,
      month: month ?? this.month,
      year: year ?? this.year,
      dateLabel: dateLabel ?? this.dateLabel,
      name: name ?? this.name,
      itemCount: itemCount ?? this.itemCount,
      wardrobeItem: wardrobeItem ?? this.wardrobeItem,
    );
  }
}
