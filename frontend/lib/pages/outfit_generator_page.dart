import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../data/app_data.dart';
import '../services/api_service.dart';
import '../models/wardrobe_item.dart';
import '../models/generated_outfit.dart';
import 'outfit_output_page.dart';

class OutfitGeneratorPage extends StatefulWidget {
  const OutfitGeneratorPage({super.key});

  @override
  State<OutfitGeneratorPage> createState() => _OutfitGeneratorPageState();
}

class _OutfitGeneratorPageState extends State<OutfitGeneratorPage> {
  int _currentQuestion = 0;
  final Map<String, String> _answers = {};

  final List<Map<String, dynamic>> _questions = [
    {
      'question': "What's the occasion?",
      'options': [
        {'label': 'Casual day', 'value': 'Casual day'},
        {'label': 'College / Work', 'value': 'College / Work'},
        {'label': 'Party', 'value': 'Party'},
        {'label': 'Date', 'value': 'Date'},
        {'label': 'Travel', 'value': 'Travel'},
        {'label': 'Home comfy', 'value': 'Home comfy'},
      ],
    },
    {
      'question': "What's your mood or aesthetic?",
      'options': [
        {'label': 'Minimal', 'value': 'Minimal'},
        {'label': 'Streetwear', 'value': 'Streetwear'},
        {'label': 'Cute', 'value': 'Cute'},
        {'label': 'Cozy', 'value': 'Cozy'},
        {'label': 'Edgy', 'value': 'Edgy'},
        {'label': 'Soft girl', 'value': 'Soft girl'},
        {'label': 'Sporty', 'value': 'Sporty'},
      ],
    },
    {
      'question': "What's the weather like?",
      'options': [
        {'label': 'Hot', 'value': 'Hot'},
        {'label': 'Mild', 'value': 'Mild'},
        {'label': 'Cold', 'value': 'Cold'},
        {'label': 'Rainy', 'value': 'Rainy'},
      ],
    },
    {
      'question': "What's your fit preference?",
      'options': [
        {'label': 'Oversized', 'value': 'Oversized'},
        {'label': 'Fitted', 'value': 'Fitted'},
        {'label': 'Balanced', 'value': 'Balanced'},
        {'label': 'Any', 'value': 'Any'},
      ],
    },
    {
      'question': "What's your color mood?",
      'options': [
        {'label': 'Dark', 'value': 'Dark'},
        {'label': 'Light', 'value': 'Light'},
        {'label': 'Neutral', 'value': 'Neutral'},
        {'label': 'Colorful', 'value': 'Colorful'},
        {'label': 'Random', 'value': 'Random'},
      ],
    },
  ];

  void _selectAnswer(String value) {
    setState(() {
      _answers[_questions[_currentQuestion]['question'] as String] = value;
      if (_currentQuestion < _questions.length - 1) {
        _currentQuestion++;
      } else {
        _generateOutfit();
      }
    });
  }

  Future<void> _generateOutfit() async {
    final appData = Provider.of<AppData>(context, listen: false);

    if (appData.userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please login first.')),
      );
      return;
    }

    final hasWardrobeItems = appData.wardrobeItems.isNotEmpty;
    if (!hasWardrobeItems) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No items in your wardrobe. Add some items first.'),
        ),
      );
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Generating outfit...')),
    );

    final occasion = _answers[_questions[0]['question']] ?? 'Casual day';

    final result = await ApiService.generateOutfit(
      appData.userId!,
      occasion,
    );

    if (!mounted) return;

    if (result == null || !result['success'] || result['data']?['outfit'] == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result?['message'] ?? result?['data']?['message'] ?? 'Failed to generate outfit'),
        ),
      );
      return;
    }

    final backendOutfit = result['data']['outfit'];
    final stylingNotes = (result['data']['styling_notes'] as List? ?? []).join('\n');

    // Parse outfit items to WardrobeItem
    final List<WardrobeItem> selectedItems = [];
    for (final key in backendOutfit.keys) {
      if (backendOutfit[key] is Map<String, dynamic>) {
        final itemMap = backendOutfit[key] as Map<String, dynamic>;
        final item = WardrobeItem.fromBackend(itemMap);
        selectedItems.add(item);
      }
    }

    if (selectedItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No suitable outfit items found')),
      );
      return;
    }

    final outfit = GeneratedOutfit(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: '$occasion Outfit',
      occasion: occasion,
      mood: _answers[_questions[1]['question']] ?? 'Any',
      weather: _answers[_questions[2]['question']] ?? 'Mild',
      fitPreference: _answers[_questions[3]['question']] ?? 'Any',
      colorMood: _answers[_questions[4]['question']] ?? 'Random',
      items: selectedItems,
      dateCreated: DateTime.now(),
      stylingNotes: stylingNotes,
    );

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => OutfitOutputPage(outfit: outfit),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appData = Provider.of<AppData>(context);
    final hasWardrobeItems = appData.wardrobeItems.isNotEmpty;
    final currentQuestion = _questions[_currentQuestion];
    final progress = (_currentQuestion + 1) / _questions.length;

    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F6),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Color(0xFF2D2620)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Outfit Generator',
          style: TextStyle(
            color: Color(0xFF2D2620),
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              if (!hasWardrobeItems) ...[
                const SizedBox(height: 40),
                const Icon(
                  Icons.warning_amber_rounded,
                  size: 72,
                  color: Color(0xFFB8957A),
                ),
                const SizedBox(height: 24),
                const Text(
                  'No wardrobe items found',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2D2620),
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                const Text(
                  'Add items to your wardrobe before generating an outfit.',
                  style: TextStyle(
                    fontSize: 16,
                    color: Color(0xFF8B7E74),
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFB8957A),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 28,
                      vertical: 16,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                  ),
                  child: const Text('Go to Wardrobe'),
                ),
              ] else ...[
                LinearProgressIndicator(
                  value: progress,
                  backgroundColor: const Color(0xFFE5E5E5),
                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFB8957A)),
                ),
                const SizedBox(height: 32),
                Text(
                  'Question ${_currentQuestion + 1} of ${_questions.length}',
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF8B7E74),
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  currentQuestion['question'] as String,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2D2620),
                    height: 1.3,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),
                Expanded(
                  child: ListView.builder(
                    itemCount: (currentQuestion['options'] as List).length,
                    itemBuilder: (context, index) {
                      final option = (currentQuestion['options'] as List)[index] as Map<String, dynamic>;

                      return Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: _OptionButton(
                          label: option['label'] as String,
                          onTap: () => _selectAnswer(option['value'] as String),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _OptionButton extends StatefulWidget {
  final String label;
  final VoidCallback onTap;

  const _OptionButton({
    required this.label,
    required this.onTap,
  });

  @override
  State<_OptionButton> createState() => _OptionButtonState();
}

class _OptionButtonState extends State<_OptionButton> {
  bool isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => isHovered = true),
      onExit: (_) => setState(() => isHovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOut,
        decoration: BoxDecoration(
          color: isHovered ? const Color(0xFFFBF6F2) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isHovered ? const Color(0xFFB8957A) : const Color(0xFFE5E5E5),
            width: 1,
          ),
          boxShadow: isHovered
              ? [const BoxShadow(color: Color(0x1FB8957A), offset: Offset(0, 4), blurRadius: 12)]
              : null,
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            borderRadius: BorderRadius.circular(16),
            onTap: widget.onTap,
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Text(
                widget.label,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: isHovered ? const Color(0xFFB8957A) : const Color(0xFF2D2620),
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

