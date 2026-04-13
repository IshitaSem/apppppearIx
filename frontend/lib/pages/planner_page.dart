

import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../data/app_data.dart';
import '../models/planned_outfit.dart';

class PlannerPage extends StatefulWidget {
  const PlannerPage({super.key});

  @override
  State<PlannerPage> createState() => _PlannerPageState();
}

class _PlannerPageState extends State<PlannerPage> {
  late int selectedDate;
  late String currentMonth;
  late int currentYear;

@override
  void initState() {
    super.initState();
    final now = DateTime.now();
    selectedDate = now.day;
    currentMonth = _getMonthName(now.month);
    currentYear = now.year;
  }


  String _getMonthName(int month) {
    const months = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];
    return months[month - 1];
  }

  List<DateInfo> generateDatesForMonth(
    int year,
    String month,
    AppData appData,
  ) {
    final months = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];

    int monthIndex = months.indexOf(month) + 1;
    DateTime firstDay = DateTime(year, monthIndex, 1);
    int daysInMonth = DateTime(year, monthIndex + 1, 0).day;

    List<DateInfo> dates = [];

    // Add empty cells for days before the first day of the month
    int startWeekday = firstDay.weekday; // 1 = Monday, 7 = Sunday
    for (int i = 1; i < startWeekday; i++) {
      dates.add(DateInfo(day: '', date: 0, hasOutfit: false));
    }

    // Add actual days
    for (int day = 1; day <= daysInMonth; day++) {
      DateTime date = DateTime(year, monthIndex, day);
      String dayName = [
        'Mon',
        'Tue',
        'Wed',
        'Thu',
        'Fri',
        'Sat',
        'Sun',
      ][date.weekday - 1];
      bool hasOutfit = appData.hasOutfitOn(day, monthIndex, year);
      dates.add(DateInfo(day: dayName, date: day, hasOutfit: hasOutfit));
    }

    return dates;
  }

  void selectDate(int date) {
    if (date != 0) {
      setState(() {
        selectedDate = date;
      });
    }
  }

  void navigateMonth(int direction) {
    final months = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];

    int currentIndex = months.indexOf(currentMonth);
    currentIndex += direction;

    if (currentIndex < 0) {
      currentIndex = 11;
      currentYear--;
    } else if (currentIndex > 11) {
      currentIndex = 0;
      currentYear++;
    }

    setState(() {
      currentMonth = months[currentIndex];
      if (selectedDate > DateTime(currentYear, currentIndex + 1, 0).day) {
        selectedDate = 1;
      }
    });
  }

  bool hasOutfitForDate(int date, AppData appData) {
    return appData.hasOutfitOn(date, getMonthIndex(currentMonth), currentYear);
  }

  int getMonthIndex(String month) {
    final months = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];
    return months.indexOf(month) + 1;
  }

  List<PlannedOutfit> getMonthOutfits(AppData appData) {
    return appData.getOutfitsForMonth(getMonthIndex(currentMonth), currentYear);
  }

  PlannedOutfit? getSelectedOutfit(AppData appData) {
    return appData.outfitForDate(
      selectedDate,
      getMonthIndex(currentMonth),
      currentYear,
    );
  }

  Future<void> _planNewOutfit(AppData appData) async {
    // Temporary: FAB now shows message - will update to generated outfit + date picker
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Plan an outfit for this date (coming soon)')),
    );
  }

  String _buildDateLabel(int date, int month, int year) {
    final weekdayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    final monthNames = [
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
    final selected = DateTime(year, month, date);
    return '${weekdayNames[selected.weekday - 1]}, ${monthNames[month - 1]} $date';
  }

  @override
  Widget build(BuildContext context) {
    final appData = Provider.of<AppData>(context);
    final dates = generateDatesForMonth(currentYear, currentMonth, appData);
    final monthOutfits = getMonthOutfits(appData);
    final noOutfitPlanned = !hasOutfitForDate(selectedDate, appData);

    return Scaffold(
      backgroundColor: PlannerColors.pageBackground,
      floatingActionButton: Container(
        width: 56,
        height: 56,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: PlannerColors.primaryTaupe,
          boxShadow: const [
            BoxShadow(
              color: Color(0x26000000),
              blurRadius: 8,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () => _planNewOutfit(appData),
            customBorder: const CircleBorder(),
            child: const Icon(Icons.add, color: Colors.white, size: 28),
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 110),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Outfit Planner',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w600,
                  color: PlannerColors.textPrimary,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Plan your week with style',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: PlannerColors.textSecondary,
                ),
              ),
              const SizedBox(height: 32),

              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                margin: const EdgeInsets.only(bottom: 28),
                decoration: BoxDecoration(
                  color: PlannerColors.cardBackground,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: PlannerColors.textSecondary.withOpacity(0.1),
                      offset: const Offset(0, 4),
                      blurRadius: 20,
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _MonthArrowButton(
                          icon: Icons.chevron_left,
                          onTap: () => navigateMonth(-1),
                        ),
                        Text(
                          '$currentMonth $currentYear',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textPrimary,
                          ),
                        ),
                        _MonthArrowButton(
                          icon: Icons.chevron_right,
                          onTap: () => navigateMonth(1),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    // Day headers
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        Text(
                          'Mon',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textSecondary,
                          ),
                        ),
                        Text(
                          'Tue',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textSecondary,
                          ),
                        ),
                        Text(
                          'Wed',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textSecondary,
                          ),
                        ),
                        Text(
                          'Thu',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textSecondary,
                          ),
                        ),
                        Text(
                          'Fri',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textSecondary,
                          ),
                        ),
                        Text(
                          'Sat',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textSecondary,
                          ),
                        ),
                        Text(
                          'Sun',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate:
                          const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 7,
                            crossAxisSpacing: 8,
                            mainAxisSpacing: 8,
                          ),
                      itemCount: dates.length,
                      itemBuilder: (context, index) {
                        final dateInfo = dates[index];
                        return DayTile(
                          day: dateInfo.day,
                          date: dateInfo.date,
                          hasOutfit: dateInfo.hasOutfit,
                          isSelected: selectedDate == dateInfo.date,
                          onTap: () => selectDate(dateInfo.date),
                        );
                      },
                    ),
                  ],
                ),
              ),

              Text(
                "This Month's Outfits",
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                  color: PlannerColors.textPrimary,
                ),
              ),
              const SizedBox(height: 16),

              if (monthOutfits.isNotEmpty) ...[
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 0.72,
                  ),
                  itemCount: monthOutfits.length,
                  itemBuilder: (context, index) {
                    final outfit = monthOutfits[index];
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        // Outfit Image
                        Builder(
                          builder: (context) {
                            debugPrint(
                              'Loading image: ${outfit.firstItem.imagePath}',
                            );
                            return Container(
                              width: double.infinity,
                              height: 100,
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(16),
                                color: Colors.grey[200],
                                boxShadow: const [
                                  BoxShadow(
                                    color: Color(0x1F000000),
                                    offset: Offset(0, 4),
                                    blurRadius: 12,
                                  ),
                                ],
                              ),
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(16),
                                child:
                                    outfit.firstItem.imagePath.startsWith(
                                      'assets/',
                                    )
                                    ? Image.asset(
                                        outfit.firstItem.imagePath,
                                        fit: BoxFit.cover,
                                        errorBuilder: (context, error, stackTrace) {
                                          debugPrint(
                                            'Asset image error: $error for path: ${outfit.firstItem.imagePath}',
                                          );
                                          return const Center(
                                            child: Icon(
                                              Icons.image_not_supported,
                                              color: Colors.grey,
                                              size: 40,
                                            ),
                                          );
                                        },
                                      )
                                    : kIsWeb
                                    ? Image.network(
                                        outfit.firstItem.imagePath,
                                        fit: BoxFit.cover,
                                        errorBuilder: (context, error, stackTrace) {
                                          debugPrint(
                                            'Network image error: $error for path: ${outfit.firstItem.imagePath}',
                                          );
                                          return const Center(
                                            child: Icon(
                                              Icons.image_not_supported,
                                              color: Colors.grey,
                                              size: 40,
                                            ),
                                          );
                                        },
                                      )
                                    : Image.file(
                                        File(outfit.firstItem.imagePath),
                                        fit: BoxFit.cover,
                                        errorBuilder: (context, error, stackTrace) {
                                          debugPrint(
                                            'File image error: $error for path: ${outfit.firstItem.imagePath}',
                                          );
                                          return const Center(
                                            child: Icon(
                                              Icons.image_not_supported,
                                              color: Colors.grey,
                                              size: 40,
                                            ),
                                          );
                                        },
                                      ),
                              ),
                            );
                          },
                        ),
                        const SizedBox(height: 8),
                        Text(
                          outfit.name,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: PlannerColors.textPrimary,
                          ),
                          textAlign: TextAlign.center,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          outfit.dateLabel,
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w400,
                            color: PlannerColors.textSecondary,
                          ),
                          textAlign: TextAlign.center,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    );
                  },
                ),
              ],

              if (noOutfitPlanned) ...[
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(32),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        PlannerColors.cardBackground,
                        PlannerColors.lightBeige,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: PlannerColors.textSecondary.withOpacity(0.12),
                        offset: const Offset(0, 4),
                        blurRadius: 20,
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Container(
                        width: 64,
                        height: 64,
                        decoration: BoxDecoration(
                          color: PlannerColors.lightBeige,
                          shape: BoxShape.circle,
                        ),
                        child: const Center(
                          child: Text('📅', style: TextStyle(fontSize: 30)),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'No outfit planned',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: PlannerColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Create a stunning look for this day',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 14,
                          color: PlannerColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton.icon(
                        onPressed: () => _planNewOutfit(appData),
                        icon: const Icon(Icons.add, size: 16),
                        label: const Text('Plan an Outfit'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: PlannerColors.primaryTaupe,
                          foregroundColor: Colors.white,
                          elevation: 0,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 12,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(20),
                          ),
                          textStyle: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
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

class DayTile extends StatelessWidget {
  final String day;
  final int date;
  final bool hasOutfit;
  final bool isSelected;
  final VoidCallback onTap;

  const DayTile({
    super.key,
    required this.day,
    required this.date,
    required this.hasOutfit,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (date == 0) {
      return const SizedBox.shrink(); // Empty cell
    }

    final bool isPlannedOnly = hasOutfit && !isSelected;
    final bool isEmpty = !hasOutfit && !isSelected;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          gradient: isSelected ? PlannerColors.primaryGradient : null,
          color: isSelected
              ? null
              : isPlannedOnly
              ? PlannerColors.lightBeige
              : PlannerColors.pageBackground,
          borderRadius: BorderRadius.circular(8),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: PlannerColors.primaryTaupe.withOpacity(0.3),
                    offset: const Offset(0, 4),
                    blurRadius: 16,
                  ),
                ]
              : null,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              day,
              style: TextStyle(
                fontSize: 10,
                color: isSelected
                    ? Colors.white
                    : PlannerColors.textSecondary.withOpacity(0.6),
              ),
            ),
            const SizedBox(height: 2),
            Text(
              '$date',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: isSelected ? Colors.white : PlannerColors.textPrimary,
              ),
            ),
            const SizedBox(height: 4),
            if (hasOutfit)
              Container(
                width: 4,
                height: 4,
                decoration: BoxDecoration(
                  color: isSelected ? Colors.white : PlannerColors.primaryTaupe,
                  shape: BoxShape.circle,
                ),
              )
            else if (isEmpty)
              const SizedBox(height: 4),
          ],
        ),
      ),
    );
  }
}

