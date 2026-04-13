
import 'package:flutter/material.dart';
import '../models/user_profile.dart';
import '../models/wardrobe_item.dart';
import '../models/planned_outfit.dart';
import '../models/generated_outfit.dart';
import '../models/trend_post.dart';
import '../../services/api_service.dart';

class AppData extends ChangeNotifier {
  String? userId;
  String? authToken;
  bool isLoading = false;

  Future<void> setAuth(String? newUserId, String? newToken) async {
    userId = newUserId;
    authToken = newToken;
    notifyListeners();
  }
  UserProfile? userProfile;
  String? profileImagePath;

  List<WardrobeItem> wardrobeItems = [];

  final List<PlannedOutfit> plannedOutfits = [];
  final List<GeneratedOutfit> generatedOutfits = [];
  final List<TrendPost> globalPosts = [];
  final List<TrendPost> favoritesPosts = [];


  void addWardrobeItem(WardrobeItem item) {
    wardrobeItems.insert(0, item);
    notifyListeners();
  }

  // syncWardrobeToPlans removed - no more auto-populating from wardrobe uploads

  void updateWardrobeItem(
    String id, {
    String? name,
    String? category,
    String? imageUrl,
    String? imagePath,
  }) {
    final itemIndex = wardrobeItems.indexWhere((item) => item.id == id);
    if (itemIndex < 0) {
      return;
    }

    final updatedItem = wardrobeItems[itemIndex].copyWith(
      name: name,
      category: category,
      imageUrl: imageUrl,
      imagePath: imagePath,
    );

    wardrobeItems[itemIndex] = updatedItem;

    notifyListeners();
  }

  void deleteWardrobeItem(String id) {
    wardrobeItems.removeWhere((item) => item.id == id);
    notifyListeners();
  }

// addOutfitPlan removed - use saveToPlanner instead


  void addGeneratedOutfit(GeneratedOutfit outfit) {
    generatedOutfits.insert(0, outfit);
    notifyListeners();
  }

  void addGlobalPost(TrendPost post) {
    globalPosts.insert(0, post);
    notifyListeners();
  }

  Future<void> loadFeedPosts({String? userId}) async {
    isLoading = true;
    notifyListeners();
    final posts = await ApiService.getFeedPosts(userId: userId);
    globalPosts.clear();
    globalPosts.addAll(posts);
    isLoading = false;
    notifyListeners();
  }

  Future<void> loadSavedPosts(String userId) async {
    isLoading = true;
    notifyListeners();
    final posts = await ApiService.getSavedPosts(userId);
    favoritesPosts.clear();
    favoritesPosts.addAll(posts);
    isLoading = false;
    notifyListeners();
  }


  void saveToPlanner(GeneratedOutfit outfit, DateTime date, {required String name, String? occasion}) {
    final planned = PlannedOutfit(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      dateNumber: date.day,
      month: date.month,
      year: date.year,
      dateLabel: _buildDateLabel(date),
      name: name,
      occasion: occasion,
      items: outfit.items,
    );
    plannedOutfits.insert(0, planned);
    plannedOutfits.sort((a, b) => DateTime(b.year, b.month, b.dateNumber).compareTo(DateTime(a.year, a.month, a.dateNumber)));
    notifyListeners();
  }

  List<PlannedOutfit> getOutfitsForMonth(int month, int year) {
    return plannedOutfits
        .where((outfit) => outfit.month == month && outfit.year == year)
        .toList();
  }

  String _buildDateLabel(DateTime date) {
    const weekdayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const monthNames = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    return '${weekdayNames[date.weekday - 1]}, ${monthNames[date.month - 1]} ${date.day}';
  }

  bool hasOutfitOn(int date, int month, int year) {
    return plannedOutfits.any(
      (outfit) =>
          outfit.dateNumber == date &&
          outfit.month == month &&
          outfit.year == year,
    );
  }

  PlannedOutfit? outfitForDate(int date, int month, int year) {
    try {
      return plannedOutfits.firstWhere(
        (outfit) =>
            outfit.dateNumber == date &&
            outfit.month == month &&
            outfit.year == year,
      );
    } catch (_) {
      return null;
    }
  }

  void updateLoginInfo({
    required String name,
    required String email,
    String? phone,
    required String gender,
    required String size,
    required String aesthetic,
    List<String>? favoriteColors,
  }) {
    userProfile = UserProfile(
      name: name,
      email: email,
      phone: phone,
      gender: gender,
      size: size,
      aesthetic: aesthetic,
      favoriteColors: favoriteColors,
    );
    notifyListeners();
  }

  void updateProfileImage(String imagePath) {
    profileImagePath = imagePath;
    notifyListeners();
  }

  void updateUserProfile({
    required String name,
    required String email,
    String? phone,
    required String gender,
    required String size,
    required String aesthetic,
    List<String>? favoriteColors,
  }) {
    if (userProfile == null) {
      userProfile = UserProfile(
        name: name,
        email: email,
        phone: phone,
        gender: gender,
        size: size,
        aesthetic: aesthetic,
        favoriteColors: favoriteColors,
      );
    } else {
      userProfile!.name = name;
      userProfile!.email = email;
      userProfile!.phone = phone;
      userProfile!.gender = gender;
      userProfile!.size = size;
      userProfile!.aesthetic = aesthetic;
      userProfile!.favoriteColors = favoriteColors;
    }
    notifyListeners();
  }

  Future<void> logout() async {
    userId = null;
    authToken = null;
    notifyListeners();
  }
}
