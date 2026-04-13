import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../data/app_data.dart';
import '../models/trend_post.dart';

class FavoritesPage extends StatefulWidget {
  const FavoritesPage({super.key});

  @override
  State<FavoritesPage> createState() => _FavoritesPageState();
}

class _FavoritesPageState extends State<FavoritesPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final appData = Provider.of<AppData>(context, listen: false);
      if (appData.userId != null) {
        appData.loadSavedPosts(appData.userId!);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppData>(
      builder: (context, appData, child) {
        if (appData.isLoading) {
          return const Scaffold(
            backgroundColor: Color(0xFFFAF8F6),
            body: Center(child: CircularProgressIndicator()),
          );
        }
        final savedPosts = appData.favoritesPosts;
        return Scaffold(
          backgroundColor: const Color(0xFFFAF8F6),
          appBar: AppBar(
            backgroundColor: const Color(0xFFFAF8F6),
            scrolledUnderElevation: 0,
            title: const Text(
              'Global Saves',
              style: TextStyle(color: Color(0xFF2D2620)),
            ),
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Color(0xFF2D2620)),
              onPressed: () => Navigator.pop(context),
            ),
          ),
          body: SafeArea(
            child: savedPosts.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.bookmark_border,
                          size: 64,
                          color: Color(0xFF8B7E74),
                        ),
                        SizedBox(height: 16),
                        Text(
                          'No saved posts yet',
                          style: TextStyle(fontSize: 18, color: Color(0xFF8B7E74)),
                        ),
                        SizedBox(height: 8),
                        Text(
                          'Start exploring trends and save your favorites!',
                          style: TextStyle(fontSize: 14, color: Color(0xFF8B7E74)),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  )
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Your Saved Posts',
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF2D2620),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${savedPosts.length} saved ${savedPosts.length == 1 ? 'post' : 'posts'}',
                          style: const TextStyle(
                            fontSize: 14,
                            color: Color(0xFF8B7E74),
                          ),
                        ),
                        const SizedBox(height: 24),
                        ...savedPosts.map(
                          (post) => Padding(
                            padding: const EdgeInsets.only(bottom: 16),
                            child: _FavoritePostCard(post: post),
                          ),
                        ),
                      ],
                    ),
                  ),
          ),
        );
      },
    );
  }
}

class _FavoritePostCard extends StatelessWidget {
  final TrendPost post;

  const _FavoritePostCard({required this.post});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0F000000),
            blurRadius: 10,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Post image
          Container(
            height: 200,
            width: double.infinity,
            decoration: const BoxDecoration(
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: ClipRRect(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
              child: post.imageUrl != null 
                ? Image.network(
                    post.imageUrl!,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => Container(
                      color: Colors.grey[200],
                      child: const Icon(Icons.image_not_supported, size: 50, color: Colors.grey),
                    ),
                    loadingBuilder: (context, child, loadingProgress) {
                      if (loadingProgress == null) return child;
                      return Container(
                        color: Colors.grey[100],
                        child: const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                      );
                    },
                  )
                : Image.asset(
                    post.imagePath.isNotEmpty ? post.imagePath : 'assets/paris.jpg',
                    fit: BoxFit.cover,
                  ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Profile info
                Row(
                  children: [
                    const CircleAvatar(
                      radius: 16,
                      backgroundColor: Color(0xFFB8957A),
                      child: Icon(Icons.person, size: 16, color: Colors.white),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            post.profileName,
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                            ),
                          ),
                          Text(
                            post.location,
                            style: const TextStyle(
                              color: Color(0xFF8B7E74),
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                // Post title
                Text(
                  post.title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2D2620),
                  ),
                ),
                const SizedBox(height: 8),
                // Post caption
                Text(
                  post.caption,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF8B7E74),
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 12),
                // Like and dislike counts
                Row(
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.favorite,
                          size: 16,
                          color: post.isLiked ? Color(0xFFDB2777) : Color(0xFF8B7E74),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${post.likes}',
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFF8B7E74),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(width: 16),
                    Row(
                      children: [
                        Icon(
                          Icons.thumb_down_alt_outlined,
                          size: 16,
                          color: post.isDisliked ? Color(0xFFE25555) : Color(0xFF8B7E74),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${post.dislikes}',
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFF8B7E74),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
