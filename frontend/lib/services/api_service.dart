import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../models/trend_post.dart';

class ApiService {
static const String baseUrl = 'https://apppearix-1.onrender.com';
  static Future<Map<String, dynamic>?> register({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return data['data'] ?? data;
      }

      return {
        'success': false,
        'message': data['detail'] ?? 'Register failed',
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Could not connect to server: $e',
      };
    }
  }

  static Future<Map<String, dynamic>?> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return data['data'] ?? data;
      }

      return {
        'success': false,
        'message': data['detail'] ?? 'Login failed',
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Could not connect to server: $e',
      };
    }
  }

  static Future<Map<String, dynamic>> removeBackground(Uint8List imageBytes) async {
    try {
      final uri = Uri.parse('$baseUrl/upload/remove-background');
      final request = http.MultipartRequest('POST', uri);

      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: 'photo.png',
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final String? imageBase64 = data['data']?['image_base64'];

        return {
          'success': data['success'] ?? false,
          'message': data['message'] ?? '',
          'imageBytes': imageBase64 != null ? base64Decode(imageBase64) : null,
          'backgroundRemoved': data['data']?['background_removed'] ?? false,
        };
      }

      return {
        'success': false,
        'message': data['detail'] ?? 'Background removal failed',
        'imageBytes': null,
        'backgroundRemoved': false,
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Could not process image: $e',
        'imageBytes': null,
        'backgroundRemoved': false,
      };
    }
  }

  static Future<Map<String, dynamic>?> uploadImage({
    required String userId,
    required String fileName,
    required Uint8List imageBytes,
    required String itemName,
    required String category,
    bool useBgRemoval = false,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/upload/');
      final request = http.MultipartRequest('POST', uri);

      request.fields['user_id'] = userId;
      request.fields['use_bg_removal'] = useBgRemoval.toString();
      request.fields['item_name'] = itemName;
      request.fields['category'] = category;

      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: fileName,
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['success'] == true) {
        return data['data'] as Map<String, dynamic>;
      }

      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<List<dynamic>> getWardrobe(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/wardrobe/all?user_id=$userId'),
      );

      if (response.statusCode == 200) {
        List<dynamic> items = [];
        final decoded = jsonDecode(response.body);

        if (decoded is List) {
          items = decoded;
        } else if (decoded is Map<String, dynamic> && decoded['data'] is List) {
          items = decoded['data'] as List<dynamic>;
        }

        // Fix image URLs to full paths
        for (var item in items) {
          if (item is Map && item['image_url'] != null) {
            item['image_url'] = makeImageUrl(item['image_url']);
          }
        }

        return items;
      }

      return [];
    } catch (e) {
      return [];
    }
  }

  static Future<Map<String, dynamic>?> generateOutfit(
    String userId,
    String occasion,
  ) async {
    try {
      final uri = Uri.parse(
        '$baseUrl/ai/generate-outfit?user_id=$userId&occasion=$occasion',
      );

      final response = await http.get(uri);
      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return data;
      }

      return {
        'success': false,
        'message': data['detail'] ?? 'Failed to generate outfit',
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Could not connect to server: $e',
      };
    }
  }

  static String makeImageUrl(String path) {
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    return '$baseUrl$path';
  }

  // Feed APIs
  static Future<List<TrendPost>> getFeedPosts({String? userId}) async {
    try {
      String url = '$baseUrl/feed/posts';
      if (userId != null && userId.isNotEmpty) {
        url += '?user_id=$userId';
      }
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List posts = data['feed'] ?? [];
        return posts.map<TrendPost>((p) => TrendPost.fromJson(p)).toList();
      }
    } catch (e) {
      print('Error fetching feed: $e');
    }
    return [];
  }

  static Future<Map<String, dynamic>?> createFeedPost({
    required Uint8List imageBytes,
    required String caption,
    required String userId,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/feed/posts');
      final request = http.MultipartRequest('POST', uri);
      request.fields['user_id'] = userId;
      request.fields['caption'] = caption;
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: 'post_${DateTime.now().millisecondsSinceEpoch}.png',
        ),
      );
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          return data['post'];
        }
      }
    } catch (e) {
      print('Error creating post: $e');
    }
    return null;
  }

  static Future<Map<String, dynamic>?> toggleLikePost(String postId, String userId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/feed/posts/$postId/like'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_id': userId}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          return data['post'];
        }
      }
    } catch (e) {
      print('Error toggling like: $e');
    }
    return null;
  }

  static Future<Map<String, dynamic>?> toggleDislikePost(String postId, String userId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/feed/posts/$postId/dislike'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_id': userId}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          return data['post'];
        }
      }
    } catch (e) {
      print('Error toggling dislike: $e');
    }
    return null;
  }

  static Future<Map<String, dynamic>?> toggleSavePost(String postId, String userId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/feed/posts/$postId/save'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_id': userId}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          return data['post'];
        }
      }
    } catch (e) {
      print('Error toggling save: $e');
    }
    return null;
  }

  static Future<List<TrendPost>> getSavedPosts(String userId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/feed/saved/$userId'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List posts = data['saved'] ?? [];
        return posts.map<TrendPost>((p) => TrendPost.fromJson(p)).toList();
      }
    } catch (e) {
      print('Error fetching saved posts: $e');
    }
    return [];
  }
}
