import 'wardrobe_item.dart';

class GeneratedOutfit {
  final String id;
  final String name;
  final DateTime dateCreated;
  final String occasion;
  final String mood;
  final String weather;
  final String fitPreference;
  final String colorMood;
  final List<WardrobeItem> items;
  final String? accessoriesSuggestion;
  final String? stylingNotes;

  GeneratedOutfit({
    required this.id,
    required this.name,
    required this.dateCreated,
    required this.occasion,
    required this.mood,
    required this.weather,
    required this.fitPreference,
    required this.colorMood,
    required this.items,
    this.accessoriesSuggestion,
    this.stylingNotes,
  });

  GeneratedOutfit copyWith({
    String? id,
    String? name,
    DateTime? dateCreated,
    String? occasion,
    String? mood,
    String? weather,
    String? fitPreference,
    String? colorMood,
    List<WardrobeItem>? items,
    String? accessoriesSuggestion,
    String? stylingNotes,
  }) {
    return GeneratedOutfit(
      id: id ?? this.id,
      name: name ?? this.name,
      dateCreated: dateCreated ?? this.dateCreated,
      occasion: occasion ?? this.occasion,
      mood: mood ?? this.mood,
      weather: weather ?? this.weather,
      fitPreference: fitPreference ?? this.fitPreference,
      colorMood: colorMood ?? this.colorMood,
      items: items ?? this.items,
      accessoriesSuggestion: accessoriesSuggestion ?? this.accessoriesSuggestion,
      stylingNotes: stylingNotes ?? this.stylingNotes,
    );
  }

  factory GeneratedOutfit.random({
    required String name,
    required List<WardrobeItem> availableItems,
  }) {
    final random = DateTime.now().millisecondsSinceEpoch;
    final occasions = ['Casual day', 'College / Work', 'Party', 'Date', 'Travel', 'Home comfy'];
    final moods = ['Minimal', 'Streetwear', 'Cute', 'Cozy', 'Edgy', 'Soft girl', 'Sporty'];
    final weathers = ['Hot', 'Mild', 'Cold', 'Rainy'];
    final fits = ['Oversized', 'Fitted', 'Balanced', 'Any'];
    final colors = ['Dark', 'Light', 'Neutral', 'Colorful', 'Random'];

    final occasion = occasions[random % occasions.length];
    final mood = moods[(random ~/ 7) % moods.length];
    final weather = weathers[(random ~/ 49) % weathers.length];
    final fit = fits[(random ~/ 196) % fits.length];
    final color = colors[(random ~/ 784) % colors.length];

    final filteredItems = _filterItemsByPreferences(availableItems, occasion, mood, weather, fit, color);

    final top = filteredItems.where((item) => item.category.toLowerCase().contains('top')).toList();
    final bottoms = filteredItems.where((item) => item.category.toLowerCase().contains('bottom')).toList();
    final dresses = filteredItems.where((item) => item.category.toLowerCase().contains('dress')).toList();
    final shoes = filteredItems.where((item) => item.category.toLowerCase().contains('shoe')).toList();
    final accessories = filteredItems.where((item) => item.category.toLowerCase().contains('accessory')).toList();

    final outfitItems = <WardrobeItem>[];

    if (dresses.isNotEmpty && (random % 3) == 0) {
      outfitItems.add(dresses[random % dresses.length]);
    } else {
      if (top.isNotEmpty) outfitItems.add(top[random % top.length]);
      if (bottoms.isNotEmpty) outfitItems.add(bottoms[(random + 1) % bottoms.length]);
    }

    if (shoes.isNotEmpty) outfitItems.add(shoes[(random + 2) % shoes.length]);

    String? accessoriesSuggestion;
    if (accessories.isNotEmpty) {
      final accessory = accessories[(random + 3) % accessories.length];
      accessoriesSuggestion = 'Try adding ${accessory.name} to complete the look!';
    }

    return GeneratedOutfit(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: name,
      dateCreated: DateTime.now(),
      occasion: occasion,
      mood: mood,
      weather: weather,
      fitPreference: fit,
      colorMood: color,
      items: outfitItems,
      accessoriesSuggestion: accessoriesSuggestion,
      stylingNotes: 'Random stylist suggestion',
    );
  }

  static List<WardrobeItem> _filterItemsByPreferences(
    List<WardrobeItem> items, String occasion, String mood, String weather, String fit, String color,
  ) {
    return items;
  }
}