class _MonthArrowButton extends StatefulWidget {
  final IconData icon;
  final VoidCallback onTap;

  const _MonthArrowButton({required this.icon, required this.onTap});

  @override
  State<_MonthArrowButton> createState() => _MonthArrowButtonState();
}

class _MonthArrowButtonState extends State<_MonthArrowButton> {
  bool isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => isHovered = true),
      onExit: (_) => setState(() => isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: isHovered ? PlannerColors.lightBeige : Colors.transparent,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Icon(widget.icon, size: 20, color: PlannerColors.textPrimary),
        ),
      ),
    );
  }
}

class DateInfo {
  final String day;
  final int date;
  final bool hasOutfit;

  DateInfo({required this.day, required this.date, required this.hasOutfit});
}

class PlannerColors {
  static const pageBackground = Color(0xFFFAF8F6);
  static const cardBackground = Color(0xFFFFFFFF);
  static const lightBeige = Color(0xFFF5F0EB);
  static const secondaryBeige = Color(0xFFE8DDD3);

  static const primaryTaupe = Color(0xFFB8957A);
  static const secondarySand = Color(0xFFD4B5A0);

  static const textPrimary = Color(0xFF2D2620);
  static const textSecondary = Color(0xFF8B7E74);

  static const primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryTaupe, secondarySand],
  );

  static const emptyStateGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFFFFFFF), lightBeige],
  );
}
