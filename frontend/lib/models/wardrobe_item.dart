class WardrobeItem {
  final String id;
  final String name;
  final String category;
  final String imagePath;
  final String imageUrl;
  final DateTime dateAdded;

  const WardrobeItem({
    required this.id,
    required this.name,
    required this.category,
    required this.imagePath,
    required this.imageUrl,
    required this.dateAdded,
  });

  WardrobeItem copyWith({
    String? id,
    String? name,
    String? category,
    String? imagePath,
    String? imageUrl,
    DateTime? dateAdded,
  }) {
    return WardrobeItem(
      id: id ?? this.id,
      name: name ?? this.name,
      category: category ?? this.category,
      imagePath: imagePath ?? this.imagePath,
      imageUrl: imageUrl ?? this.imageUrl,
      dateAdded: dateAdded ?? this.dateAdded,
    );
  }

  factory WardrobeItem.fromBackend(Map<String, dynamic> json) {
    return WardrobeItem(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Unknown Item',
      category: json['category']?.toString() ?? 'Other',
      imagePath: json['image_url']?.toString() ?? json['image_path']?.toString() ?? '',
      imageUrl: json['image_url']?.toString() ?? json['imagePath']?.toString() ?? json['image_path']?.toString() ?? '',
      dateAdded: _parseDate(json['date_added'] ?? json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  static DateTime _parseDate(String dateStr) {
    try {
      return DateTime.parse(dateStr);
    } catch (e) {
      return DateTime.now();
    }
  }
}
