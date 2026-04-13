import 'package:flutter/material.dart';
import 'pages/wardrobe_page.dart';
import 'pages/planner_page.dart';
import 'pages/global_page.dart';
import 'pages/tools_page.dart';
import 'pages/profile_page.dart';
import 'widgets/bottom_nav_bar.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int selectedIndex = 0;

  final List<Widget> pages = [
    const WardrobePage(),
    const PlannerPage(),
    const GlobalPage(),
    const ToolsPage(),
    const ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: selectedIndex, children: pages),
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: selectedIndex,
        onTap: (index) {
          setState(() {
            selectedIndex = index;
          });
        },
      ),
    );
  }
}
