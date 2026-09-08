import 'package:flutter/material.dart';

class AppTheme {
  // --- Dark Mode Palette ---
  static const Color darkBg = Color(0xFF080D1A);
  static const Color darkSurface = Color(0xFF0F172A);
  static const Color darkCard = Color(0xFF131D31);
  static const Color darkCardHover = Color(0xFF1E293B);
  static const Color darkBorder = Color(0xFF1E293B);
  static const Color darkBorderLight = Color(0xFF334155);

  // --- Light Mode Palette ---
  static const Color lightBg = Color(0xFFF8FAFC);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightCard = Color(0xFFFFFFFF);
  static const Color lightCardHover = Color(0xFFF1F5F9);
  static const Color lightBorder = Color(0xFFE2E8F0);
  static const Color lightBorderLight = Color(0xFFCBD5E1);

  // --- Semantic Brand Accents ---
  static const Color primaryBlue = Color(0xFF0EA5E9);
  static const Color primaryBlueLight = Color(0xFF38BDF8);
  static const Color emeraldGreen = Color(0xFF10B981);
  static const Color mintGreen = Color(0xFF34D399);
  static const Color roseRed = Color(0xFFF43F5E);
  static const Color lightRed = Color(0xFFE11D48);
  static const Color amberGold = Color(0xFFF59E0B);
  static const Color purpleViolet = Color(0xFF8B5CF6);

  // --- High-Visibility Institutional Trading Accents ---
  static const Color neonGreen = Color(0xFF00E676);
  static const Color neonRed = Color(0xFFFF334B);
  static const Color electricCyan = Color(0xFF00B0FF);
  static const Color obsidianCard = Color(0xFF11192E);
  static const Color obsidianSurface = Color(0xFF0D1322);

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: darkBg,
    canvasColor: darkSurface,
    cardColor: darkCard,
    primaryColor: primaryBlueLight,
    colorScheme: const ColorScheme.dark(
      primary: primaryBlueLight,
      secondary: emeraldGreen,
      surface: darkSurface,
      error: roseRed,
      onPrimary: Colors.black,
      onSecondary: Colors.white,
      onSurface: Color(0xFFF8FAFC),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: darkSurface,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        color: Color(0xFFF8FAFC),
        fontSize: 16,
        fontWeight: FontWeight.w800,
        letterSpacing: -0.3,
      ),
      iconTheme: IconThemeData(color: Color(0xFF94A3B8)),
    ),
    cardTheme: CardThemeData(
      color: darkCard,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: darkBorder, width: 1),
      ),
    ),
    dividerTheme: const DividerThemeData(
      color: darkBorder,
      thickness: 1,
      space: 1,
    ),
    tabBarTheme: const TabBarThemeData(
      indicatorColor: primaryBlueLight,
      indicatorSize: TabBarIndicatorSize.tab,
      labelColor: primaryBlueLight,
      unselectedLabelColor: Color(0xFF94A3B8),
      labelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
      unselectedLabelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
      dividerColor: darkBorder,
    ),
    navigationRailTheme: const NavigationRailThemeData(
      backgroundColor: darkSurface,
      elevation: 0,
      indicatorColor: Color(0x220EA5E9),
      selectedIconTheme: IconThemeData(color: primaryBlueLight, size: 22),
      unselectedIconTheme: IconThemeData(color: Color(0xFF64748B), size: 20),
      selectedLabelTextStyle: TextStyle(color: primaryBlueLight, fontWeight: FontWeight.w800, fontSize: 11),
      unselectedLabelTextStyle: TextStyle(color: Color(0xFF64748B), fontWeight: FontWeight.w600, fontSize: 11),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: darkSurface,
      elevation: 0,
      indicatorColor: const Color(0x220EA5E9),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const IconThemeData(color: primaryBlueLight);
        }
        return const IconThemeData(color: Color(0xFF64748B));
      }),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(color: primaryBlueLight, fontWeight: FontWeight.w800, fontSize: 11);
        }
        return const TextStyle(color: Color(0xFF64748B), fontWeight: FontWeight.w600, fontSize: 11);
      }),
    ),
    textTheme: const TextTheme(
      titleLarge: TextStyle(fontWeight: FontWeight.w800, color: Color(0xFFF8FAFC)),
      titleMedium: TextStyle(fontWeight: FontWeight.w700, color: Color(0xFFF8FAFC)),
      bodyLarge: TextStyle(color: Color(0xFFF8FAFC)),
      bodyMedium: TextStyle(color: Color(0xFF94A3B8)),
      bodySmall: TextStyle(color: Color(0xFF64748B)),
    ),
  );

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    scaffoldBackgroundColor: lightBg,
    canvasColor: lightSurface,
    cardColor: lightCard,
    primaryColor: primaryBlue,
    colorScheme: const ColorScheme.light(
      primary: primaryBlue,
      secondary: emeraldGreen,
      surface: lightSurface,
      error: lightRed,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: Color(0xFF0F172A),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: lightSurface,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        color: Color(0xFF0F172A),
        fontSize: 16,
        fontWeight: FontWeight.w800,
        letterSpacing: -0.3,
      ),
      iconTheme: IconThemeData(color: Color(0xFF64748B)),
    ),
    cardTheme: CardThemeData(
      color: lightCard,
      elevation: 0.5,
      shadowColor: Colors.black.withAlpha(12),
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: lightBorder, width: 1),
      ),
    ),
    dividerTheme: const DividerThemeData(
      color: lightBorder,
      thickness: 1,
      space: 1,
    ),
    tabBarTheme: const TabBarThemeData(
      indicatorColor: primaryBlue,
      indicatorSize: TabBarIndicatorSize.tab,
      labelColor: primaryBlue,
      unselectedLabelColor: Color(0xFF64748B),
      labelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
      unselectedLabelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
      dividerColor: lightBorder,
    ),
    navigationRailTheme: const NavigationRailThemeData(
      backgroundColor: lightSurface,
      elevation: 0,
      indicatorColor: Color(0x180EA5E9),
      selectedIconTheme: IconThemeData(color: primaryBlue, size: 22),
      unselectedIconTheme: IconThemeData(color: Color(0xFF94A3B8), size: 20),
      selectedLabelTextStyle: TextStyle(color: primaryBlue, fontWeight: FontWeight.w800, fontSize: 11),
      unselectedLabelTextStyle: TextStyle(color: Color(0xFF94A3B8), fontWeight: FontWeight.w600, fontSize: 11),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: lightSurface,
      elevation: 2,
      shadowColor: Colors.black.withAlpha(20),
      indicatorColor: const Color(0x180EA5E9),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const IconThemeData(color: primaryBlue);
        }
        return const IconThemeData(color: Color(0xFF94A3B8));
      }),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(color: primaryBlue, fontWeight: FontWeight.w800, fontSize: 11);
        }
        return const TextStyle(color: Color(0xFF94A3B8), fontWeight: FontWeight.w600, fontSize: 11);
      }),
    ),
    textTheme: const TextTheme(
      titleLarge: TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
      titleMedium: TextStyle(fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
      bodyLarge: TextStyle(color: Color(0xFF0F172A)),
      bodyMedium: TextStyle(color: Color(0xFF475569)),
      bodySmall: TextStyle(color: Color(0xFF94A3B8)),
    ),
  );
}

