import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../data/app_data.dart';
import '../models/trend_post.dart';
import '../services/api_service.dart';
import 'create_post_page.dart';

class GlobalPage extends StatefulWidget {
  const GlobalPage({super.key});

  @override
  State<GlobalPage> createState() => _GlobalPageState();
}

class _GlobalPageState extends State<GlobalPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final appData = Provider.of<AppData>(context, listen: false);
      if (appData.userId != null) {
        appData.loadFeedPosts(userId: appData.userId);
      }
    });
  }

  Future<void> _refreshPosts() async {
    final appData = Provider.of<AppData>(context, listen: false);
    if (appData.userId != null) {
      await appData.loadFeedPosts(userId: appData.userId);
    }
  }

Future<void> _toggleLike(int index) async {
    final appData = Provider.of<AppData>(context, listen: false);
    if (appData.userId == null) return;
    final postId = appData.globalPosts[index].id;
    await ApiService.toggleLikePost(postId, appData.userId!);
    await appData.loadFeedPosts(userId: appData.userId);
  }

Future<void> _toggleDislike(int index) async {
    final appData = Provider.of<AppData>(context, listen: false);
    if (appData.userId == null) return;
    final postId = appData.globalPosts[index].id;
    await ApiService.toggleDislikePost(postId, appData.userId!);
    await appData.loadFeedPosts(userId: appData.userId);
  }

  Future<void> _toggleSave(int index) async {
    final appData = Provider.of<AppData>(context, listen: false);
    if (appData.userId == null) return;
    final postId = appData.globalPosts[index].id;
    await ApiService.toggleSavePost(postId, appData.userId!);
    await appData.loadFeedPosts(userId: appData.userId);
  }

  Future<void> _openCreatePostPage() async {
    final appData = Provider.of<AppData>(context, listen: false);
    if (appData.userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please login to create posts')));
      return;
    }
    final newPostMap = await Navigator.push<Map<String, dynamic>>(
      context,
      MaterialPageRoute(builder: (context) => const CreatePostPage()),
    );

    if (newPostMap != null) {
      final newPost = TrendPost.fromJson(newPostMap);
      appData.addGlobalPost(newPost);
    }
    await appData.loadFeedPosts(userId: appData.userId);
  }

  void _openPostPopup(TrendPost post, int index) {
    showDialog(
      context: context,
      barrierColor: const Color.fromRGBO(0, 0, 0, 0.45),
      builder: (context) {
        return Dialog(
          insetPadding: const EdgeInsets.symmetric(
            horizontal: 18,
            vertical: 24,
          ),
          backgroundColor: Colors.transparent,
          child: StatefulBuilder(
            builder: (context, setStateDialog) {
              return Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(28),
                ),
                clipBehavior: Clip.antiAlias,
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Stack(
                        children: [
                          post.imageUrl != null 
                            ? Image.network(
                                  post.imageUrl!,
                                  height: 260,
                                  width: double.infinity,
                                  fit: BoxFit.contain,
                                loadingBuilder: (context, child, loadingProgress) {
                                  if (loadingProgress == null) return child;
                                  return Container(
                                    height: 260,
                                    color: const Color(0xFFF3F4F6),
                                    child: const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                                  );
                                },
                                errorBuilder: (context, error, stackTrace) => Container(
                                    height: 260,
                                    color: Colors.grey[200],
                                    child: const Icon(Icons.image_not_supported, size: 50, color: Colors.grey),
                                  ),
                              )
                            : Image.asset(
                                post.imagePath,
                                height: 260,
                                width: double.infinity,
                                fit: BoxFit.contain,
                              ),
                          Positioned(
                            top: 12,
                            right: 12,
                            child: GestureDetector(
                              onTap: () => Navigator.pop(context),
                              child: Container(
                                width: 38,
                                height: 38,
                                decoration: BoxDecoration(
                                  color: const Color.fromRGBO(
                                    255,
                                    255,
                                    255,
                                    0.95,
                                  ),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(
                                  Icons.close,
                                  color: Color(0xFF2D2620),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                      Padding(
                        padding: const EdgeInsets.fromLTRB(18, 18, 18, 20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              post.title,
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF2D2620),
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'by ${post.profileName}',
                              style: const TextStyle(
                                fontSize: 14,
                                color: Color(0xFF8B7E74),
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            const SizedBox(height: 10),
                            Text(
                              post.caption,
                              style: const TextStyle(
                                fontSize: 15,
                                height: 1.55,
                                color: Color(0xFF6F6258),
                              ),
                            ),
                            const SizedBox(height: 18),
                            Row(
                              children: [
                                _PopupActionButton(
                                  icon: post.isLiked
                                      ? Icons.favorite
                                      : Icons.favorite_border,
                                  color: post.isLiked
                                      ? const Color(0xFFE25555)
                                      : const Color(0xFF8B7E74),
                                  label: '${post.likes}',
                                  onTap: () {
                                    Navigator.pop(context);
                                    _toggleLike(index);
                                  },
                                ),
                                const SizedBox(width: 10),
                                _PopupActionButton(
                                  icon: post.isDisliked
                                      ? Icons.heart_broken
                                      : Icons.heart_broken_outlined,
                                  color: post.isDisliked
                                      ? const Color(0xFFE25555)
                                      : const Color(0xFF8B7E74),
                                  label: '${post.dislikes}',
                                  onTap: () {
                                    Navigator.pop(context);
                                    _toggleDislike(index);
                                  },
                                ),
                                const SizedBox(width: 10),
                                _PopupActionButton(
                                  icon: post.isSaved
                                      ? Icons.bookmark
                                      : Icons.bookmark_border,
                                  color: post.isSaved
                                      ? const Color(0xFFB8957A)
                                      : const Color(0xFF8B7E74),
                                  label: post.isSaved ? 'Saved' : 'Save',
                                  onTap: () {
                                    Navigator.pop(context);
                                    _toggleSave(index);
                                  },
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F6),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 110),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Expanded(
                    child: Text(
                      'Global Trends',
                      style: TextStyle(
                        fontSize: 30,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF2D2620),
                      ),
                    ),
                  ),
                  Material(
                    color: Colors.transparent,
                    child: InkWell(
                      borderRadius: BorderRadius.circular(16),
                      onTap: _openCreatePostPage,
                      child: Container(
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white,
                          boxShadow: const [
                            BoxShadow(
                              color: Color(0x0F000000),
                              blurRadius: 12,
                              offset: Offset(0, 4),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.add,
                          color: Color(0xFFB8957A),
                          size: 28,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              const Text(
                'Fashion inspiration worldwide',
                style: TextStyle(fontSize: 14, color: Color(0xFF8B7E74)),
              ),
              const SizedBox(height: 24),
  Consumer<AppData>(
    builder: (context, appData, child) {
      if (appData.isLoading) {
        return const Center(child: CircularProgressIndicator());
      }
      if (appData.globalPosts.isEmpty) {
        return const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.trending_up, size: 64, color: Color(0xFF8B7E74)),
              SizedBox(height: 16),
              Text('No posts yet', style: TextStyle(fontSize: 18, color: Color(0xFF8B7E74))),
              Text('Follow friends and explore trends!', style: TextStyle(fontSize: 14, color: Color(0xFF8B7E74))),
            ],
          ),
        );
      }
      return RefreshIndicator(
        onRefresh: _refreshPosts,
        child: GridView.builder(
          key: ValueKey(appData.globalPosts.length),
          itemCount: appData.globalPosts.length,
          shrinkWrap: true,
          physics: const AlwaysScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            childAspectRatio: 0.75,
          ),
          itemBuilder: (context, index) => TrendSocialCard(
            post: appData.globalPosts[index],
            onLike: () => _toggleLike(index),
            onDislike: () => _toggleDislike(index),
            onSave: () => _toggleSave(index),
            onOpen: () => _openPostPopup(appData.globalPosts[index], index),
          ),
        ),
      );
    },
  ),
            ],
          ),
        ),
      ),
    );
  }
}

class TrendSocialCard extends StatefulWidget {
  final TrendPost post;
  final VoidCallback onLike;
  final VoidCallback onDislike;
  final VoidCallback onSave;
  final VoidCallback onOpen;

  const TrendSocialCard({
    super.key,
    required this.post,
    required this.onLike,
    required this.onDislike,
    required this.onSave,
    required this.onOpen,
  });

  @override
  State<TrendSocialCard> createState() => _TrendSocialCardState();
}

class _TrendSocialCardState extends State<TrendSocialCard> {
  bool pressedLike = false;
  bool pressedSave = false;
  bool pressedDislike = false;

  void _animate(String type) async {
    setState(() {
      if (type == 'like') pressedLike = true;
      if (type == 'save') pressedSave = true;
      if (type == 'dislike') pressedDislike = true;
    });

    await Future.delayed(const Duration(milliseconds: 120));

    if (mounted) {
      setState(() {
        if (type == 'like') pressedLike = false;
        if (type == 'save') pressedSave = false;
        if (type == 'dislike') pressedDislike = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final post = widget.post;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0F000000),
            blurRadius: 20,
            offset: Offset(0, 4),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 3,
            child: GestureDetector(
              onTap: widget.onOpen,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  post.imageUrl != null
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
                      : (post.imageBytes != null
                          ? Image.memory(post.imageBytes!, fit: BoxFit.cover)
                          : Image.asset(
                              post.imagePath.isNotEmpty ? post.imagePath : 'assets/paris.jpg',
                              fit: BoxFit.cover,
                            )),
                  Positioned(
                    bottom: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: const Color.fromRGBO(255, 255, 255, 0.9),
                        shape: BoxShape.circle,
                      ),
                      child: AnimatedScale(
                        scale: pressedSave ? 1.2 : 1.0,
                        duration: const Duration(milliseconds: 160),
                        child: GestureDetector(
                          onTap: () {
                            _animate('save');
                            widget.onSave();
                          },
                          child: Icon(
                            post.isSaved
                                ? Icons.bookmark
                                : Icons.bookmark_border,
                            size: 18,
                            color: post.isSaved
                                ? const Color(0xFFB8957A)
                                : const Color(0xFF8B7E74),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    post.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF2D2620),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    post.caption,
                    style: const TextStyle(
                      fontSize: 12,
                      height: 1.4,
                      color: Color(0xFF8B7E74),
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      AnimatedScale(
                        scale: pressedLike ? 1.22 : 1.0,
                        duration: const Duration(milliseconds: 160),
                        child: GestureDetector(
                          onTap: () {
                            _animate('like');
                            widget.onLike();
                          },
                          child: Icon(
                            post.isLiked
                                ? Icons.favorite
                                : Icons.favorite_border,
                            size: 18,
                            color: post.isLiked
                                ? const Color(0xFFE25555)
                                : const Color(0xFF8B7E74),
                          ),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${post.likes}',
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF6F6258),
                        ),
                      ),
                      const SizedBox(width: 16),
                      AnimatedScale(
                        scale: pressedDislike ? 1.18 : 1.0,
                        duration: const Duration(milliseconds: 160),
                        child: GestureDetector(
                          onTap: () {
                            _animate('dislike');
                            widget.onDislike();
                          },
                          child: Icon(
                            post.isDisliked
                                ? Icons.heart_broken
                                : Icons.heart_broken_outlined,
                            size: 18,
                            color: post.isDisliked
                                ? const Color(0xFFE25555)
                                : const Color(0xFF8B7E74),
                          ),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${post.dislikes}',
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF6F6258),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PopupActionButton extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String label;
  final VoidCallback onTap;

  const _PopupActionButton({
    required this.icon,
    required this.color,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Material(
        color: const Color(0xFFF8F3EE),
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 14),
            child: Column(
              children: [
                Icon(icon, color: color),
                const SizedBox(height: 6),
                Text(
                  label,
                  style: const TextStyle(
                    color: Color(0xFF6F6258),
                    fontWeight: FontWeight.w600,
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
