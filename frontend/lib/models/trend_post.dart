import 'dart:typed_data';
import '../../services/api_service.dart';

class TrendPost {
  String id = '';
  String profileName;
  String location;
  String title;
  String caption;
  String imagePath;
  String? imageUrl;
  Uint8List? imageBytes;
  bool isUserPost;

  int likes;
  int dislikes;
  bool isLiked;
  bool isDisliked;
  bool isSaved;

  TrendPost({
    this.id = '',
    required this.profileName,
    required this.location,
    required this.title,
    required this.caption,
    required this.imagePath,
    this.imageUrl,
    this.imageBytes,
    required this.likes,
    required this.dislikes,
    this.isLiked = false,
    this.isDisliked = false,
    this.isSaved = false,
    this.isUserPost = false,
  });

  factory TrendPost.fromJson(Map<String, dynamic> json) {
    String caption = json['caption'] ?? '';
    String title = caption.isNotEmpty ? caption.split('\n').first : 'Fashion Post';
    final post = TrendPost(
      id: json['id'] ?? '',
      profileName: json['username'] ?? 'Anonymous',
      location: '',
      title: title,
      caption: caption,
      imagePath: '',
      imageUrl: ApiService.makeImageUrl(json['image_url'] ?? ''),
      likes: (json['likes_count'] ?? 0) as int,
      dislikes: (json['dislikes_count'] ?? 0) as int,
      isLiked: json['is_liked_by_current_user'] ?? false,
      isDisliked: json['is_disliked_by_current_user'] ?? false,
      isSaved: json['is_saved_by_current_user'] ?? false,
    );
    return post;
  }
}