class AppColors {
  static bool isDark(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark;

  static Color bg(BuildContext context) =>
      isDark(context) ? AppTheme.darkBg : AppTheme.lightBg;

  static Color surface(BuildContext context) =>
      isDark(context) ? AppTheme.darkSurface : AppTheme.lightSurface;

  static Color card(BuildContext context) =>
      isDark(context) ? AppTheme.darkCard : AppTheme.lightCard;

  static Color cardHover(BuildContext context) =>
      isDark(context) ? AppTheme.darkCardHover : AppTheme.lightCardHover;

  static Color border(BuildContext context) =>
      isDark(context) ? AppTheme.darkBorder : AppTheme.lightBorder;

  static Color borderLight(BuildContext context) =>
      isDark(context) ? AppTheme.darkBorderLight : AppTheme.lightBorderLight;

  static Color textPrimary(BuildContext context) =>
      isDark(context) ? const Color(0xFFF8FAFC) : const Color(0xFF0F172A);

  static Color textSecondary(BuildContext context) =>
      isDark(context) ? const Color(0xFF94A3B8) : const Color(0xFF475569);

  static Color textMuted(BuildContext context) =>
      isDark(context) ? const Color(0xFF64748B) : const Color(0xFF94A3B8);

  static Color green(BuildContext context) =>
      isDark(context) ? AppTheme.mintGreen : AppTheme.emeraldGreen;

  static Color red(BuildContext context) =>
      isDark(context) ? AppTheme.roseRed : AppTheme.lightRed;

  static Color blue(BuildContext context) =>
      isDark(context) ? AppTheme.primaryBlueLight : AppTheme.primaryBlue;

  static Color gold(BuildContext context) => AppTheme.amberGold;

  static Color purple(BuildContext context) => AppTheme.purpleViolet;

  static Color neonGreen(BuildContext context) =>
      isDark(context) ? AppTheme.neonGreen : AppTheme.emeraldGreen;

  static Color neonRed(BuildContext context) =>
      isDark(context) ? AppTheme.neonRed : AppTheme.roseRed;

  static Color glassBorder(BuildContext context) =>
      isDark(context) ? const Color(0x2238BDF8) : const Color(0x180284C7);

  static List<BoxShadow> glowShadow(Color color, {double blur = 10.0}) => [
    BoxShadow(
      color: color.withAlpha(50),
      blurRadius: blur,
      spreadRadius: 1,
    ),
  ];

  static BoxDecoration cardDecoration(BuildContext context, {bool isSelected = false, double borderRadius = 12.0}) {
    final dark = isDark(context);
    return BoxDecoration(
      color: isSelected
          ? blue(context).withAlpha(dark ? 28 : 20)
          : card(context),
      borderRadius: BorderRadius.circular(borderRadius),
      border: Border.all(
        color: isSelected
            ? blue(context).withAlpha(180)
            : border(context),
        width: isSelected ? 1.4 : 1.0,
      ),
      boxShadow: [
        softShadow(context),
        if (isSelected)
          BoxShadow(
            color: blue(context).withAlpha(35),
            blurRadius: 10,
            spreadRadius: 1,
          ),
      ],
    );
  }

  static BoxShadow softShadow(BuildContext context) {
    if (isDark(context)) {
      return BoxShadow(
        color: Colors.black.withAlpha(40),
        blurRadius: 8,
        offset: const Offset(0, 3),
      );
    }
    return BoxShadow(
      color: Colors.black.withAlpha(10),
      blurRadius: 10,
      offset: const Offset(0, 2),
    );
  }
}
