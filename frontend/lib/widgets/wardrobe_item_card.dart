
import 'package:flutter/material.dart';

class WardrobeItemCard extends StatelessWidget {
  final String name;
  final String category;
  final String imagePath;
  final DateTime dateAdded;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const WardrobeItemCard({
    super.key,
    required this.name,
    required this.category,
    required this.imagePath,
    required this.dateAdded,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
  Widget imageWidget;

  if (imagePath.isEmpty) {
    imageWidget = Container(
      color: const Color(0xFFF5F0EB),
      child: const Center(
        child: Icon(Icons.image_outlined, size: 48, color: Color(0xFFB8957A)),
      ),
    );
  } else if (imagePath.startsWith('assets/')) {
    imageWidget = Image.asset(
      imagePath,
      fit: BoxFit.cover,
      width: double.infinity,
      errorBuilder: (context, error, stackTrace) {
        return Container(
          color: const Color(0xFFF5F0EB),
          child: const Center(
            child: Icon(
              Icons.broken_image_outlined,
              size: 48,
              color: Color(0xFFB8957A),
            ),
          ),
        );
      },
    );
  } else {
    imageWidget = Image.network(
      imagePath,
      fit: BoxFit.cover,
      width: double.infinity,
      errorBuilder: (context, error, stackTrace) {
        return Container(
          color: const Color(0xFFF5F0EB),
          child: const Center(
            child: Icon(
              Icons.broken_image_outlined,
              size: 48,
              color: Color(0xFFB8957A),
            ),
          ),
        );
      },
    );
  }

    final bool hasActions = onEdit != null || onDelete != null;
    final Widget imageWithActions = Stack(
      children: [
        Positioned.fill(child: imageWidget),
        if (hasActions)
          Positioned(
            top: 12,
            right: 12,
            child: Material(
              color: Colors.white70,
              shape: const CircleBorder(),
              child: PopupMenuButton<String>(
                color: Colors.white,
                icon: const Icon(
                  Icons.more_vert,
                  size: 20,
                  color: Color(0xFF2D2620),
                ),
                onSelected: (value) {
                  if (value == 'rename') {
                    onEdit?.call();
                  } else if (value == 'delete') {
                    onDelete?.call();
                  }
                },
                itemBuilder: (_) => const [
                  PopupMenuItem(value: 'rename', child: Text('Rename')),
                  PopupMenuItem(value: 'delete', child: Text('Delete')),
                ],
              ),
            ),
          ),
      ],
    );

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: const [
          BoxShadow(
            color: Color(0x14000000),
            blurRadius: 18,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: ClipRRect(
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(24),
              ),
              child: imageWithActions,
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 12, 14, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  category.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF8B7E74),
                    fontWeight: FontWeight.w500,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  name,
                  style: const TextStyle(
                    fontSize: 16,
                    color: Color(0xFF2D2620),
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Added ${_formatDate(dateAdded)}',
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF8B7E74),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return 'today';
    } else if (difference.inDays == 1) {
      return 'yesterday';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else {
      return '${date.month}/${date.day}/${date.year}';
    }
  }
}
